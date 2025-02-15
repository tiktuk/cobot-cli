import pytest
import os
import json
from datetime import datetime, timedelta
from dateutil.tz import tzutc
from cobot_cli.history import (
    save_bookings,
    get_last_bookings,
    find_cancelled_bookings,
    find_new_bookings,
)
from unittest.mock import patch, mock_open

@pytest.fixture
def mock_settings():
    with patch("cobot_cli.history.settings") as mock_settings:
        mock_settings.data_dir = "/tmp/test_data"
        mock_settings.space_id = "test-space"
        yield mock_settings

@pytest.fixture
def sample_booking():
    return {
        "id": "booking-1",
        "attributes": {
            "from": "2024-02-15T09:00:00Z",
            "to": "2024-02-15T10:00:00Z",
            "name": "John Doe",
            "title": "Meeting"
        }
    }

@pytest.fixture
def sample_bookings(sample_booking):
    return [sample_booking]

def test_save_bookings(mock_settings, sample_bookings):
    """Test saving bookings to history file"""
    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        
        save_bookings(sample_bookings, "resource-1")
        
        # Check if directory was created
        mock_makedirs.assert_called_once_with("/tmp/test_data", exist_ok=True)
        
        # Check if file was opened for appending
        m.assert_called_once_with(
            "/tmp/test_data/bookings_resource-1.jsonl",
            "a",
            encoding="utf-8"
        )
        
        # Check if data was written
        handle = m()
        written_data = handle.write.call_args[0][0]
        entry = json.loads(written_data)
        
        assert entry["resource_id"] == "resource-1"
        assert entry["space_id"] == "test-space"
        assert entry["bookings"] == sample_bookings

def test_get_last_bookings_no_file(mock_settings):
    """Test getting last bookings when file doesn't exist"""
    with patch("os.path.exists", return_value=False):
        result = get_last_bookings("resource-1")
        assert result is None

def test_get_last_bookings(mock_settings, sample_bookings):
    """Test getting last bookings from history file"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "space_id": "test-space",
        "resource_id": "resource-1",
        "bookings": sample_bookings
    }
    
    m = mock_open(read_data=json.dumps(entry) + "\n")
    with patch("builtins.open", m), \
         patch("os.path.exists", return_value=True):
        
        result = get_last_bookings("resource-1")
        assert result == sample_bookings

def test_find_cancelled_bookings():
    """Test finding cancelled bookings"""
    now = datetime.now(tzutc())
    future = now + timedelta(hours=2)
    past = now - timedelta(hours=2)
    
    # Create bookings with different end times
    future_booking = {
        "id": "future",
        "attributes": {
            "from": now.isoformat(),
            "to": future.isoformat()
        }
    }
    past_booking = {
        "id": "past",
        "attributes": {
            "from": past.isoformat(),
            "to": past.isoformat()
        }
    }
    
    previous = [future_booking, past_booking]
    current = []  # All bookings removed
    
    cancelled = find_cancelled_bookings(current, previous)
    
    # Only future booking should be considered cancelled
    assert len(cancelled) == 1
    assert cancelled[0]["id"] == "future"

def test_find_new_bookings(sample_booking):
    """Test finding new bookings"""
    previous = []
    current = [sample_booking]
    
    new_bookings = find_new_bookings(current, previous)
    
    assert len(new_bookings) == 1
    assert new_bookings[0] == sample_booking

def test_find_new_bookings_with_existing():
    """Test finding new bookings when some already exist"""
    existing_booking = {
        "id": "existing",
        "attributes": {
            "name": "Existing Booking"
        }
    }
    new_booking = {
        "id": "new",
        "attributes": {
            "name": "New Booking"
        }
    }
    
    previous = [existing_booking]
    current = [existing_booking, new_booking]
    
    new_bookings = find_new_bookings(current, previous)
    
    assert len(new_bookings) == 1
    assert new_bookings[0]["id"] == "new"
