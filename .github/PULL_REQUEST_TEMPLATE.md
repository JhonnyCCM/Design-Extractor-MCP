## Descripción del Cambio 📋
Por favor resume brevemente la motivación de este Pull Request y qué problema resuelve o qué funcionalidad introduce.

## Tipo de Cambio 🏷️
- [ ] Corrección de error (`fix`)
- [ ] Nueva funcionalidad o herramienta MCP (`feat`)
- [ ] Mejora de documentación (`docs`)
- [ ] Refactorización de código (`refactor`)
- [ ] Pruebas unitarias adicionales (`test`)
- [ ] Configuración o CI (`chore`)

## Lista de Verificación (Checklist) ✅
- [ ] He ejecutado `python -m unittest discover tests` y todas las pruebas pasan exitosamente.
- [ ] Mis cambios no introducen escrituras directas inseguras (utilizo `storage.atomic_write`).
- [ ] He manejado los recursos de Playwright con bloques `try...finally: browser.close()`.
- [ ] He redactado información sensible con `storage.redact_sensitive_data` si aplica.
- [ ] He actualizado la documentación (`README.md`) si este cambio afecta comandos de usuario o herramientas MCP.
- [ ] He seguido las convenciones de [Conventional Commits](https://www.conventionalcommits.org/).
