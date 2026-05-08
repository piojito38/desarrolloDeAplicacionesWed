from app.services.prestamo_service import PrestamoService

class PrestamoController:
    def __init__(self):
        # Instanciamos el Service (Capa 3), donde está la fórmula correcta
        self.service = PrestamoService()

    async def simular(self, datos):
        """Coordina la simulación básica (Casos Críticos 1, 2 y 5)"""
        # El Controller delega los cálculos al Service
        resultado = self.service.calcular_cuota(
            monto=datos.monto,
            plazo=datos.plazo_meses,
            tasa_anual=datos.tasa_anual
        )
        return {"success": True, "data": resultado}

    async def solicitar(self, datos):
        """Caso Crítico 3 y 4: Calcula y guarda la solicitud en Supabase"""
        # Llamamos al Service para que valide duplicados y guarde
        # Usamos model_dump() para convertir el esquema Pydantic a un diccionario
        solicitud = await self.service.guardar_solicitud(datos.model_dump())
        return {"success": True, "data": solicitud}

    async def promedio_cuota(self, user_id: str):
        """Endpoint para Riesgos: Promedio recalculado (Caso Crítico 6)"""
        data = self.service.calcular_promedio_cuota(user_id)
        
        return {
            "success": True,
            "data": data,
            "nota_integridad": (
                "Los valores cuota_registrada fueron calculados con fórmula TEA/12 "
                "durante el período 01/2024-08/2024. Usar cuota_correcta para reportes "
                "y decisiones de cartera."
            )
        }

    async def cuota_mas_alta(self, user_id: str):
        """Endpoint para Riesgos: Cuota máxima recalculada (Caso Crítico 6)"""
        data = self.service.obtener_cuota_mas_alta(user_id)
        
        if not data:
            return {"success": False, "message": "Sin solicitudes registradas"}
            
        return {
            "success": True,
            "data": data,
            "nota_integridad": (
                "cuota_registrada corresponde al período con fórmula incorrecta. "
                "Usar cuota_correcta para evaluación de capacidad de pago."
            )
        }