# Bug Log — syswatch

## 2026-06-25 — Revisión 1

### [HIGH] Endpoints `/control/*` sin autenticación
- **Fix:** Añadida `_check_control()` con token o restricción a localhost.

---

## 2026-06-25 — Revisión 2

### [LOW] CSRF en endpoints `/control/*` via bypass de localhost
- **Archivo:** `web.py`
- **Fix:** Eliminado el bypass de localhost. `CONTROL_TOKEN` es ahora obligatorio.

---

## 2026-06-28 — Revisión 3

### [HIGH] Botones Start/Stop/Restart del dashboard siempre devuelven 403
- **Archivo:** `web.py`
- **Descripción:** `_check_control()` verificaba `request.form.get('token')`, pero el HTML del dashboard nunca incluía ese campo en los formularios, haciendo los controles completamente inoperables.
- **Fix:** Sustituido por sesiones Flask firmadas. Se añaden `/login` (GET/POST) y `/logout`. El usuario se autentica con `CONTROL_TOKEN`; la sesión firmada por `FLASK_SECRET_KEY` se verifica en llamadas posteriores. El índice redirige a `/login` si no hay sesión.

### [MEDIA] KeyError en `check_thresholds` cuando el umbral no está en `config.yml`
- **Archivo:** `monitor.py`, función `check_thresholds`
- **Descripción:** El mensaje de alerta usaba `cfg['cpu_pct']`, `cfg['ram_pct']`, etc. directamente (sin `.get()`). Si `config.yml` no existía o algún campo faltaba, el proceso lanzaba `KeyError` en lugar de usar el valor por defecto.
- **Fix:** Variables locales `cpu_thr`, `ram_thr`, `disk_thr`, `load_thr` calculadas con `.get()` una sola vez y reutilizadas tanto en la comparación como en el mensaje.

### [BAJA] Errores de Telegram silenciados sin traza
- **Archivo:** `notifier.py`
- **Descripción:** `except Exception: pass` ocultaba fallos de red o errores de la API de Telegram.
- **Fix:** `logging.warning()` registra el código de estado HTTP y la excepción.

### [BAJA] `/api/metrics` era POST en lugar de GET
- **Archivo:** `web.py`
- **Fix:** Cambiado a `methods=["GET"]`.
