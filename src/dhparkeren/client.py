# client.py
# ---------------------------------------------------
# API-Client
#
# This module implements the ApiClient class that handles API requests 
# with built-in retry logic and session management. It provides methods 
# for performing common actions such as retrieving account details, managing 
# favorites, and handling reservations.
# ---------------------------------------------------

import asyncio
import json
import random
from typing import Any, Dict, Optional
from aiohttp import ClientResponse, ClientError

from .session import SessionManager
from .logging import LOGGER, async_log_event
from .validators import TimeController, InputValidator


class ApiClient:
    """
    Performs API calls using the SessionManager and implements retry logic.

    This class handles communication with the API, including sending HTTP requests,
    managing sessions, handling retries, and logging errors. It supports operations
    such as retrieving account details, managing favorites, and handling reservations.
    """

    def __init__(self, session_manager: SessionManager, max_retries: int = 5) -> None:
        """
        Initializes the ApiClient with a session manager and maximum retries.

        Args:
            session_manager (SessionManager): The session manager to manage API sessions.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 5.
        """
        self.session_manager = session_manager
        self.max_retries = max_retries
        LOGGER.info("ApiClient initialized with max_retries=%d", self.max_retries)

    async def safe_json(self, response: ClientResponse) -> dict:
        """
        Attempts to decode a valid JSON response.
        If the response has status 204 (No Content), returns an empty dictionary.
        
        Args:
            response (ClientResponse): The HTTP response from the API.
            
        Returns:
            dict: The decoded JSON response, or an empty dict for status 204, 
                or an error dict if decoding fails.
        """
        if response.status == 204:
            return {}
        try:
            return await response.json()
        except json.decoder.JSONDecodeError as e:
            LOGGER.exception("JSON decode error: %s", e)
            return {"error": "Invalid JSON response", "status": response.status}

    async def request_data(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Performs an HTTP request with retry logic.

        This method sends an HTTP request using the given method and endpoint. It
        includes retry logic for handling failures and refreshing the session if a
        401 (Unauthorized) status is encountered.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PATCH', 'DELETE').
            endpoint (str): API endpoint to target.
            data (Optional[Dict[str, Any]], optional): JSON payload for the request.
            extra_headers (Optional[Dict[str, str]], optional): Additional headers.

        Returns:
            Optional[Dict[str, Any]]: The JSON response as a dictionary if successful, otherwise None.
        """
        attempt = 0
        retried_401 = False

        while attempt < self.max_retries:
            session_cookie = await self.session_manager.fetch_new_session()
            if not session_cookie:
                await async_log_event("error", {"msg": "No valid session cookie found", "endpoint": endpoint})
                return None

            url = f"{self.session_manager.config.base_url}{endpoint}"
            headers = self.session_manager.create_headers()
            if extra_headers:
                headers.update(extra_headers)
            cookies = {"session": session_cookie}

            LOGGER.debug("Attempt %d for %s request to %s with data: %s", attempt + 1, method, endpoint, data)
            try:
                async with self.session_manager.session.request(
                    method, url, headers=headers, cookies=cookies, json=data
                ) as response:
                    # If a 401 error occurs, try refreshing the session once.
                    if response.status == 401 and not retried_401:
                        retried_401 = True
                        await async_log_event(
                            "warning",
                            {"msg": "Session expired; refreshing...", "endpoint": endpoint, "attempt": attempt + 1},
                        )
                        self.session_manager.session_cookie = None  # Reset session
                        attempt += 1
                        continue

                    response_json = await self.safe_json(response)
                    
                    # Log the response status and endpoint.
                    await async_log_event(
                        "info",
                        {
                            "msg": "Received response",
                            "status": response.status,
                            "endpoint": endpoint,
                            "attempt": attempt + 1,
                        },
                    )
                    
                    # Treat status 200 and 204 as success.
                    if response.status in (200, 204):
                        await async_log_event(
                            "success",
                            {"msg": "Request succeeded", "endpoint": endpoint, "attempt": attempt + 1},
                        )
                    else:
                        await async_log_event(
                            "error",
                            {"msg": f"Request failed with status {response.status}", "endpoint": endpoint, "response": response_json},
                        )
                    return response_json

            except ClientError as e:
                LOGGER.exception("Client error for endpoint %s: %s", endpoint, e)
                await async_log_event(
                    "error",
                    {"msg": "Client error encountered", "endpoint": endpoint, "error": str(e), "attempt": attempt + 1},
                )
            attempt += 1
            backoff = random.uniform(2 ** attempt, 2 ** (attempt + 1))
            LOGGER.debug("Retrying in %.2f seconds (attempt %d)", backoff, attempt + 1)
            await asyncio.sleep(backoff)

        await async_log_event("error", {"msg": f"Max retries reached for {endpoint}", "endpoint": endpoint})
        return None

    async def has_overlapping_reservation(
        self, license_plate: str, start_time: str, end_time: str
    ) -> bool:
        """
        Checks if an overlapping reservation exists for the given license plate and time range.

        Args:
            license_plate (str): The license plate to check.
            start_time (str): The start time of the proposed reservation.
            end_time (str): The end time of the proposed reservation.

        Returns:
            bool: True if an overlapping reservation exists, False otherwise.
        """
        reservations_data = await self.get_reservations()
        if not reservations_data:
            LOGGER.debug("No reservations data found when checking for overlapping reservations for %s", license_plate)
            return False
        reservations = reservations_data.get("reservations", [])
        for res in reservations:
            if res.get("license_plate", "").upper() == license_plate:
                res_start = res.get("start_time")
                res_end = res.get("end_time")
                if (
                    res_start
                    and res_end
                    and TimeController.is_valid_time_range(start_time, end_time)
                    and TimeController.parse_iso_datetime(start_time)
                    < TimeController.parse_iso_datetime(res_end)
                    and TimeController.parse_iso_datetime(res_start)
                    < TimeController.parse_iso_datetime(end_time)
                ):
                    LOGGER.info("Found overlapping reservation for license plate %s: %s - %s", license_plate, res_start, res_end)
                    return True
        return False

    async def get_account(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves account information from the API.

        Returns:
            Optional[Dict[str, Any]]: Account details as a dictionary if successful, otherwise None.
        """
        result = await self.request_data("GET", "/api/account/0")
        if result and result.get("account"):
            await async_log_event("success", {"msg": "Account details retrieved", "account": result.get("account")})
        return result

    async def get_favorites(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves favorite items from the API.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing favorite items, or None if the request fails.
        """
        headers = {"x-data-limit": "100", "x-data-offset": "0"}
        result = await self.request_data("GET", "/api/favorite", extra_headers=headers)
        if result and result.get("favorites"):
            await async_log_event("success", {"msg": "Favorites retrieved", "favorites_count": len(result.get("favorites", []))})
        return result

    async def add_favorite(
        self, name: str, license_plate: str
    ) -> Optional[Dict[str, Any]]:
        """
        Adds a favorite item after validating the license plate.

        Args:
            name (str): The name for the favorite item.
            license_plate (str): The license plate to be associated with the favorite.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        normalized_plate = await InputValidator.validate_license_plate(license_plate)
        if normalized_plate is None:
            return None
        data = {"name": name, "license_plate": normalized_plate}
        result = await self.request_data("POST", "/api/favorite", data)
        if result and result.get("favorite_id"):
            await async_log_event("success", {"msg": "Favorite added", "favorite_id": result.get("favorite_id")})
        return result

    async def update_favorite(
        self, favorite_id: int, name: str, license_plate: str
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing favorite item after validating the license plate.

        Args:
            favorite_id (int): The ID of the favorite to update.
            name (str): The new name for the favorite.
            license_plate (str): The new license plate for the favorite.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        normalized_plate = await InputValidator.validate_license_plate(license_plate)
        if normalized_plate is None:
            return None
        data = {"name": name, "license_plate": normalized_plate}
        result = await self.request_data("PATCH", f"/api/favorite/{favorite_id}", data)
        if result and result.get("success"):
            await async_log_event("success", {"msg": "Favorite updated", "favorite_id": favorite_id})
        return result

    async def delete_favorite(self, favorite_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a favorite item.

        Args:
            favorite_id (int): The ID of the favorite to delete.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        result = await self.request_data("DELETE", f"/api/favorite/{favorite_id}")
        if result and result.get("success"):
            await async_log_event("success", {"msg": "Favorite deleted", "favorite_id": favorite_id})
        return result

    async def get_history(self, extra_headers: Optional[Dict[str, str]] = None) -> list:
        """
        Retrieves history from the API.

        Returns:
            list: A list of history entries if successful, otherwise an empty list.
        """
        headers = {"x-data-limit": "20", "x-data-offset": "0"}
        if extra_headers:
            headers.update(extra_headers)
        result = await self.request_data("GET", "/api/history", extra_headers=headers)
        if result is None:
            await async_log_event(
                "error", {"msg": "Failed to retrieve history", "endpoint": "/api/history"}
            )
            return []
        # Omdat we ervan uitgaan dat de API altijd een lijst retourneert:
        await async_log_event(
            "success", {"msg": "History retrieved", "history_entries": len(result)}
        )
        return result

    async def get_reservations(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves reservations from the API.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing reservation details, or None if the request fails.
        """
        result = await self.request_data("GET", "/api/reservation")
        if result:
            await async_log_event("success", {"msg": "Reservations retrieved", "reservations_count": len(result.get("reservations", []))})
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

        Args:
            name (str): The name associated with the reservation.
            license_plate (str): The license plate to validate.
            start_time (str): The start time of the reservation in ISO format.
            end_time (str): The end time of the reservation in ISO format.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful,
            otherwise None.
        """
        normalized_plate = await InputValidator.validate_license_plate(license_plate)
        if normalized_plate is None:
            return None

        times = await InputValidator.validate_reservation_times(start_time, end_time)
        if times is None:
            return None
        start_time_valid, end_time_valid = times

        if await self.has_overlapping_reservation(normalized_plate, start_time_valid, end_time_valid):
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
        result = await self.request_data("POST", "/api/reservation", data)
        if result and result.get("reservation_id"):
            await async_log_event("success", {"msg": "Reservation added", "reservation_id": result.get("reservation_id")})
        return result

    async def update_reservation(
        self, reservation_id: int, end_time: str
    ) -> Optional[Dict[str, Any]]:
        """
        Updates a reservation's end time after verifying the new end time is valid.

        Args:
            reservation_id (int): The ID of the reservation to update.
            end_time (str): The new end time in ISO format.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful,
            otherwise None.
        """
        reservation = await self.request_data("GET", f"/api/reservation/{reservation_id}")
        if not reservation:
            await async_log_event(
                "error", {"msg": "Reservation not found", "reservation_id": reservation_id}
            )
            return None
        current_start_time = reservation.get("start_time")
        if current_start_time is None:
            await async_log_event(
                "error",
                {"msg": "Reservation start time not found", "reservation_id": reservation_id},
            )
            return None
        new_end_time_valid = await InputValidator.validate_new_end_time(current_start_time, end_time)
        if new_end_time_valid is None:
            return None

        result = await self.request_data(
            "PATCH", f"/api/reservation/{reservation_id}", {"end_time": new_end_time_valid}
        )
        if result and result.get("success"):
            await async_log_event("success", {"msg": "Reservation updated", "reservation_id": reservation_id})
        return result

    async def delete_reservation(self, reservation_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a reservation.

        Args:
            reservation_id (int): The ID of the reservation to delete.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful,
            otherwise None.
        """
        result = await self.request_data("DELETE", f"/api/reservation/{reservation_id}")
        if result and result.get("success"):
            await async_log_event("success", {"msg": "Reservation deleted", "reservation_id": reservation_id})
        return result
