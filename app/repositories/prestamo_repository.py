import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class PrestamoRepository:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        # --- LÍNEAS DE DIAGNÓSTICO ---
        print("--- DEBUGGING ENV VARIABLES ---")
        print("URL leída:", url)
        print("KEY leída:", "VACÍO/NONE" if not key else "LLAVE ENCONTRADA (empieza con " + key[:10] + "...)")
        print("-------------------------------")
        
        self.supabase: Client = create_client(url, key)

    def insertar_solicitud(self, datos: dict):
        """Inserta la solicitud calculada correctamente"""
        return self.supabase.table("solicitudes_prestamo").insert(datos).execute()

    def buscar_solicitud_reciente(self, user_id: str, monto: float, plazo_meses: int, segundos: int = 30):
        """Previene duplicados buscando registros idénticos recientes (Caso Crítico 4)"""
        from datetime import datetime, timedelta
        desde = (datetime.utcnow() - timedelta(seconds=segundos)).isoformat()
        
        response = self.supabase.table("solicitudes_prestamo") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("monto", monto) \
            .eq("plazo_meses", plazo_meses) \
            .gte("created_at", desde) \
            .order("created_at", desc=True) \
            .limit(1).execute()
        return response.data[0] if response.data else None

    def obtener_datos_para_recalculo(self, user_id: str) -> list:
        """
        Trae campos necesarios para recalcular la cuota con TEM (Caso Crítico 6).
        NO trae solo la cuota_mensual porque ese campo está contaminado en BD.
        """
        response = self.supabase.table("solicitudes_prestamo") \
            .select("id, monto, plazo_meses, tasa_anual, cuota_mensual, estado") \
            .eq("user_id", user_id) \
            .execute()
        return response.data

    def obtener_datos_para_recalculo_uno(self, user_id: str) -> dict:
        """Trae la solicitud con mayor cuota registrada para recalcular (Caso Crítico 6)"""
        response = self.supabase.table("solicitudes_prestamo") \
            .select("id, monto, plazo_meses, tasa_anual, cuota_mensual") \
            .eq("user_id", user_id) \
            .order("cuota_mensual", desc=True) \
            .limit(1).execute()
        return response.data[0] if response.data else None