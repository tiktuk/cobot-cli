import pytest
from datetime import datetime, timedelta
from dateutil.tz import tzutc
from cobot_cli.cli import (
    format_date,
    format_time_range,
    format_booking_info,
    fetch_bookings,
    create_bookings_table,
)
from unittest.mock import patch, MagicMock

def test_format_date():
    """Test date formatting function"""
    dt = datetime(2024, 2, 15, tzinfo=tzutc())
    assert format_date(dt) == "Thu 15 Feb"

def test_format_time_range():
    """Test time range formatting function"""
    from_time = datetime(2024, 2, 15, 9, 0, tzinfo=tzutc())
    to_time = datetime(2024, 2, 15, 10, 30, tzinfo=tzutc())
    assert format_time_range(from_time, to_time) == "09:00 - 10:30"

def test_format_booking_info():
    """Test booking info formatting"""
    assert format_booking_info("John Doe", "Meeting") == "John Doe: Meeting"
    assert format_booking_info("John Doe", None) == "John Doe"
    assert format_booking_info("John Doe", "") == "John Doe"
    assert format_booking_info("", "Meeting") == "N/A: Meeting"  # Empty string is converted to N/A, title is still appended

@pytest.fixture
def mock_settings():
    with patch("cobot_cli.cli.settings") as mock_settings:
        mock_settings.access_token = "test-token"
        mock_settings.api_base = "https://api.cobot.me"
        mock_settings.space_id = "test-space"
        yield mock_settings

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {
        "data": [
            {
                "attributes": {
                    "from": "2024-02-15T09:00:00Z",
                    "to": "2024-02-15T10:00:00Z",
                    "name": "John Doe",
                    "title": "Meeting"
                },
                "relationships": {
                    "resource": {
                        "data": {
                            "id": "resource-1"
                        }
                    }
                }
            }
        ]
    }
    return mock

def test_fetch_bookings(mock_settings, mock_response):
    """Test fetching bookings from the API"""
    with patch("requests.get", return_value=mock_response) as mock_get:
        from_date = datetime.now(tzutc())
        to_date = from_date + timedelta(days=7)
        
        bookings = fetch_bookings(
            from_date=from_date,
            to_date=to_date,
            resource_id="resource-1"
        )
        
        mock_get.assert_called_once()
        assert len(bookings) == 1
        assert bookings[0]["attributes"]["name"] == "John Doe"
        assert bookings[0]["attributes"]["title"] == "Meeting"

def test_fetch_bookings_with_resource_filter(mock_settings, mock_response):
    """Test fetching bookings with resource filtering"""
    with patch("requests.get", return_value=mock_response) as mock_get:
        from_date = datetime.now(tzutc())
        to_date = from_date + timedelta(days=7)
        
        # Test with matching resource ID
        bookings = fetch_bookings(
            from_date=from_date,
            to_date=to_date,
            resource_id="resource-1"
        )
        assert len(bookings) == 1
        
        # Test with non-matching resource ID
        bookings = fetch_bookings(
            from_date=from_date,
            to_date=to_date,
            resource_id="resource-2"
        )
        assert len(bookings) == 0

@pytest.fixture
def sample_bookings():
    return [
        {
            "attributes": {
                "from": "2024-02-15T09:00:00Z",
                "to": "2024-02-15T10:00:00Z",
                "name": "John Doe",
                "title": "Meeting"
            },
            "relationships": {
                "resource": {
                    "data": {
                        "id": "resource-1"
                    }
                }
            }
        }
    ]

def test_create_bookings_table(sample_bookings):
    """Test creation of bookings table"""
    table = create_bookings_table(sample_bookings)
    assert table is not None
    # Note: Since rich.table.Table doesn't have a straightforward way to assert its contents,
    # we mainly verify that the table is created without errors
