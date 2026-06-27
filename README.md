<p align="center">
  <a href="#english">🇬🇧 English</a> &nbsp;·&nbsp; <a href="#español">🇪🇸 Español</a>
</p>

---

<a name="english"></a>

# syswatch

System resource monitor for Linux servers. Tracks CPU, RAM, disk usage and load average. Sends Telegram alerts when configurable thresholds are exceeded. Runs as a one-shot check or as a daemon.

## Stack
Python · psutil · PyYAML · SQLite · Telegram Bot API

## Demo

```
$ python main.py check

  syswatch -- 2026-06-24 10:32:01 UTC -- myserver
  -------------------------------------------------
  CPU        14.3%
  RAM        67.8%   (5.42 / 8.0 GB)
  Disk       73.1%   (146.2 / 200.0 GB)
  Load       0.82  0.74  0.68  (1m / 5m / 15m)
  Net I/O    sent 1240.5 MB   recv 8730.2 MB

  [ok] All metrics within thresholds
```

Telegram alert:
```
syswatch alert -- myserver
  - CPU at 93.7% (threshold 90%)
  - RAM at 91.2% (threshold 90%)
```

## Setup

```bash
git clone https://github.com/Cid736/syswatch.git
cd syswatch
pip install -r requirements.txt
cp .env.example .env
# Add Telegram credentials (optional — alerts won't fire without them)
```

## Usage

```bash
# One-shot check (alerts if thresholds exceeded)
python main.py check

# One-shot check without sending alert
python main.py check --no-alert

# Show current metrics + configured thresholds
python main.py report

# Daemon mode — checks every 5 minutes, alerts on new threshold breaches
python main.py run --interval 5
```

## Configuration

Edit `config.yml` to set your thresholds:

```yaml
cpu_pct:  90      # CPU usage %
ram_pct:  90      # RAM usage %
disk_pct: 85      # Disk usage %
load_1m:  4.0     # Load average 1m
```

## Telegram setup

1. Create a bot with [@BotFather](https://t.me/BotFather) — get `TELEGRAM_TOKEN`
2. Message your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to get `TELEGRAM_CHAT_ID`
3. Add both to `.env`

## Automate with cron (Linux)

```bash
# Check every 5 minutes
*/5 * * * * /usr/bin/python3 /opt/syswatch/main.py check >> /var/log/syswatch.log 2>&1
```

## Changelog

**v0.1.1** — 2026-06-24
- Fix: collector thread now catches exceptions and keeps running instead of silently dying
- Fix: replaced garbled em-dash sequences in CLI output that caused display issues on Windows

**v0.1.0** — 2026-06-23
- Initial release: CPU, RAM, disk and load monitoring, Telegram alerts, configurable thresholds

## Security

Automated security reviews are powered by [Claude](https://claude.ai) (Anthropic AI) and run on every significant change. Findings are tracked in [`BUGLOG.md`](BUGLOG.md).

**Last review:** 2026-06-28 — 3 new issues found (1 high, 1 medium, 2 low) — all patched.

### Model

| Control | Implementation |
|---|---|
| Dashboard authentication | Session-based login at `/login`; `CONTROL_TOKEN` (required) authenticates the session; `FLASK_SECRET_KEY` signs cookies |
| No user-supplied shell commands | psutil reads `/proc` directly — no subprocess calls, no injection surface |
| Secret management | Credentials via `.env` / environment variables only; `.env` is git-ignored |
| Threshold error safety | All threshold defaults use `.get()` — no `KeyError` if `config.yml` is missing fields |
| Security headers | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` on every response |

### Required `.env` variables

```
CONTROL_TOKEN=<random 32+ char string>    # protects the web dashboard
FLASK_SECRET_KEY=<random 32+ char string> # signs Flask session cookies
TELEGRAM_TOKEN=<bot token>               # optional — alerts won't fire without it
TELEGRAM_CHAT_ID=<chat id>               # optional
```

Found a vulnerability? Open an issue or contact directly.

---

<a name="español"></a>

# syswatch

Monitor de recursos del sistema para servidores Linux. Rastrea CPU, RAM, disco y carga media. Envía alertas por Telegram cuando se superan los umbrales configurables. Funciona como comprobación puntual o como demonio.

## Stack
Python · psutil · PyYAML · SQLite · Telegram Bot API

## Instalación

```bash
git clone https://github.com/Cid736/syswatch.git
cd syswatch
pip install -r requirements.txt
cp .env.example .env
# Añade tus credenciales de Telegram (opcional — sin ellas las alertas no se envían)
```

## Uso

```bash
# Comprobación puntual (alerta si se superan umbrales)
python main.py check

# Comprobación puntual sin enviar alerta
python main.py check --no-alert

# Mostrar métricas actuales + umbrales configurados
python main.py report

# Modo demonio — comprueba cada 5 minutos, alerta en nuevas superaciones
python main.py run --interval 5
```

## Configuración

Edita `config.yml` para definir tus umbrales:

```yaml
cpu_pct:  90      # % de uso de CPU
ram_pct:  90      # % de uso de RAM
disk_pct: 85      # % de uso de disco
load_1m:  4.0     # Carga media 1m
```

## Automatizar con cron (Linux)

```bash
# Comprobar cada 5 minutos
*/5 * * * * /usr/bin/python3 /opt/syswatch/main.py check >> /var/log/syswatch.log 2>&1
```

## Seguridad

Las revisiones de seguridad automatizadas utilizan [Claude](https://claude.ai) (Anthropic AI) y se ejecutan en cada cambio significativo. Los hallazgos se registran en [`BUGLOG.md`](BUGLOG.md).

**Última revisión:** 2026-06-28 — 3 nuevas vulnerabilidades encontradas (1 alta, 1 media, 2 bajas) — todas parcheadas.

| Control | Implementación |
|---|---|
| Autenticación del dashboard | Login de sesión en `/login`; `CONTROL_TOKEN` (obligatorio) autentica la sesión; `FLASK_SECRET_KEY` firma las cookies |
| Sin comandos de shell | psutil lee `/proc` directamente — sin subprocess, sin superficie de inyección |
| Gestión de secretos | Credenciales solo via `.env` / variables de entorno; `.env` en `.gitignore` |
| Seguridad en umbrales | Todos los defaults usan `.get()` — sin `KeyError` si faltan campos en `config.yml` |
| Cabeceras de seguridad | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` en cada respuesta |

¿Encontraste una vulnerabilidad? Abre un issue o contacta directamente.
## Licencia

MIT
