from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.endpoints import auth

app = FastAPI(title=settings.PROJECT_NAME)

# Configurar CORS (importante para que el frontend pueda consumir la API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringe a tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "Backend running", "project": settings.PROJECT_NAME}