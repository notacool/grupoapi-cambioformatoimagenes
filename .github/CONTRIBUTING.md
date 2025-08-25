# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir al Conversor TIFF! Este documento te guiará a través del proceso de contribución.

## 📋 Tabla de Contenidos

- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Documentación](#documentación)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Funcionalidades](#solicitar-funcionalidades)
- [Preguntas Frecuentes](#preguntas-frecuentes)

## 🚀 Cómo Contribuir

### **Tipos de Contribuciones Aceptadas:**

- 🐛 **Reportes de bugs** - Ayudan a mejorar la estabilidad
- ✨ **Nuevas funcionalidades** - Expanden las capacidades
- 📚 **Mejoras de documentación** - Hacen el proyecto más accesible
- 🧪 **Tests** - Mejoran la calidad y confiabilidad
- 🔧 **Mejoras de código** - Optimizaciones y refactorizaciones
- 🌍 **Traducciones** - Hacen el proyecto más accesible globalmente

### **Antes de Contribuir:**

1. **Revisa los issues existentes** para evitar duplicados
2. **Lee la documentación** del proyecto
3. **Asegúrate de que tu contribución** esté alineada con los objetivos del proyecto
4. **Consulta** si tienes dudas sobre la implementación

## 🛠️ Configuración del Entorno

### **Requisitos:**

- Python 3.8+
- Git
- Editor de código (VS Code, PyCharm, etc.)

### **Configuración Local:**

1. **Fork del repositorio:**
   ```bash
   # Ve a GitHub y haz fork del repositorio
   # Luego clona tu fork
   git clone https://github.com/TU_USUARIO/grupoapi-cambioformatoimagenes.git
   cd grupoapi-cambioformatoimagenes
   ```

2. **Configurar upstream:**
   ```bash
   git remote add upstream https://github.com/notacool/grupoapi-cambioformatoimagenes.git
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación:**
   ```bash
   python test_converter.py
   ```

## 🔀 Flujo de Trabajo

### **1. Crear Rama de Desarrollo:**

```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear rama para tu feature
git checkout -b feature/nombre-de-tu-feature
```

### **2. Hacer Cambios:**

- **Código:** Implementa tu funcionalidad
- **Tests:** Agrega tests para tu código
- **Documentación:** Actualiza documentación relevante

### **3. Commit y Push:**

```bash
# Agregar cambios
git add .

# Commit descriptivo
git commit -m "feat: agregar nueva funcionalidad X

- Descripción detallada de los cambios
- Resuelve #123
- Breaking change: no"

# Push a tu fork
git push origin feature/nombre-de-tu-feature
```

### **4. Crear Pull Request:**

- Ve a GitHub y crea un Pull Request
- Usa la plantilla de PR
- Describe claramente los cambios
- Incluye tests y documentación

### **5. Revisión y Merge:**

- Responde a cualquier feedback
- Haz los cambios solicitados
- Una vez aprobado, se hará merge

## 📝 Estándares de Código

### **Python:**

- **Versión:** Python 3.8+
- **Estilo:** PEP 8 (usar Black para formateo)
- **Tipos:** Type hints cuando sea posible
- **Docstrings:** Google style para funciones públicas

### **Ejemplo de Código:**

```python
from pathlib import Path
from typing import Dict, Any, Optional

def convert_image(
    input_path: Path, 
    output_path: Path, 
    config: Dict[str, Any]
) -> bool:
    """
    Convierte una imagen de un formato a otro.
    
    Args:
        input_path: Ruta del archivo de entrada
        output_path: Ruta del archivo de salida
        config: Configuración de conversión
        
    Returns:
        True si la conversión fue exitosa, False en caso contrario
        
    Raises:
        ValueError: Si los parámetros son inválidos
        FileNotFoundError: Si el archivo de entrada no existe
    """
    try:
        # Validar entrada
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
            
        # Implementar conversión
        # ... código de conversión ...
        
        return True
        
    except Exception as e:
        print(f"Error en conversión: {str(e)}")
        return False
```

### **Commits:**

- **Formato:** `tipo: descripción breve`
- **Tipos:** `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- **Ejemplos:**
  - `feat: agregar conversor BMP`
  - `fix: corregir error de memoria en conversión JPG`
  - `docs: actualizar README con nuevos formatos`

## 🧪 Testing

### **Ejecutar Tests:**

```bash
# Tests completos
python test_converter.py

# Tests específicos
python test_converter.py TestTIFFConverter.test_jpg_converter

# Tests con verbose
python test_converter.py -v
```

### **Escribir Tests:**

```python
def test_my_converter(self):
    """Test del conversor personalizado"""
    # Arrange
    converter = MyConverter({'enabled': True})
    input_path = Path("test_input/test.tiff")
    output_path = Path("test_output/test.output")
    
    # Act
    success = converter.convert(input_path, output_path)
    
    # Assert
    self.assertTrue(success)
    self.assertTrue(output_path.exists())
```

### **Cobertura de Tests:**

- **Objetivo:** >90% de cobertura
- **Nuevas funcionalidades:** 100% de cobertura
- **Tests de integración:** Para funcionalidades complejas

## 📚 Documentación

### **Documentar Código:**

- **Docstrings:** Para todas las funciones públicas
- **Comentarios:** Para lógica compleja
- **README:** Actualizar con nuevas funcionalidades
- **DEVELOPER_GUIDE:** Agregar ejemplos de uso

### **Ejemplo de Documentación:**

```python
class MyConverter(BaseConverter):
    """
    Conversor personalizado para formato X.
    
    Este conversor implementa la funcionalidad para convertir
    archivos TIFF al formato X con opciones configurables.
    
    Attributes:
        quality: Calidad de la conversión (1-100)
        format: Formato de salida específico
        
    Example:
        >>> converter = MyConverter({'quality': 95})
        >>> success = converter.convert(input_path, output_path)
        >>> print(f"Conversión exitosa: {success}")
        Conversión exitosa: True
    """
```

## 🐛 Reportar Bugs

### **Antes de Reportar:**

1. **Verifica** que el bug no haya sido reportado
2. **Reproduce** el bug en tu entorno
3. **Recopila** información relevante (logs, configuración, etc.)

### **Información Requerida:**

- **Descripción clara** del problema
- **Pasos para reproducir**
- **Comportamiento esperado vs. actual**
- **Información del sistema** (OS, Python, etc.)
- **Archivos de ejemplo** si es posible

## ✨ Solicitar Funcionalidades

### **Antes de Solicitar:**

1. **Revisa** si la funcionalidad ya existe
2. **Considera** el impacto en el proyecto
3. **Evalúa** la complejidad de implementación

### **Información Requerida:**

- **Caso de uso** específico
- **Beneficios** para los usuarios
- **Alternativas** consideradas
- **Propuesta** de implementación

## ❓ Preguntas Frecuentes

### **¿Puedo contribuir si soy principiante?**

¡Absolutamente! Las contribuciones de principiantes son bienvenidas. Comienza con:
- Reportes de bugs
- Mejoras de documentación
- Tests simples
- Issues de "good first issue"

### **¿Qué hago si mi PR no es aprobado?**

- **Lee el feedback** cuidadosamente
- **Haz los cambios** solicitados
- **Pregunta** si algo no está claro
- **Mantén la comunicación** abierta

### **¿Cómo puedo obtener ayuda?**

- **Issues de GitHub:** Para preguntas generales
- **Discussions:** Para debates y ideas
- **Documentación:** DEVELOPER_GUIDE.md
- **Tests:** Como ejemplos de uso

### **¿Puedo contribuir con conversores específicos?**

¡Sí! Los nuevos conversores son bienvenidos. Sigue la guía en `DEVELOPER_GUIDE.md` y usa `examples/add_new_converter.py` como plantilla.

## 🎯 Próximos Pasos

1. **Fork** el repositorio
2. **Configura** tu entorno local
3. **Elige** un issue o crea uno nuevo
4. **Implementa** tu contribución
5. **Envía** un Pull Request

## 📞 Contacto

- **Issues:** [GitHub Issues](https://github.com/notacool/grupoapi-cambioformatoimagenes/issues)
- **Discussions:** [GitHub Discussions](https://github.com/notacool/grupoapi-cambioformatoimagenes/discussions)
- **Documentación:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

**¡Gracias por contribuir al Conversor TIFF!** 🎉

Tu contribución ayuda a hacer este proyecto mejor para todos los usuarios.
