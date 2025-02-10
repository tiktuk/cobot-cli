import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from .settings import settings


def save_bookings(bookings: List[Dict], resource_id: str) -> None:
    """Save bookings to JSONL history file."""
    data_dir = str(settings.data_dir)
    history_file = os.path.join(data_dir, f"bookings_{resource_id}.jsonl")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "space_id": str(settings.space_id),
        "resource_id": resource_id,
        "bookings": bookings,
    }

    # Ensure directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Append to JSONL file
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_last_bookings(resource_id: str) -> Optional[List[Dict]]:
    """Get the most recent bookings from history."""
    data_dir = str(settings.data_dir)
    history_file = os.path.join(data_dir, f"bookings_{resource_id}.jsonl")

    if not os.path.exists(history_file):
        return None

    # Read last line of file
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            last_entry = line.strip()

    if not last_entry:
        return None

    try:
        entry = json.loads(last_entry)
        return entry["bookings"]
    except (json.JSONDecodeError, KeyError):
        return None


def find_cancelled_bookings(current: List[Dict], previous: List[Dict]) -> List[Dict]:
    """Find bookings that were present in previous but not in current."""
    current_ids = {b.get("id") or b.get("attributes", {}).get("id") for b in current}
    cancelled = []

    for booking in previous:
        booking_id = booking.get("id") or booking.get("attributes", {}).get("id")
        if booking_id not in current_ids:
            cancelled.append(booking)

    return cancelled


def find_new_bookings(current: List[Dict], previous: List[Dict]) -> List[Dict]:
    """Find bookings that are present in current but not in previous."""
    previous_ids = {b.get("id") or b.get("attributes", {}).get("id") for b in previous}
    new_bookings = []

    for booking in current:
        booking_id = booking.get("id") or booking.get("attributes", {}).get("id")
        if booking_id not in previous_ids:
            new_bookings.append(booking)

    return new_bookings
