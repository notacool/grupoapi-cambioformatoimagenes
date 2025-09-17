#!/usr/bin/env python3
"""
Test Suite Completo para Patrones de Diseño
===========================================

Ejecuta todos los tests de los patrones de diseño implementados.
"""

import sys
import time
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.output_manager import output_manager


def run_all_pattern_tests():
    """Ejecuta todos los tests de patrones de diseño"""
    print("🚀 Iniciando Test Suite Completo de Patrones de Diseño")
    print("=" * 60)
    
    # Importar y ejecutar tests de cada patrón
    test_modules = [
        ("Factory Pattern", "test_factory_pattern"),
        ("Strategy Pattern", "test_strategy_pattern"),
        ("Observer Pattern", "test_observer_pattern"),
        ("Builder Pattern", "test_builder_pattern"),
        ("Command Pattern", "test_command_pattern")
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    start_time = time.time()
    
    for pattern_name, module_name in test_modules:
        print(f"\n🧪 Ejecutando tests de {pattern_name}...")
        print("-" * 40)
        
        try:
            # Importar módulo de test
            module = __import__(module_name)
            
            # Ejecutar función de test
            if hasattr(module, f'run_{module_name.split("_")[1]}_tests'):
                test_function = getattr(module, f'run_{module_name.split("_")[1]}_tests')
                success = test_function()
                
                if success:
                    results[pattern_name] = "✅ PASÓ"
                    total_passed += 1
                else:
                    results[pattern_name] = "❌ FALLÓ"
                    total_failed += 1
            else:
                print(f"⚠️ Función de test no encontrada en {module_name}")
                results[pattern_name] = "⚠️ ERROR"
                total_failed += 1
                
        except ImportError as e:
            print(f"❌ Error importando {module_name}: {str(e)}")
            results[pattern_name] = "❌ ERROR DE IMPORT"
            total_failed += 1
        except Exception as e:
            print(f"❌ Error ejecutando tests de {pattern_name}: {str(e)}")
            results[pattern_name] = "❌ ERROR DE EJECUCIÓN"
            total_failed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Mostrar resultados finales
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES DEL TEST SUITE")
    print("=" * 60)
    
    for pattern_name, result in results.items():
        print(f"{result} {pattern_name}")
    
    print("-" * 60)
    print(f"📈 Resumen General:")
    print(f"   ✅ Patrones que pasaron: {total_passed}")
    print(f"   ❌ Patrones que fallaron: {total_failed}")
    print(f"   📊 Total de patrones: {len(test_modules)}")
    print(f"   🎯 Tasa de éxito: {(total_passed/len(test_modules)*100):.1f}%")
    print(f"   ⏱️ Tiempo total: {total_time:.2f} segundos")
    
    if total_failed == 0:
        print("\n🎉 ¡TODOS LOS PATRONES DE DISEÑO PASARON LOS TESTS!")
        print("✅ El sistema está listo para producción con patrones implementados")
        return True
    else:
        print(f"\n⚠️ {total_failed} patrones fallaron los tests")
        print("🔧 Revisar implementaciones antes de usar en producción")
        return False


def run_individual_pattern_test(pattern_name):
    """Ejecuta test de un patrón específico"""
    pattern_modules = {
        "factory": "test_factory_pattern",
        "strategy": "test_strategy_pattern", 
        "observer": "test_observer_pattern",
        "builder": "test_builder_pattern",
        "command": "test_command_pattern"
    }
    
    if pattern_name.lower() not in pattern_modules:
        print(f"❌ Patrón '{pattern_name}' no encontrado")
        print(f"Patrones disponibles: {list(pattern_modules.keys())}")
        return False
    
    module_name = pattern_modules[pattern_name.lower()]
    print(f"🧪 Ejecutando test de {pattern_name.title()} Pattern...")
    
    try:
        module = __import__(module_name)
        test_function = getattr(module, f'run_{pattern_name.lower()}_tests')
        return test_function()
    except Exception as e:
        print(f"❌ Error ejecutando test: {str(e)}")
        return False


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        # Ejecutar patrón específico
        pattern_name = sys.argv[1]
        success = run_individual_pattern_test(pattern_name)
    else:
        # Ejecutar todos los tests
        success = run_all_pattern_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
