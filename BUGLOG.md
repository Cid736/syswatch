# Bug Log — syswatch

## 2026-06-25 — Revisión 1

### [HIGH] Endpoints `/control/*` sin autenticación
- **Fix:** Añadida `_check_control()` con token o restricción a localhost.

---

## 2026-06-25 — Revisión 2

### [LOW] CSRF en endpoints `/control/*` via bypass de localhost
- **Archivo:** `web.py`
- **Fix:** Eliminado el bypass de localhost. `CONTROL_TOKEN` es ahora obligatorio.
