class PrestamoService:
    def __init__(self):
        # Importamos el repositorio que conecta con Supabase
        from app.repositories.prestamo_repository import PrestamoRepository
        self.repository = PrestamoRepository()

    def calcular_cuota(self, monto: float, plazo: int, tasa_anual: float) -> dict:
        # CORRECCIÓN CRÍTICA: Tasa Efectiva Mensual según normativa SBS
        # Fórmula: TEM = (1 + TEA/100)^(1/12) - 1
        tem = (1 + tasa_anual / 100) ** (1/12) - 1
        cuota = monto * tem / (1 - (1 + tem) ** -plazo)
        
        total = cuota * plazo
        itf = round(monto * 0.00005, 2) # ITF 0.005% según TUO Ley N° 28194

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
        # El Service recalcula la cuota antes de guardar
        # No confía en el valor que viene del frontend
        calculo = self.calcular_cuota(
            datos["monto"], datos["plazo_meses"], datos["tasa_anual"]
        )
        
        # Sobrescribe la cuota_mensual con el valor correcto calculado internamente
        datos["cuota_mensual"] = calculo["cuota_mensual"]
        return self.repository.insertar_solicitud(datos)