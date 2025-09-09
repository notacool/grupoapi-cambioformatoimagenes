"""
Observer Pattern para Sistema de Eventos
=======================================

Este módulo implementa el patrón Observer para notificar
eventos del sistema a múltiples observadores.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable
from datetime import datetime
from enum import Enum
from ..output_manager import output_manager


class EventType(Enum):
    """Tipos de eventos del sistema."""
    CONVERSION_STARTED = "conversion_started"
    CONVERSION_COMPLETED = "conversion_completed"
    CONVERSION_FAILED = "conversion_failed"
    FILE_PROCESSED = "file_processed"
    POSTCONVERSION_STARTED = "postconversion_started"
    POSTCONVERSION_COMPLETED = "postconversion_completed"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_INFO = "system_info"


class Event:
    """
    Representa un evento del sistema.
    """
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime = None):
        """
        Inicializa un evento.
        
        Args:
            event_type: Tipo del evento
            data: Datos del evento
            timestamp: Timestamp del evento (por defecto: ahora)
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.event_type.value}: {self.data}"


class Observer(ABC):
    """
    Interfaz abstracta para observadores de eventos.
    """
    
    @abstractmethod
    def update(self, event: Event) -> None:
        """
        Actualiza el observador con un nuevo evento.
        
        Args:
            event: Evento a procesar
        """
        pass


class LoggingObserver(Observer):
    """
    Observador que registra eventos en logs.
    """
    
    def __init__(self, log_file: str = None):
        """
        Inicializa el observador de logging.
        
        Args:
            log_file: Archivo de log (opcional)
        """
        self.log_file = log_file
        self.events_logged = 0
    
    def update(self, event: Event) -> None:
        """Registra el evento en el log."""
        try:
            log_message = f"[{event.timestamp}] {event.event_type.value}: {event.data}"
            
            # Log en consola
            if event.event_type == EventType.ERROR_OCCURRED:
                output_manager.error(f"🚨 {log_message}")
            elif event.event_type == EventType.CONVERSION_COMPLETED:
                output_manager.success(f"✅ {log_message}")
            else:
                output_manager.info(f"ℹ️ {log_message}")
            
            # Log en archivo si está configurado
            if self.log_file:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{log_message}\n")
            
            self.events_logged += 1
            
        except Exception as e:
            output_manager.error(f"❌ Error en logging observer: {str(e)}")
    
    def get_events_count(self) -> int:
        """Retorna el número de eventos registrados."""
        return self.events_logged


class MetricsObserver(Observer):
    """
    Observador que recopila métricas del sistema.
    """
    
    def __init__(self):
        """Inicializa el observador de métricas."""
        self.metrics = {
            'conversions_started': 0,
            'conversions_completed': 0,
            'conversions_failed': 0,
            'files_processed': 0,
            'errors_occurred': 0,
            'total_processing_time': 0.0,
            'start_time': None,
            'end_time': None
        }
    
    def update(self, event: Event) -> None:
        """Actualiza las métricas basándose en el evento."""
        try:
            if event.event_type == EventType.CONVERSION_STARTED:
                self.metrics['conversions_started'] += 1
                if not self.metrics['start_time']:
                    self.metrics['start_time'] = event.timestamp
            
            elif event.event_type == EventType.CONVERSION_COMPLETED:
                self.metrics['conversions_completed'] += 1
                self.metrics['end_time'] = event.timestamp
                
                # Calcular tiempo de procesamiento
                if 'processing_time' in event.data:
                    self.metrics['total_processing_time'] += event.data['processing_time']
            
            elif event.event_type == EventType.CONVERSION_FAILED:
                self.metrics['conversions_failed'] += 1
            
            elif event.event_type == EventType.FILE_PROCESSED:
                self.metrics['files_processed'] += 1
            
            elif event.event_type == EventType.ERROR_OCCURRED:
                self.metrics['errors_occurred'] += 1
                
        except Exception as e:
            output_manager.error(f"❌ Error en metrics observer: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna las métricas recopiladas."""
        return self.metrics.copy()
    
    def get_success_rate(self) -> float:
        """Calcula la tasa de éxito."""
        total = self.metrics['conversions_started']
        if total == 0:
            return 0.0
        return (self.metrics['conversions_completed'] / total) * 100


class ProgressObserver(Observer):
    """
    Observador que muestra el progreso de las operaciones.
    """
    
    def __init__(self):
        """Inicializa el observador de progreso."""
        self.current_operation = None
        self.progress = 0
        self.total = 0
    
    def update(self, event: Event) -> None:
        """Actualiza el progreso basándose en el evento."""
        try:
            if event.event_type == EventType.CONVERSION_STARTED:
                self.current_operation = "Conversión"
                self.progress = 0
                if 'total_files' in event.data:
                    self.total = event.data['total_files']
            
            elif event.event_type == EventType.FILE_PROCESSED:
                self.progress += 1
                if self.total > 0:
                    percentage = (self.progress / self.total) * 100
                    output_manager.info(f"📊 Progreso: {self.progress}/{self.total} ({percentage:.1f}%)")
            
            elif event.event_type == EventType.CONVERSION_COMPLETED:
                output_manager.success(f"✅ {self.current_operation} completada: {self.progress} archivos")
                
        except Exception as e:
            output_manager.error(f"❌ Error en progress observer: {str(e)}")


class EventManager:
    """
    Gestor de eventos que implementa el patrón Observer.
    """
    
    def __init__(self):
        """Inicializa el gestor de eventos."""
        self.observers: List[Observer] = []
        self.event_history: List[Event] = []
        self.max_history = 1000  # Límite de eventos en historial
    
    def attach(self, observer: Observer) -> None:
        """
        Adjunta un observador.
        
        Args:
            observer: Observador a adjuntar
        """
        if observer not in self.observers:
            self.observers.append(observer)
            output_manager.info(f"✅ Observador adjuntado: {observer.__class__.__name__}")
    
    def detach(self, observer: Observer) -> None:
        """
        Desadjunta un observador.
        
        Args:
            observer: Observador a desadjuntar
        """
        if observer in self.observers:
            self.observers.remove(observer)
            output_manager.info(f"✅ Observador desadjuntado: {observer.__class__.__name__}")
    
    def notify(self, event: Event) -> None:
        """
        Notifica un evento a todos los observadores.
        
        Args:
            event: Evento a notificar
        """
        # Agregar al historial
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notificar a observadores
        for observer in self.observers:
            try:
                observer.update(event)
            except Exception as e:
                output_manager.error(f"❌ Error notificando a observador: {str(e)}")
    
    def emit(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Emite un evento.
        
        Args:
            event_type: Tipo del evento
            data: Datos del evento
        """
        event = Event(event_type, data)
        self.notify(event)
    
    def get_event_history(self) -> List[Event]:
        """Retorna el historial de eventos."""
        return self.event_history.copy()
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos."""
        self.event_history.clear()
        output_manager.info("🧹 Historial de eventos limpiado")


# Instancia global del gestor de eventos
event_manager = EventManager()
