# syswatch

System resource monitor for Linux servers. Tracks CPU, RAM, disk usage and load average. Sends Telegram alerts when configurable thresholds are exceeded. Runs as a one-shot check or as a daemon.

## Stack
Python · psutil · PyYAML · SQLite · Telegram Bot API

## Demo

```
$ python main.py check

  syswatch — 2026-06-24 10:32:01 UTC — myserver
  ─────────────────────────────────────────────────────
  CPU        14.3%
  RAM        67.8%   (5.42 / 8.0 GB)
  Disk       73.1%   (146.2 / 200.0 GB)
  Load       0.82  0.74  0.68  (1m / 5m / 15m)
  Net I/O    sent 1240.5 MB   recv 8730.2 MB

  [ok] All metrics within thresholds

$ python main.py run --interval 5

  Monitoring every 5 min. Ctrl+C to stop.

  syswatch — 2026-06-24 10:37:01 UTC — myserver
  ─────────────────────────────────────────────────────
  CPU        93.7%
  RAM        91.2%   (7.3 / 8.0 GB)
  ...
  [!] CPU at 93.7% (threshold 90%) | RAM at 91.2% (threshold 90%)
```

Telegram alert:
```
⚠️ syswatch alert — myserver
  • CPU at 93.7% (threshold 90%)
  • RAM at 91.2% (threshold 90%)
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
load_1m:  4.0     # Load average 1m — set to number of CPU cores for 100% load
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
- Web dashboard with progress bars, history table and Start/Stop/Restart controls, alpha banner
