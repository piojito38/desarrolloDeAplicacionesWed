from fastapi import APIRouter, HTTPException
from app.models.schemas import PrestamoSimularRequest, PrestamoSolicitudRequest
from app.controllers.prestamo_controller import PrestamoController

router = APIRouter()
controller = PrestamoController()

@router.post(
    "/simular",
    summary="Simular cuota de préstamo",
    response_description="Cuota mensual y cronograma calculados con TEM"
)
async def simular_prestamo(datos: PrestamoSimularRequest):
    # El Router solo pasa los datos validados al Controller
    # Pydantic ya validó el formato antes de llegar aquí
    # Si Pydantic falla, retorna HTTP 422 automáticamente
    try:
        return await controller.simular(datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/solicitar",
    summary="Enviar solicitud de préstamo",
    response_description="Solicitud registrada con éxito en Supabase"
)
async def solicitar_prestamo(datos: PrestamoSolicitudRequest):
    """Caso Crítico 3 y 4: Recibe la solicitud para guardarla en BD"""
    try:
        # El Controller delegará al Service para recalcular y verificar duplicados
        return await controller.solicitar(datos)
    except Exception as e:
        # Error 500 en caso de fallos de conexión con Supabase
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/promedio-cuota/{user_id}",
    summary="Cuota promedio recalculada con TEM correcta",
    description="""
    Retorna el promedio de cuota mensual recalculado con TEM (Tasa Efectiva Mensual).
    IMPORTANTE: El campo cuota_registrada refleja el valor almacenado históricamente
    con la fórmula TEA/12 (incorrecta). El campo cuota_correcta es el valor real
    calculado con TEM según normativa SBS.
    El área de Riesgos debe usar cuota_correcta para reportes ejecutivos.
    """
)
async def promedio_cuota(user_id: str):
    return await controller.promedio_cuota(user_id)

@router.get(
    "/cuota-mas-alta/{user_id}",
    summary="Cuota más alta recalculada con TEM correcta"
)
async def cuota_mas_alta(user_id: str):
    return await controller.cuota_mas_alta(user_id)