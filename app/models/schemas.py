from pydantic import BaseModel, Field
from typing import Optional

class PrestamoSimularRequest(BaseModel):
    """Esquema de entrada para la simulación (Caso Crítico 5)"""
    monto: float = Field(
        ge=500, 
        le=300000, 
        description="Monto entre S/ 500 y S/ 300,000 según reglamento"
    )
    plazo_meses: int = Field(
        ge=6, 
        le=60, 
        description="Plazo entre 6 y 60 meses según tarifario"
    )
    tasa_anual: float = Field(
        ge=13.35, 
        le=114.13, 
        description="TEA según tarifario SBS vigente"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "monto": 10000.0,
                "plazo_meses": 12,
                "tasa_anual": 24.0
            }
        }

class PrestamoSimularResponse(BaseModel):
    """Esquema de salida con transparencia total (Caso Crítico 1 y 2)"""
    monto: float
    tem_pct: float
    cuota_mensual: float
    total_pagar: float
    total_intereses: float
    itf: float
    importe_a_recibir: float
    plazo_meses: int
    tasa_anual: float

class PrestamoSolicitudRequest(PrestamoSimularRequest):
    """Extiende la simulación agregando el ID de usuario para persistencia"""
    user_id: str