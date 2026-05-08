from fastapi import APIRouter, HTTPException
from app.models.schemas import PrestamoSimularRequest
from app.controllers.prestamo_controller import PrestamoController

router = APIRouter()
controller = PrestamoController()

@router.post(
    "/simular",
    summary="Simular cuota de préstamo",
    response_description="Cuota mensual y cronograma calculados con TEM"
)
async def simular_prestamo(datos: PrestamoSimularRequest):
    # El Router solo pasa los datos validados al Controller [cite: 735]
    # Pydantic ya validó el formato antes de llegar aquí [cite: 736]
    # Si Pydantic falla, retorna HTTP 422 automáticamente [cite: 737]
    try:
        return await controller.simular(datos) [cite: 739]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) [cite: 743, 744]

@router.get(
    "/promedio-cuota/{user_id}",
    summary="Cuota promedio recalculada con TEM correcta",
    description="""
    Retorna el promedio de cuota mensual recalculado con TEM (Tasa Efectiva Mensual). [cite: 924, 925]
    IMPORTANTE: El campo cuota_registrada refleja el valor almacenado históricamente [cite: 926]
    con la fórmula TEA/12 (incorrecta). El campo cuota_correcta es el valor real [cite: 928]
    calculado con TEM según normativa SBS. [cite: 928]
    El área de Riesgos debe usar cuota_correcta para reportes ejecutivos. [cite: 929]
    """
)
async def promedio_cuota(user_id: str):
    return await controller.promedio_cuota(user_id) [cite: 931]

@router.get(
    "/cuota-mas-alta/{user_id}",
    summary="Cuota más alta recalculada con TEM correcta"
)
async def cuota_mas_alta(user_id: str):
    return await controller.cuota_mas_alta(user_id) [cite: 936]