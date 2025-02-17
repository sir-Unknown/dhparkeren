# validators.py
# ---------------------------------------------------
# Time Utilities (TimeController)
#
# This module provides utilities for parsing and validating ISO 8601 timestamps,
# normalizing and validating license plates, and centralizing input validation
# to avoid duplicate logging.
# ---------------------------------------------------

from datetime import datetime
import re
from typing import Optional, Tuple

from .logging import async_log_event, LOGGER


class TimeController:
    """
    Utilities for parsing and validating ISO 8601 timestamps.
    """

    @staticmethod
    def parse_iso_datetime(time_str: str) -> Optional[datetime]:
        """
        Parses an ISO 8601 formatted string into a datetime object.

        Args:
            time_str (str): The time string in ISO 8601 format.

        Returns:
            Optional[datetime]: A datetime object if parsing is successful, otherwise None.
        """
        try:
            dt = datetime.fromisoformat(time_str)
            LOGGER.debug("Parsed ISO datetime '%s' to %s", time_str, dt)
            return dt
        except ValueError:
            LOGGER.error("Failed to parse ISO datetime: '%s'", time_str)
            return None

    @staticmethod
    def is_valid_time_range(start_time: str, end_time: str) -> bool:
        """
        Checks if the end time is after the start time.

        Args:
            start_time (str): The start time in ISO 8601 format.
            end_time (str): The end time in ISO 8601 format.

        Returns:
            bool: True if the end time is later than the start time, otherwise False.
        """
        start_dt = TimeController.parse_iso_datetime(start_time)
        end_dt = TimeController.parse_iso_datetime(end_time)
        if start_dt is None or end_dt is None:
            LOGGER.debug("One or both timestamps are invalid: start_time='%s', end_time='%s'", start_time, end_time)
            return False
        valid = end_dt > start_dt
        LOGGER.debug("Time range valid check: start_time='%s', end_time='%s' -> %s", start_time, end_time, valid)
        return valid


# ---------------------------------------------------
# License Plate Utilities (LicensePlateController)
# ---------------------------------------------------

class LicensePlateController:
    """
    Provides methods to normalize and validate license plates.
    """

    @staticmethod
    def normalize(plate: str) -> str:
        """
        Normalizes a license plate by removing dashes, underscores, and spaces, then converting to uppercase.

        Args:
            plate (str): The original license plate string.

        Returns:
            str: The normalized license plate.
        """
        normalized = re.sub(r"[-_\s]", "", plate).upper()
        LOGGER.debug("Normalized license plate '%s' to '%s'", plate, normalized)
        return normalized

    @staticmethod
    def is_valid(plate: str) -> bool:
        """
        Validates a normalized license plate against a regex pattern.

        Args:
            plate (str): The normalized license plate string.

        Returns:
            bool: True if the license plate is valid, otherwise False.
        """
        valid = re.fullmatch(r"^[A-Z0-9]{1,12}$", plate) is not None
        LOGGER.debug("License plate '%s' validity: %s", plate, valid)
        return valid


# ---------------------------------------------------
# Input Validation (InputValidator)
# ---------------------------------------------------

class InputValidator:
    """
    Centralizes input validation checks and logging to prevent duplicate logging.

    This class provides methods to validate license plates and reservation times.
    """
    ISO8601_REGEX = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$"
    )

    @staticmethod
    def is_iso8601(time_str: str) -> bool:
        """
        Checks if a given time string matches the ISO 8601 format.

        Args:
            time_str (str): The time string to check.

        Returns:
            bool: True if the string is in ISO 8601 format, otherwise False.
        """
        match = bool(InputValidator.ISO8601_REGEX.fullmatch(time_str))
        LOGGER.debug("Time string '%s' is ISO 8601: %s", time_str, match)
        return match

    @staticmethod
    async def validate_license_plate(license_plate: str) -> Optional[str]:
        """
        Validates and normalizes a license plate.

        Args:
            license_plate (str): The license plate string to validate.

        Returns:
            Optional[str]: The normalized license plate if valid, otherwise None.
        """
        normalized_plate = LicensePlateController.normalize(license_plate)
        if not LicensePlateController.is_valid(normalized_plate):
            await async_log_event(
                "error",
                {"msg": "Invalid license plate format", "license_plate": license_plate},
            )
            return None
        await async_log_event(
            "debug",
            {"msg": "License plate validated successfully", "normalized_plate": normalized_plate},
        )
        return normalized_plate

    @staticmethod
    async def validate_reservation_times(
        start_time: str, end_time: str
    ) -> Optional[Tuple[str, str]]:
        """
        Validates the reservation times ensuring they are in ISO 8601 format, the time range is valid,
        and the start time is in the future.

        Args:
            start_time (str): The proposed start time in ISO 8601 format.
            end_time (str): The proposed end time in ISO 8601 format.

        Returns:
            Optional[Tuple[str, str]]: A tuple of the validated start and end times if valid, otherwise None.
        """
        if not InputValidator.is_iso8601(start_time):
            await async_log_event(
                "error",
                {"msg": "Start time is not in ISO 8601 format", "start_time": start_time},
            )
            return None
        if not InputValidator.is_iso8601(end_time):
            await async_log_event(
                "error",
                {"msg": "End time is not in ISO 8601 format", "end_time": end_time},
            )
            return None

        if not TimeController.is_valid_time_range(start_time, end_time):
            await async_log_event(
                "error",
                {
                    "msg": "Invalid time range: end_time must be after start_time",
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )
            return None

        now = datetime.now()
        start_dt = TimeController.parse_iso_datetime(start_time)
        if start_dt is None:
            await async_log_event(
                "error", {"msg": "Invalid start_time", "start_time": start_time}
            )
            return None
        if start_dt < now:
            await async_log_event(
                "error",
                {"msg": "Start time may not lie in the past", "start_time": start_time},
            )
            return None

        await async_log_event(
            "debug",
            {"msg": "Reservation times validated successfully", "start_time": start_time, "end_time": end_time},
        )
        return start_time, end_time

    @staticmethod
    async def validate_new_end_time(
        current_start_time: str, new_end_time: str
    ) -> Optional[str]:
        """
        Validates that the new end time is in ISO 8601 format and is later than the current start time.

        Args:
            current_start_time (str): The current start time in ISO 8601 format.
            new_end_time (str): The proposed new end time in ISO 8601 format.

        Returns:
            Optional[str]: The new end time if valid, otherwise None.
        """
        if not InputValidator.is_iso8601(new_end_time):
            await async_log_event(
                "error",
                {
                    "msg": "New end time is not in ISO 8601 format",
                    "new_end_time": new_end_time,
                },
            )
            return None

        if not TimeController.is_valid_time_range(current_start_time, new_end_time):
            await async_log_event(
                "error",
                {
                    "msg": "Invalid time range: new end_time must be after start_time",
                    "start_time": current_start_time,
                    "new_end_time": new_end_time,
                },
            )
            return None

        await async_log_event(
            "debug",
            {"msg": "New end time validated successfully", "new_end_time": new_end_time, "current_start_time": current_start_time},
        )
        return new_end_time
