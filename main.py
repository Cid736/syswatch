#!/usr/bin/env python3
"""
syswatch â€” system resource monitor
Tracks CPU, RAM, disk and network I/O.
Sends Telegram alerts when configurable thresholds are exceeded.
"""

import argparse
import socket
import time
import yaml
from pathlib import Path
from dotenv import load_dotenv
from monitor import snapshot, check_thresholds
from notifier import alert

load_dotenv()

CONFIG_FILE = Path(__file__).parent / "config.yml"
HOSTNAME    = socket.gethostname()


def load_cfg() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def print_snapshot(snap: dict):
    r = snap["ram"]
    d = snap["disk"]
    l = snap["load"]
    n = snap["net"]
    print(f"\n  syswatch â€” {snap['ts']} UTC â€” {HOSTNAME}")
    print(f"  {'-'*55}")
    print(f"  CPU      {snap['cpu']:>6.1f}%")
    print(f"  RAM      {r['used_pct']:>6.1f}%   ({r['used_gb']} / {r['total_gb']} GB)")
    print(f"  Disk     {d['used_pct']:>6.1f}%   ({d['used_gb']} / {d['total_gb']} GB)")
    print(f"  Load     {l[0]:.2f}  {l[1]:.2f}  {l[2]:.2f}  (1m / 5m / 15m)")
    print(f"  Net I/O  sent {n['sent_mb']} MB   recv {n['recv_mb']} MB")
    print()


# â”€â”€ commands â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def cmd_check(args):
    cfg  = load_cfg()
    snap = snapshot()
    print_snapshot(snap)

    issues = check_thresholds(snap, cfg)
    if issues:
        print("  [!] Threshold breaches:")
        for i in issues:
            print(f"      - {i}")
        if not args.no_alert:
            alert(HOSTNAME, issues)
    else:
        print("  [ok] All metrics within thresholds")
    print()


def cmd_run(args):
    cfg      = load_cfg()
    interval = args.interval * 60
    last_alert_issues: set[str] = set()

    print(f"Monitoring every {args.interval} min. Ctrl+C to stop.\n")
    while True:
        snap   = snapshot()
        print_snapshot(snap)
        issues = check_thresholds(snap, cfg)

        if issues:
            new = set(issues) - last_alert_issues
            if new:
                alert(HOSTNAME, list(new))
                last_alert_issues = set(issues)
            print("  [!] " + " | ".join(issues))
        else:
            last_alert_issues = set()
            print("  [ok] All metrics within thresholds")

        print(f"  -- next check in {args.interval} min --\n")
        time.sleep(interval)


def cmd_report(_args):
    cfg    = load_cfg()
    thresholds = {
        "CPU threshold":  f"{cfg.get('cpu_pct',  90)}%",
        "RAM threshold":  f"{cfg.get('ram_pct',  90)}%",
        "Disk threshold": f"{cfg.get('disk_pct', 85)}%",
        "Load 1m limit":  str(cfg.get("load_1m", 4.0)),
    }
    snap = snapshot()
    print_snapshot(snap)
    print("  Configured thresholds:")
    for k, v in thresholds.items():
        print(f"    {k:<20} {v}")
    print()


# â”€â”€ CLI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    p = argparse.ArgumentParser(
        prog="syswatch",
        description="System resource monitor with Telegram alerts",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="One-shot resource check")
    c.add_argument("--no-alert", action="store_true", help="Skip Telegram alert even if thresholds exceeded")

    r = sub.add_parser("run", help="Monitor continuously")
    r.add_argument("--interval", type=int, default=5, help="Minutes between checks (default: 5)")

    sub.add_parser("report", help="Show current metrics and configured thresholds")

    args = p.parse_args()
    {"check": cmd_check, "run": cmd_run, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()

