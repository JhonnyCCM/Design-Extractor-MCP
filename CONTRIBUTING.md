# Guía de Contribución (Contributing Guide) 🤝

¡Gracias por tu interés en contribuir a **Design Extractor MCP**! Este proyecto es de código abierto y agradecemos sugerencias, corrección de errores, mejoras en la documentación y nuevas funcionalidades.

---

## 🛠️ Entorno de Desarrollo Local

### 1. Clonar el repositorio y configurar el entorno
```bash
git clone https://github.com/JhonnyCCM/Design-Extractor-MCP.git
cd Design-Extractor-MCP
```

### 2. Crear entorno virtual (.venv) e instalar dependencias
En Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

---

## 🧪 Ejecución de Pruebas Unitarias

Antes de enviar cualquier cambio, asegúrate de que todas las pruebas pasen sin errores:

```bash
python -m unittest discover tests
```

Si agregas una nueva funcionalidad o herramienta MCP:
1. Crea o extiende un archivo de prueba en la carpeta `tests/` (por ejemplo, `tests/test_tu_feature.py`).
2. Verifica que las pruebas sigan ejecutándose con `unittest` de manera rápida y sin dependencias externas obligatorias.

---

## 📐 Estilo de Código y Buenas Prácticas

- **Python 3.10+**: Utilizamos tipado estático (`typing.Dict`, `typing.Optional`, `typing.Union`, etc.).
- **Escritura Atómica**: Cualquier persistencia a disco debe utilizar `storage.atomic_write` para evitar escrituras corruptas en caso de interrupción.
- **Manejo Seguro de Procesos**: Al interactuar con Playwright, envuelve siempre la sesión en bloques `try...finally: browser.close()`.
- **Privacidad y Seguridad**: Los mensajes de error expuestos al protocolo MCP deben pasar por `storage.redact_sensitive_data` para no filtrar rutas de usuario o secretos locales.
- **Preservación de Docstrings**: Todo módulo, función o herramienta MCP debe contar con su docstring explicativo en español o inglés técnico estándar.

---

## 📝 Convenciones de Commits (Conventional Commits)

Seguimos el estándar de [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva característica o herramienta MCP (ej. `feat: add oklch color converter`).
- `fix:` Corrección de errores (ej. `fix: handle cors timeout on external fonts`).
- `docs:` Actualización de documentación o README (ej. `docs: update installation instructions`).
- `test:` Inclusión o ajuste de pruebas unitarias (ej. `test: add tests for shadcn generator`).
- `refactor:` Refactorización de código sin cambio de comportamiento externo.
- `chore:` Tareas de mantenimiento, dependencias o configuración CI.

---

## 🚀 Flujo para Pull Requests (PR)

1. Haz un **Fork** del repositorio en GitHub.
2. Crea una rama descriptiva para tu cambio:
   ```bash
   git checkout -b feat/mi-nueva-mejora
   ```
3. Realiza tus cambios asegurándote de que `python -m unittest discover tests` pase exitosamente.
4. Haz commit siguiendo las convenciones:
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```
5. Sube tu rama a tu fork:
   ```bash
   git push origin feat/mi-nueva-mejora
   ```
6. Abre un **Pull Request** hacia la rama `main` del repositorio oficial describiendo la motivación y los cambios realizados.

¡Muchas gracias por hacer de Design Extractor una herramienta más potente y precisa para toda la comunidad! 🌟
