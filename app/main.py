from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.endpoints import auth_mobile, auth_web, conductores, perfil, vehiculos

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

@app.get("/")
async def root():
    return {"status": "Backend running", "project": settings.PROJECT_NAME}