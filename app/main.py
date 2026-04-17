from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.endpoints import auth_mobile, auth_web, conductores, perfil, vehiculos, solicitudes, emergencias, taller_operaciones, tecnicos
from app.api.websockets import notificaciones

app = FastAPI(title=settings.PROJECT_NAME)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_mobile.router, prefix="/api/v1")
app.include_router(auth_web.router, prefix="/api/v1")
app.include_router(conductores.router, prefix="/api/v1")
app.include_router(perfil.router, prefix="/api/v1")
app.include_router(vehiculos.router, prefix="/api/v1")
app.include_router(solicitudes.router, prefix="/api/v1")
app.include_router(emergencias.router, prefix="/api/v1/emergencias", tags=["Emergencias"])
app.include_router(taller_operaciones.router, prefix="/api/v1/talleres", tags=["Taller Operaciones"])
app.include_router(tecnicos.router, prefix="/api/v1/tecnicos", tags=["Operacion en Campo"])
app.include_router(notificaciones.router, prefix="/ws", tags=["WebSockets RealTime"])



@app.get("/")
async def root():
    return {"status": "Backend running", "project": settings.PROJECT_NAME}