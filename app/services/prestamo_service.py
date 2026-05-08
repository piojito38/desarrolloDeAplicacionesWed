class PrestamoService:
    def __init__(self):
        # Importamos el repositorio que conecta con Supabase
        from app.repositories.prestamo_repository import PrestamoRepository
        self.repository = PrestamoRepository()

    def calcular_cuota(self, monto: float, plazo: int, tasa_anual: float) -> dict:
        # CORRECCIÓN CRÍTICA 1: Tasa Efectiva Mensual según normativa SBS
        tem = (1 + tasa_anual / 100) ** (1/12) - 1
        cuota = monto * tem / (1 - (1 + tem) ** -plazo)
        
        total = cuota * plazo
        # CORRECCIÓN CRÍTICA 2: Inclusión del ITF
        itf = round(monto * 0.00005, 2) 

        return {
            "monto": round(monto, 2),
            "tem_pct": round(tem * 100, 4),
            "cuota_mensual": round(cuota, 2),
            "total_pagar": round(total, 2),
            "total_intereses": round(total - monto, 2),
            "itf": itf,
            "importe_a_recibir": round(monto - itf, 2),
            "plazo_meses": plazo,
            "tasa_anual": tasa_anual
        }

    async def guardar_solicitud(self, datos: dict) -> dict:
        # CORRECCIÓN CRÍTICA 4: Prevenir duplicados (doble clic)
        duplicado = self.repository.buscar_solicitud_reciente(
            user_id=datos["user_id"],
            monto=datos["monto"],
            plazo_meses=datos["plazo_meses"],
            segundos=30
        )
        if duplicado:
            return duplicado

        # CORRECCIÓN CRÍTICA 3: Recalcular internamente
        calculo = self.calcular_cuota(
            datos["monto"], datos["plazo_meses"], datos["tasa_anual"]
        )
        datos["cuota_mensual"] = calculo["cuota_mensual"]
        return self.repository.insertar_solicitud(datos)

    def calcular_promedio_cuota(self, user_id: str) -> dict:
        # CORRECCIÓN CRÍTICA 6: Recálculo de promedio de cartera
        solicitudes = self.repository.obtener_datos_para_recalculo(user_id)
        if not solicitudes:
            return {"promedio_cuota_correcto": 0, "cantidad": 0}
        
        cuotas_registradas = []
        cuotas_correctas = []
        
        for s in solicitudes:
            cuotas_registradas.append(s["cuota_mensual"])
            tem = (1 + s["tasa_anual"] / 100) ** (1/12) - 1
            cuota = s["monto"] * tem / (1 - (1 + tem) ** -s["plazo_meses"])
            cuotas_correctas.append(round(cuota, 2))
            
        prom_registrado = sum(cuotas_registradas) / len(cuotas_registradas)
        prom_correcto = sum(cuotas_correctas) / len(cuotas_correctas)
        
        return {
            "promedio_cuota_registrado": round(prom_registrado, 2),
            "promedio_cuota_correcto": round(prom_correcto, 2),
            "diferencia": round(prom_registrado - prom_correcto, 2),
            "pct_sobreestimacion": round((prom_registrado / prom_correcto - 1) * 100, 2),
            "cantidad_solicitudes": len(solicitudes),
            "advertencia": "cuota_registrada calculada con fórmula TEA/12 incorrecta"
        }

    def obtener_cuota_mas_alta(self, user_id: str) -> dict:
        # CORRECCIÓN CRÍTICA 6: Recálculo de cuota máxima de cartera
        solicitud = self.repository.obtener_datos_para_recalculo_uno(user_id)
        if not solicitud:
            return None
            
        tem = (1 + solicitud["tasa_anual"] / 100) ** (1/12) - 1
        cuota_correcta = solicitud["monto"] * tem / (
            1 - (1 + tem) ** -solicitud["plazo_meses"]
        )
        
        return {
            "id": solicitud["id"],
            "monto": solicitud["monto"],
            "plazo_meses": solicitud["plazo_meses"],
            "tasa_anual": solicitud["tasa_anual"],
            "cuota_registrada": solicitud["cuota_mensual"],
            "cuota_correcta": round(cuota_correcta, 2),
            "diferencia": round(solicitud["cuota_mensual"] - cuota_correcta, 2),
            "advertencia": "cuota_registrada calculada con fórmula TEA/12 incorrecta"
        }