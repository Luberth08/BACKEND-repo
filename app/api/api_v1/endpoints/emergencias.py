import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.api.api_v1 import deps
from app.models.usuario import Usuario
from app.models.solicitud_diagnostico import SolicitudDiagnostico, EstadoSolicitudDiagnostico
from app.models.vehiculo import Vehiculo
from app.models.evidencia import Evidencia, TipoEvidencia
from app.models.solicitud_servicio import SolicitudServicio, EstadoSolicitudServicio
from app.services.ai_service import transcribe_audio, generar_diagnostico_ia
from app.services.asignacion_service import buscar_taller_adecuado
from app.schemas.emergencia import SolicitudDiagnosticoResponse

router = APIRouter()

UPLOAD_DIR = "uploads/emergencias"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/reportar", response_model=SolicitudDiagnosticoResponse, status_code=status.HTTP_201_CREATED)
async def reportar_emergencia(
    latitud: float = Form(...),
    longitud: float = Form(...),
    id_vehiculo: int = Form(...),
    descripcion: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    imagen: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_usuario)
):
    """
    Recibe el reporte multimedia del conductor. 
    Llama a IA para procesar audio y clasificar,
    y conecta con el algoritmo de PostGIS para ofertar el servicio.
    """
    # 1. Validar vehiculo
    query_vehiculo = select(Vehiculo).filter(Vehiculo.id == id_vehiculo, Vehiculo.id_persona == current_user.id_persona)
    result = await db.execute(query_vehiculo)
    vehiculo = result.scalars().first()
    
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o no pertenece al usuario.")

    # 2. Guardar solicitud inicial
    ubicacion_wkt = f'POINT({longitud} {latitud})'
    solicitud = SolicitudDiagnostico(
        descripcion=descripcion,
        ubicacion=func.ST_GeographyFromText(ubicacion_wkt),
        id_vehiculo=vehiculo.id,
        estado=EstadoSolicitudDiagnostico.procesando
    )
    db.add(solicitud)
    await db.flush() # Para obtener ID
    
    texto_combinado = descripcion or ""
    imagen_url_procesada = None

    # Procesar Audio
    if audio:
        audio_path = f"{UPLOAD_DIR}/audio_{solicitud.id}_{audio.filename}"
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        texto_transcrito = await transcribe_audio(audio_path)
        texto_combinado += f" [Audio transcrito: {texto_transcrito}]"
        
        evidencia_audio = Evidencia(
            url=audio_path,
            transcripcion=texto_transcrito,
            tipo=TipoEvidencia.audio,
            id_solicitud=solicitud.id
        )
        db.add(evidencia_audio)
    
    # Procesar Imagen
    if imagen:
        img_path = f"{UPLOAD_DIR}/img_{solicitud.id}_{imagen.filename}"
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        
        # Mocking
        imagen_url_procesada = "https://mock-image-server.com/" + imagen.filename 
        
        evidencia_img = Evidencia(
            url=img_path,
            tipo=TipoEvidencia.imagen,
            id_solicitud=solicitud.id
        )
        db.add(evidencia_img)

    # 3. Invocar la IA para el Diagnóstico
    resultado_ia = await generar_diagnostico_ia(texto_combinado, imagen_url_procesada)
    
    # 4. Motor de Asignación Cercana
    taller_asignado = await buscar_taller_adecuado(
        db, 
        lat=latitud, 
        lon=longitud, 
        requiere_remolque=resultado_ia.requiere_remolque
    )
    
    if taller_asignado:
        # Generar "Solicitud de Servicio" ofertada
        oferta = SolicitudServicio(
            ubicacion=func.ST_GeographyFromText(ubicacion_wkt),
            comentario=resultado_ia.resumen_problema,
            estado=EstadoSolicitudServicio.ofertada,
            costo_estimado=250.0, 
            id_taller=taller_asignado.id,
            id_solicitud_diagnostico=solicitud.id
        )
        db.add(oferta)
        solicitud.estado = EstadoSolicitudDiagnostico.completado
    else:
        solicitud.estado = EstadoSolicitudDiagnostico.fallido 

    await db.commit()
    await db.refresh(solicitud)
    
    # Mapeo explicito para evitar el MissingGreenlet de sqlalchemy AsyncIO al cargar relaciones perezosas
    response = SolicitudDiagnosticoResponse(
        id=solicitud.id,
        descripcion=solicitud.descripcion,
        id_vehiculo=solicitud.id_vehiculo,
        fecha=solicitud.fecha,
        estado=solicitud.estado,
        id_incidente=solicitud.id_incidente,
        incidente=None,
        diagnosticos=[],
        evidencias=[]
    )
    return response
