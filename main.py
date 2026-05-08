from fastapi import FastAPI
from app.routers.prestamo_router import router as prestamo_router

# Esta es la variable "app" que uvicorn no encontraba
app = FastAPI(
    title="Simulador de Créditos - Operación Simulador",
    description="Backend para la corrección de errores financieros y de integridad",
    version="2.0.0"
)

# Registro de la Capa 1: Routers
app.include_router(prestamo_router, prefix="/api/prestamos", tags=["Préstamos"])

@app.get("/")
async def root():
    return {"message": "Bienvenido al Sistema de Simulación - Backend Activo"}