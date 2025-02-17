# reservations.py
# ---------------------------------------------------
# Reservations Management
#
# This module provides the ReservationManager class which handles reservation
# operations using the provided ApiClient. It includes methods to retrieve,
# add, update, and delete reservations.
# ---------------------------------------------------

from typing import Optional, Dict, Any

from .client import ApiClient
from .validators import InputValidator
from .logging import async_log_event


class ReservationManager:
    """
    Manages reservations using the underlying ApiClient.

    This class provides methods for managing reservations, including retrieval,
    creation, updating, and deletion of reservations.
    """

    def __init__(self, api_client: ApiClient) -> None:
        """
        Initializes the ReservationManager with an instance of ApiClient.

        Args:
            api_client (ApiClient): The API client used for making requests.
        """
        self.api_client = api_client

    async def get_reservations(self) -> list:
        """
        Retrieves reservations from the API.

        Returns:
            list: A list of reservation details if successful, otherwise an empty list.
        """
        result = await self.api_client.get_reservations()
        if result is None:
            await async_log_event(
                "error", {"msg": "Failed to retrieve reservations", "endpoint": "/api/reservation"}
            )
            return []
        await async_log_event(
            "success", {"msg": "Reservations retrieved successfully", "reservations_count": len(result)}
        )
        return result

    async def add_reservation(
        self,
        name: str,
        license_plate: str,
        start_time: str,
        end_time: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Adds a reservation after validating the license plate and reservation times.

        This method validates the provided license plate and reservation times. If the
        validations pass and there is no overlapping reservation, it sends a request
        to create the reservation.

        Args:
            name (str): The name associated with the reservation.
            license_plate (str): The license plate to validate.
            start_time (str): The start time of the reservation in ISO format.
            end_time (str): The end time of the reservation in ISO format.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        normalized_plate = await InputValidator.validate_license_plate(license_plate)
        if normalized_plate is None:
            await async_log_event(
                "error",
                {"msg": "Invalid license plate provided", "license_plate": license_plate}
            )
            return None

        times = await InputValidator.validate_reservation_times(start_time, end_time)
        if times is None:
            await async_log_event(
                "error",
                {"msg": "Invalid reservation times provided", "start_time": start_time, "end_time": end_time}
            )
            return None
        start_time_valid, end_time_valid = times

        if await self.api_client.has_overlapping_reservation(normalized_plate, start_time_valid, end_time_valid):
            await async_log_event(
                "error",
                {
                    "msg": "Overlapping reservation exists for this license plate",
                    "license_plate": normalized_plate,
                    "start_time": start_time_valid,
                    "end_time": end_time_valid,
                },
            )
            return None

        data = {
            "name": name,
            "license_plate": normalized_plate,
            "start_time": start_time_valid,
            "end_time": end_time_valid,
        }
        result = await self.api_client.request_data("POST", "/api/reservation", data)
        if result and result.get("reservation_id"):
            await async_log_event(
                "success",
                {"msg": "Reservation added successfully", "reservation_id": result.get("reservation_id")}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to add reservation", "data": data}
            )
        return result

    async def update_reservation(self, reservation_id: int, end_time: str) -> Optional[Dict[str, Any]]:
        """
        Updates a reservation by verifying that the new end time is after the existing start time.

        This method retrieves the current reservation data, validates the new end time,
        and sends a PATCH request to update the reservation if the new end time is valid.

        Args:
            reservation_id (int): The ID of the reservation to update.
            end_time (str): The new end time for the reservation in ISO format.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        reservation = await self.api_client.request_data("GET", f"/api/reservation/{reservation_id}")
        if not reservation:
            await async_log_event(
                "error",
                {"msg": "Reservation not found", "reservation_id": reservation_id}
            )
            return None

        current_start_time = reservation.get("start_time")
        if current_start_time is None:
            await async_log_event(
                "error",
                {"msg": "Reservation start time not found", "reservation_id": reservation_id}
            )
            return None

        new_end_time_valid = await InputValidator.validate_new_end_time(current_start_time, end_time)
        if new_end_time_valid is None:
            await async_log_event(
                "error",
                {"msg": "Invalid new end time", "current_start_time": current_start_time, "new_end_time": end_time}
            )
            return None

        result = await self.api_client.request_data(
            "PATCH", f"/api/reservation/{reservation_id}", {"end_time": new_end_time_valid}
        )
        # Controleer op "success" of op "id", omdat de API geen "success" key retourneert
        if result and (result.get("success") or result.get("id")):
            await async_log_event(
                "success",
                {"msg": "Reservation updated successfully", "reservation_id": reservation_id}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to update reservation", "reservation_id": reservation_id, "new_end_time": new_end_time_valid}
            )
        return result

    async def delete_reservation(self, reservation_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a reservation.

        Args:
            reservation_id (int): The ID of the reservation to delete.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        result = await self.api_client.request_data("DELETE", f"/api/reservation/{reservation_id}")
        # Beschouw een lege dictionary als een succesvolle delete (204 No Content)
        if result == {} or (result and result.get("id")):
            await async_log_event(
                "success",
                {"msg": "Reservation deleted successfully", "reservation_id": reservation_id}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to delete reservation", "reservation_id": reservation_id}
            )
        return result
