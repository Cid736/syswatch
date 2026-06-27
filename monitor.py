import psutil
import time
from datetime import datetime


def cpu(interval=1.0) -> float:
    return psutil.cpu_percent(interval=interval)


def ram() -> dict:
    m = psutil.virtual_memory()
    return {"used_pct": m.percent, "used_gb": round(m.used / 1e9, 2), "total_gb": round(m.total / 1e9, 2)}


def disk(path="/") -> dict:
    d = psutil.disk_usage(path)
    return {"used_pct": d.percent, "used_gb": round(d.used / 1e9, 2), "total_gb": round(d.total / 1e9, 2)}


def load() -> tuple[float, float, float]:
    try:
        return psutil.getloadavg()
    except AttributeError:
        return (0.0, 0.0, 0.0)


def net_io() -> dict:
    n = psutil.net_io_counters()
    return {"sent_mb": round(n.bytes_sent / 1e6, 2), "recv_mb": round(n.bytes_recv / 1e6, 2)}


def snapshot(cpu_interval=1.0) -> dict:
    return {
        "ts":   datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu":  cpu(cpu_interval),
        "ram":  ram(),
        "disk": disk(),
        "load": load(),
        "net":  net_io(),
    }


def check_thresholds(snap: dict, cfg: dict) -> list[str]:
    alerts = []
    cpu_thr  = cfg.get("cpu_pct",  90)
    ram_thr  = cfg.get("ram_pct",  90)
    disk_thr = cfg.get("disk_pct", 85)
    load_thr = cfg.get("load_1m",  4.0)
    if snap["cpu"] >= cpu_thr:
        alerts.append(f"CPU at {snap['cpu']}% (threshold {cpu_thr}%)")
    if snap["ram"]["used_pct"] >= ram_thr:
        alerts.append(f"RAM at {snap['ram']['used_pct']}% (threshold {ram_thr}%)")
    if snap["disk"]["used_pct"] >= disk_thr:
        alerts.append(f"Disk at {snap['disk']['used_pct']}% (threshold {disk_thr}%)")
    load1 = snap["load"][0]
    if load1 >= load_thr:
        alerts.append(f"Load avg (1m) at {load1} (threshold {load_thr})")
    return alerts
