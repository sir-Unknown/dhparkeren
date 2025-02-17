# test_validators.py
import pytest
from datetime import datetime, timedelta

from dhparkeren.validators import InputValidator, TimeController

@pytest.mark.asyncio
async def test_validate_license_plate_valid():
    valid_plate = "AB123CD"
    normalized = await InputValidator.validate_license_plate(valid_plate)
    assert normalized == "AB123CD"

@pytest.mark.asyncio
async def test_validate_license_plate_invalid():
    invalid_plate = "invalid plate!"
    normalized = await InputValidator.validate_license_plate(invalid_plate)
    assert normalized is None

def test_parse_iso_datetime_valid():
    time_str = "2025-02-16T12:30:45"
    dt = TimeController.parse_iso_datetime(time_str)
    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.hour == 12

def test_parse_iso_datetime_invalid():
    time_str = "not a date"
    dt = TimeController.parse_iso_datetime(time_str)
    assert dt is None

def test_is_valid_time_range_valid():
    start_time = "2025-02-16T12:30:45"
    end_time = "2025-02-16T13:30:45"
    assert TimeController.is_valid_time_range(start_time, end_time)

def test_is_valid_time_range_invalid():
    start_time = "2025-02-16T14:30:45"
    end_time = "2025-02-16T13:30:45"
    assert not TimeController.is_valid_time_range(start_time, end_time)

@pytest.mark.asyncio
async def test_validate_reservation_times_success():
    now = datetime.now() + timedelta(hours=1)
    later = now + timedelta(hours=1)
    start_str = now.isoformat()
    end_str = later.isoformat()
    result = await InputValidator.validate_reservation_times(start_str, end_str)
    assert result == (start_str, end_str)

@pytest.mark.asyncio
async def test_validate_reservation_times_failure_due_to_format():
    start_str = "2025/02/16 12:30:45"  # Incorrect format
    end_str = "2025-02-16T13:30:45"
    result = await InputValidator.validate_reservation_times(start_str, end_str)
    assert result is None

@pytest.mark.asyncio
async def test_validate_reservation_times_failure_due_to_past_start():
    past_time = datetime.now() - timedelta(hours=1)
    future_time = datetime.now() + timedelta(hours=1)
    start_str = past_time.isoformat()
    end_str = future_time.isoformat()
    result = await InputValidator.validate_reservation_times(start_str, end_str)
    assert result is None
