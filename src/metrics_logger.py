import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
from config import METRICS_FILE_PATH, ENABLE_METRICS, METRICS_RETENTION_DAYS

logger = logging.getLogger(__name__)


class MetricsLogger:
    """Sistema de logging y métricas para el agente conversacional"""
    
    def __init__(self):
        self.session_metrics = []
        self.error_counts = defaultdict(int)
        self.session_start = time.time()
        
        if ENABLE_METRICS:
            self.ensure_metrics_file()
            self.cleanup_old_metrics()
    
    def ensure_metrics_file(self):
        """Asegurar que el archivo de métricas existe"""
        try:
            os.makedirs(os.path.dirname(METRICS_FILE_PATH), exist_ok=True)
            if not os.path.exists(METRICS_FILE_PATH):
                with open(METRICS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump({"sessions": [], "errors": []}, f)
        except Exception as e:
            logger.error(f"Error creando archivo de métricas: {e}")
    
    def log_interaction(self, metrics: Dict):
        """Registrar métricas de una interacción"""
        if not ENABLE_METRICS:
            return
        
        try:
            # Agregar a métricas de sesión
            self.session_metrics.append(metrics)
            
            # Guardar en archivo persistente
            self._save_metrics_to_file(metrics)
            
            logger.debug(f"Métricas registradas: {metrics['total_tokens']} tokens, {metrics['response_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")
    
    def log_error(self, error_type: str, error_message: str):
        """Registrar un error"""
        if not ENABLE_METRICS:
            return
        
        try:
            self.error_counts[error_type] += 1
            
            error_record = {
                "timestamp": time.time(),
                "type": error_type,
                "message": error_message,
                "session_id": self.session_start
            }
            
            # Guardar error en archivo
            self._save_error_to_file(error_record)
            
            logger.warning(f"Error registrado: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"Error registrando error: {e}")
    
    def _save_metrics_to_file(self, metrics: Dict):
        """Guardar métricas en archivo persistente"""
        try:
            # Cargar métricas existentes
            data = {"sessions": [], "errors": []}
            if os.path.exists(METRICS_FILE_PATH):
                with open(METRICS_FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Agregar sesión si es nueva
            session_id = str(self.session_start)
            session_found = False
            
            for session in data["sessions"]:
                if session["session_id"] == session_id:
                    session["interactions"].append(metrics)
                    session["last_interaction"] = time.time()
                    session_found = True
                    break
            
            if not session_found:
                new_session = {
                    "session_id": session_id,
                    "start_time": self.session_start,
                    "last_interaction": time.time(),
                    "interactions": [metrics]
                }
                data["sessions"].append(new_session)
            
            # Guardar archivo actualizado
            with open(METRICS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando métricas en archivo: {e}")
    
    def _save_error_to_file(self, error_record: Dict):
        """Guardar error en archivo persistente"""
        try:
            data = {"sessions": [], "errors": []}
            if os.path.exists(METRICS_FILE_PATH):
                with open(METRICS_FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            data["errors"].append(error_record)
            
            with open(METRICS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando error en archivo: {e}")
    
    def get_session_stats(self) -> Dict:
        """Obtener estadísticas de la sesión actual"""
        if not self.session_metrics:
            return {"session_duration": time.time() - self.session_start, "interactions": 0}
        
        total_tokens = sum(m['total_tokens'] for m in self.session_metrics)
        total_time = sum(m['response_time'] for m in self.session_metrics)
        avg_response_time = total_time / len(self.session_metrics)
        avg_tokens_per_interaction = total_tokens / len(self.session_metrics)
        
        return {
            "session_duration": time.time() - self.session_start,
            "interactions": len(self.session_metrics),
            "total_tokens": total_tokens,
            "average_response_time": avg_response_time,
            "average_tokens_per_interaction": avg_tokens_per_interaction,
            "errors": dict(self.error_counts),
            "streaming_usage": sum(1 for m in self.session_metrics if m.get('streaming_enabled', False))
        }
    
    def get_summary_stats(self) -> Dict:
        """Obtener estadísticas resumidas de todas las sesiones"""
        if not ENABLE_METRICS or not os.path.exists(METRICS_FILE_PATH):
            return self.get_session_stats()
        
        try:
            with open(METRICS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            all_interactions = []
            total_sessions = len(data.get("sessions", []))
            
            for session in data.get("sessions", []):
                all_interactions.extend(session.get("interactions", []))
            
            if not all_interactions:
                return self.get_session_stats()
            
            total_tokens = sum(i['total_tokens'] for i in all_interactions)
            total_time = sum(i['response_time'] for i in all_interactions)
            
            # Estadísticas por período (últimos 7 días)
            week_ago = time.time() - (7 * 24 * 3600)
            recent_interactions = [i for i in all_interactions if i['timestamp'] > week_ago]
            
            stats = {
                "total_sessions": total_sessions,
                "total_interactions": len(all_interactions),
                "total_tokens_used": total_tokens,
                "average_response_time": total_time / len(all_interactions),
                "average_tokens_per_interaction": total_tokens / len(all_interactions),
                "recent_interactions_7d": len(recent_interactions),
                "total_errors": len(data.get("errors", [])),
                "current_session": self.get_session_stats()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas resumidas: {e}")
            return self.get_session_stats()
    
    def cleanup_old_metrics(self):
        """Limpiar métricas antiguas según configuración de retención"""
        if not ENABLE_METRICS or not os.path.exists(METRICS_FILE_PATH):
            return
        
        try:
            with open(METRICS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cutoff_time = time.time() - (METRICS_RETENTION_DAYS * 24 * 3600)
            
            # Filtrar sesiones antiguas
            data["sessions"] = [
                session for session in data.get("sessions", [])
                if session.get("start_time", 0) > cutoff_time
            ]
            
            # Filtrar errores antiguos
            data["errors"] = [
                error for error in data.get("errors", [])
                if error.get("timestamp", 0) > cutoff_time
            ]
            
            # Guardar datos filtrados
            with open(METRICS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Limpieza de métricas completada - Reteniendo {METRICS_RETENTION_DAYS} días")
            
        except Exception as e:
            logger.error(f"Error en limpieza de métricas: {e}")
    
    def export_metrics(self, days: int = 7) -> Dict:
        """Exportar métricas de los últimos N días"""
        if not ENABLE_METRICS or not os.path.exists(METRICS_FILE_PATH):
            return {}
        
        try:
            with open(METRICS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cutoff_time = time.time() - (days * 24 * 3600)
            
            # Filtrar datos recientes
            recent_sessions = [
                session for session in data.get("sessions", [])
                if session.get("start_time", 0) > cutoff_time
            ]
            
            recent_errors = [
                error for error in data.get("errors", [])
                if error.get("timestamp", 0) > cutoff_time
            ]
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "period_days": days,
                "sessions": recent_sessions,
                "errors": recent_errors,
                "summary": self._calculate_export_summary(recent_sessions, recent_errors)
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exportando métricas: {e}")
            return {}
    
    def _calculate_export_summary(self, sessions: List[Dict], errors: List[Dict]) -> Dict:
        """Calcular resumen para exportación"""
        all_interactions = []
        for session in sessions:
            all_interactions.extend(session.get("interactions", []))
        
        if not all_interactions:
            return {"total_interactions": 0, "total_sessions": len(sessions)}
        
        return {
            "total_sessions": len(sessions),
            "total_interactions": len(all_interactions),
            "total_tokens": sum(i['total_tokens'] for i in all_interactions),
            "average_response_time": sum(i['response_time'] for i in all_interactions) / len(all_interactions),
            "total_errors": len(errors),
            "error_rate": len(errors) / len(all_interactions) if all_interactions else 0,
            "streaming_usage_rate": sum(1 for i in all_interactions if i.get('streaming_enabled', False)) / len(all_interactions)
        }