# Bug Log — syswatch

## 2026-06-25

### [HIGH] Endpoints `/control/*` sin autenticación
- **Archivo:** `web.py`
- **Fix:** Añadida función `_check_control()` que restringe los endpoints de control a localhost (127.0.0.1/::1) si no hay `CONTROL_TOKEN` configurado, o verifica el token en el formulario si está configurado.
