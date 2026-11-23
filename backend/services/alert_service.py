"""
Alert Service — Offline alerts (console + log file)
Extendable: add email, SMS, sound, etc.
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from backend.config import settings


SEPARATOR = "=" * 60


def trigger_alert(criminal: dict, confidence: float) -> None:
    """
    Trigger a local alert when a criminal is identified.
    Currently: prints to console + writes to alert log file.
    """
    name = criminal.get("name", "Unknown")
    alias = criminal.get("alias", "N/A")
    crime = criminal.get("crime", "N/A")
    danger = criminal.get("danger_level", "unknown").upper()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    alert_msg = f"""
{SEPARATOR}
⚠️  MOST-WANTED PERSON DETECTED!
{SEPARATOR}
  Name       : {name}
  Alias      : {alias}
  Crime      : {crime}
  Danger     : {danger}
  Confidence : {confidence:.1f}%
  Time       : {ts}
{SEPARATOR}
"""
    print(alert_msg)
    _write_alert_log(alert_msg)


def _write_alert_log(message: str) -> None:
    """Append alert to a local log file."""
    try:
        log_dir = Path(settings.LOGS_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "alerts.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"[AlertService] Could not write log: {e}")
