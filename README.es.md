# syswatch

Monitor de recursos del sistema para servidores Linux. Rastrea CPU, RAM, uso de disco y carga del sistema. Envía alertas por Telegram cuando se superan umbrales configurables. Funciona como comprobación puntual o como demonio.

## Stack
Python · psutil · PyYAML · SQLite · Telegram Bot API

## Demo

```
$ python main.py check

  syswatch — 2026-06-24 10:32:01 UTC — miservidor
  ─────────────────────────────────────────────────────
  CPU        14.3%
  RAM        67.8%   (5.42 / 8.0 GB)
  Disk       73.1%   (146.2 / 200.0 GB)
  Load       0.82  0.74  0.68  (1m / 5m / 15m)
  Net I/O    sent 1240.5 MB   recv 8730.2 MB

  [ok] All metrics within thresholds

$ python main.py run --interval 5

  Monitorizando cada 5 min. Ctrl+C para detener.

  syswatch — 2026-06-24 10:37:01 UTC — miservidor
  ─────────────────────────────────────────────────────
  CPU        93.7%
  RAM        91.2%   (7.3 / 8.0 GB)
  ...
  [!] CPU at 93.7% (threshold 90%) | RAM at 91.2% (threshold 90%)
```

Alerta de Telegram:
```
⚠️ syswatch alert — miservidor
  • CPU at 93.7% (threshold 90%)
  • RAM at 91.2% (threshold 90%)
```

## Instalación

```bash
git clone https://github.com/Cid736/syswatch.git
cd syswatch
pip install -r requirements.txt
cp .env.example .env
# Añade tus credenciales de Telegram (opcional — las alertas no funcionan sin ellas)
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

Edita `config.yml` para ajustar tus umbrales:

```yaml
cpu_pct:  90      # Uso de CPU %
ram_pct:  90      # Uso de RAM %
disk_pct: 85      # Uso de disco %
load_1m:  4.0     # Carga media 1m — igual al número de núcleos CPU para carga 100%
```

## Configurar Telegram

1. Crea un bot con [@BotFather](https://t.me/BotFather) — obtén `TELEGRAM_TOKEN`
2. Escribe a tu bot, luego visita `https://api.telegram.org/bot<TOKEN>/getUpdates` para obtener `TELEGRAM_CHAT_ID`
3. Añade ambos al archivo `.env`

## Automatizar con cron (Linux)

```bash
# Comprobar cada 5 minutos
*/5 * * * * /usr/bin/python3 /opt/syswatch/main.py check >> /var/log/syswatch.log 2>&1
```

## Historial de versiones

**v0.1.1** — 2026-06-24
- Fix: reemplazadas secuencias de guion largo corruptas en la salida CLI que causaban problemas de visualización en Windows

**v0.1.0** — 2026-06-23
- Publicación inicial: monitorización de CPU, RAM, disco y carga, alertas Telegram, umbrales configurables
- Dashboard web con barras de progreso, historial y controles Iniciar/Parar/Reiniciar, banner alfa
