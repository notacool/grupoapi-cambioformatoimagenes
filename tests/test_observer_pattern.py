#!/usr/bin/env python3
"""
Tests para Observer Pattern
==========================

Tests específicos para el patrón Observer implementado en el sistema.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.observers.event_system import (
    EventType, Event, Observer, LoggingObserver, 
    MetricsObserver, ProgressObserver, EventManager, event_manager
)


class MockObserver(Observer):
    """Observador mock para testing"""
    
    def __init__(self):
        self.events_received = []
        self.update_count = 0
    
    def update(self, event: Event) -> None:
        self.events_received.append(event)
        self.update_count += 1


class FailingObserver(Observer):
    """Observador que falla para testing"""
    
    def update(self, event: Event) -> None:
        raise Exception("Error simulado en observador")


def test_event_creation():
    """Test de creación de eventos"""
    print("🧪 Probando creación de eventos...")
    
    # Crear evento
    data = {"file": "test.tiff", "size": 1024}
    event = Event(EventType.CONVERSION_STARTED, data)
    
    # Verificar propiedades
    assert event.event_type == EventType.CONVERSION_STARTED
    assert event.data == data
    assert isinstance(event.timestamp, datetime)
    
    # Verificar string representation
    event_str = str(event)
    assert "conversion_started" in event_str.lower()
    assert "test.tiff" in event_str
    
    print("✅ Creación de eventos correcta")


def test_event_types():
    """Test de tipos de eventos"""
    print("🧪 Probando tipos de eventos...")
    
    # Verificar que todos los tipos están definidos
    expected_types = [
        "CONVERSION_STARTED",
        "CONVERSION_COMPLETED", 
        "CONVERSION_FAILED",
        "FILE_PROCESSED",
        "POSTCONVERSION_STARTED",
        "POSTCONVERSION_COMPLETED",
        "ERROR_OCCURRED",
        "SYSTEM_INFO"
    ]
    
    for event_type_name in expected_types:
        assert hasattr(EventType, event_type_name)
        event_type = getattr(EventType, event_type_name)
        assert event_type.value == event_type_name.lower()
    
    print(f"✅ Tipos de eventos: {len(expected_types)} definidos")


def test_logging_observer():
    """Test del observador de logging"""
    print("🧪 Probando observador de logging...")
    
    # Crear archivo de log temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file = f.name
    
    try:
        # Crear observador
        observer = LoggingObserver(log_file)
        
        # Crear evento
        event = Event(EventType.CONVERSION_STARTED, {"file": "test.tiff"})
        
        # Procesar evento
        observer.update(event)
        
        # Verificar que se incrementó el contador
        assert observer.events_logged == 1
        
        # Verificar que se escribió al archivo
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert "conversion_started" in log_content.lower()
            assert "test.tiff" in log_content
        
        print("✅ Observador de logging funcionando")
        
    finally:
        # Limpiar archivo temporal
        Path(log_file).unlink(missing_ok=True)


def test_metrics_observer():
    """Test del observador de métricas"""
    print("🧪 Probando observador de métricas...")
    
    observer = MetricsObserver()
    
    # Emitir diferentes tipos de eventos
    events = [
        Event(EventType.CONVERSION_STARTED, {}),
        Event(EventType.FILE_PROCESSED, {}),
        Event(EventType.CONVERSION_COMPLETED, {"processing_time": 5.5}),
        Event(EventType.CONVERSION_FAILED, {}),
        Event(EventType.ERROR_OCCURRED, {}),
    ]
    
    for event in events:
        observer.update(event)
    
    # Verificar métricas
    metrics = observer.get_metrics()
    
    assert metrics['conversions_started'] == 1
    assert metrics['conversions_completed'] == 1
    assert metrics['conversions_failed'] == 1
    assert metrics['files_processed'] == 1
    assert metrics['errors_occurred'] == 1
    assert metrics['total_processing_time'] == 5.5
    
    # Verificar tasa de éxito
    success_rate = observer.get_success_rate()
    assert success_rate == 100.0  # 1 completada de 1 iniciada
    
    print("✅ Observador de métricas funcionando")


def test_progress_observer():
    """Test del observador de progreso"""
    print("🧪 Probando observador de progreso...")
    
    observer = ProgressObserver()
    
    # Simular progreso de conversión
    events = [
        Event(EventType.CONVERSION_STARTED, {"total_files": 5}),
        Event(EventType.FILE_PROCESSED, {}),
        Event(EventType.FILE_PROCESSED, {}),
        Event(EventType.FILE_PROCESSED, {}),
        Event(EventType.CONVERSION_COMPLETED, {}),
    ]
    
    for event in events:
        observer.update(event)
    
    # Verificar estado del progreso
    assert observer.current_operation == "Conversión"
    assert observer.progress == 3
    assert observer.total == 5
    
    print("✅ Observador de progreso funcionando")


def test_event_manager_attach_detach():
    """Test de adjuntar/desadjuntar observadores"""
    print("🧪 Probando adjuntar/desadjuntar observadores...")
    
    # Crear manager local para test
    manager = EventManager()
    
    # Crear observadores
    observer1 = MockObserver()
    observer2 = MockObserver()
    
    # Adjuntar observadores
    manager.attach(observer1)
    manager.attach(observer2)
    
    assert len(manager.observers) == 2
    
    # Emitir evento
    manager.emit(EventType.CONVERSION_STARTED, {"test": True})
    
    # Verificar que ambos observadores recibieron el evento
    assert observer1.update_count == 1
    assert observer2.update_count == 1
    
    # Desadjuntar un observador
    manager.detach(observer1)
    assert len(manager.observers) == 1
    
    # Emitir otro evento
    manager.emit(EventType.CONVERSION_COMPLETED, {"test": True})
    
    # Verificar que solo observer2 recibió el segundo evento
    assert observer1.update_count == 1  # No cambió
    assert observer2.update_count == 2  # Incrementó
    
    print("✅ Adjuntar/desadjuntar observadores funcionando")


def test_event_manager_notification():
    """Test de notificación de eventos"""
    print("🧪 Probando notificación de eventos...")
    
    manager = EventManager()
    observer = MockObserver()
    
    manager.attach(observer)
    
    # Emitir diferentes tipos de eventos
    event_data = [
        (EventType.CONVERSION_STARTED, {"file": "test1.tiff"}),
        (EventType.FILE_PROCESSED, {"file": "test1.tiff"}),
        (EventType.CONVERSION_COMPLETED, {"file": "test1.tiff", "time": 2.5}),
    ]
    
    for event_type, data in event_data:
        manager.emit(event_type, data)
    
    # Verificar que se recibieron todos los eventos
    assert observer.update_count == 3
    assert len(observer.events_received) == 3
    
    # Verificar tipos de eventos recibidos
    received_types = [event.event_type for event in observer.events_received]
    assert EventType.CONVERSION_STARTED in received_types
    assert EventType.FILE_PROCESSED in received_types
    assert EventType.CONVERSION_COMPLETED in received_types
    
    print("✅ Notificación de eventos funcionando")


def test_event_manager_history():
    """Test del historial de eventos"""
    print("🧪 Probando historial de eventos...")
    
    manager = EventManager()
    
    # Emitir varios eventos
    for i in range(5):
        manager.emit(EventType.SYSTEM_INFO, {"message": f"Info {i}"})
    
    # Verificar historial
    history = manager.get_event_history()
    assert len(history) == 5
    
    # Verificar que los eventos están en orden
    for i, event in enumerate(history):
        assert event.data["message"] == f"Info {i}"
    
    # Limpiar historial
    manager.clear_history()
    assert len(manager.get_event_history()) == 0
    
    print("✅ Historial de eventos funcionando")


def test_event_manager_error_handling():
    """Test de manejo de errores en observadores"""
    print("🧪 Probando manejo de errores en observadores...")
    
    manager = EventManager()
    
    # Crear observadores (uno que falla y uno que funciona)
    failing_observer = FailingObserver()
    working_observer = MockObserver()
    
    manager.attach(failing_observer)
    manager.attach(working_observer)
    
    # Emitir evento (debe manejar el error del observador que falla)
    manager.emit(EventType.CONVERSION_STARTED, {"test": True})
    
    # Verificar que el observador que funciona recibió el evento
    assert working_observer.update_count == 1
    
    print("✅ Manejo de errores en observadores correcto")


def test_global_event_manager():
    """Test del gestor de eventos global"""
    print("🧪 Probando gestor de eventos global...")
    
    # Limpiar observadores existentes
    event_manager.observers.clear()
    
    # Crear observador
    observer = MockObserver()
    event_manager.attach(observer)
    
    # Emitir evento global
    event_manager.emit(EventType.SYSTEM_INFO, {"message": "Test global"})
    
    # Verificar que se recibió
    assert observer.update_count == 1
    assert len(observer.events_received) == 1
    
    # Limpiar
    event_manager.detach(observer)
    
    print("✅ Gestor de eventos global funcionando")


def test_event_manager_max_history():
    """Test del límite de historial"""
    print("🧪 Probando límite de historial...")
    
    manager = EventManager()
    manager.max_history = 3  # Límite pequeño para test
    
    # Emitir más eventos que el límite
    for i in range(5):
        manager.emit(EventType.SYSTEM_INFO, {"id": i})
    
    # Verificar que solo se mantienen los últimos 3
    history = manager.get_event_history()
    assert len(history) == 3
    
    # Verificar que son los últimos 3
    ids = [event.data["id"] for event in history]
    assert ids == [2, 3, 4]  # Los últimos 3
    
    print("✅ Límite de historial funcionando")


def run_observer_tests():
    """Ejecuta todos los tests del Observer Pattern"""
    print("🚀 Iniciando tests del Observer Pattern...")
    print("=" * 50)
    
    tests = [
        test_event_creation,
        test_event_types,
        test_logging_observer,
        test_metrics_observer,
        test_progress_observer,
        test_event_manager_attach_detach,
        test_event_manager_notification,
        test_event_manager_history,
        test_event_manager_error_handling,
        test_global_event_manager,
        test_event_manager_max_history
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test falló: {test.__name__} - {str(e)}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Resultados Observer Pattern:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ¡Todos los tests del Observer Pattern pasaron!")
        return True
    else:
        print("⚠️ Algunos tests del Observer Pattern fallaron")
        return False


if __name__ == "__main__":
    success = run_observer_tests()
    sys.exit(0 if success else 1)
