# favorites.py
# ---------------------------------------------------
# Favorite Items Management
#
# This module provides the FavoriteManager class which handles favorite items
# using the provided ApiClient. It includes methods to retrieve, add, update,
# and delete favorite items.
# ---------------------------------------------------

from typing import Optional, Dict, Any

from .client import ApiClient
from .logging import async_log_event
from .validators import InputValidator


class FavoriteManager:
    """
    Manages favorite items using the underlying ApiClient.

    This class offers methods to interact with favorite items by retrieving,
    adding, updating, or deleting them via API requests.
    """

    def __init__(self, api_client: ApiClient) -> None:
        """
        Initializes the FavoriteManager with an instance of ApiClient.

        Args:
            api_client (ApiClient): The API client used for making requests.
        """
        self.api_client = api_client

    async def get_favorites(self, extra_headers: Optional[Dict[str, str]] = None) -> list:
        """
        Retrieves favorite items from the API.

        Returns:
            list: A list of favorite items if successful, otherwise an empty list.
        """
        headers = {"x-data-limit": "100", "x-data-offset": "0"}
        if extra_headers:
            headers.update(extra_headers)
        result = await self.api_client.request_data("GET", "/api/favorite", extra_headers=headers)
        if result is None:
            await async_log_event(
                "error", {"msg": "Failed to retrieve favorite items", "endpoint": "/api/favorite"}
            )
            return []
        # We gaan ervan uit dat result altijd een lijst is.
        await async_log_event(
            "success", {"msg": "Favorites retrieved successfully", "favorites_count": len(result)}
        )
        return result

    async def add_favorite(self, name: str, license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Adds a favorite item after validating the license plate.

        Args:
            name (str): The name for the favorite item.
            license_plate (str): The license plate associated with the favorite.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        normalized_plate = await InputValidator.validate_license_plate(license_plate)
        if normalized_plate is None:
            await async_log_event(
                "error", {"msg": "Invalid license plate provided", "license_plate": license_plate}
            )
            return None
        data = {"name": name, "license_plate": normalized_plate}
        result = await self.api_client.request_data("POST", "/api/favorite", data)
        # Controleer op de key "id" in plaats van "favorite_id"
        if result and result.get("id"):
            await async_log_event(
                "success",
                {"msg": "Favorite added successfully", "favorite_id": result.get("id")}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to add favorite", "data": data}
            )
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
            await async_log_event(
                "error", {"msg": "Invalid license plate provided for update", "license_plate": license_plate}
            )
            return None
        data = {"name": name, "license_plate": normalized_plate}
        result = await self.api_client.request_data("PATCH", f"/api/favorite/{favorite_id}", data)
        # Nu controleren we op de key "id" voor succes.
        if result and result.get("id"):
            await async_log_event(
                "success",
                {"msg": "Favorite updated successfully", "favorite_id": result.get("id")}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to update favorite", "favorite_id": favorite_id, "data": data}
            )
        return result

    async def delete_favorite(self, favorite_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a favorite item.

        Args:
            favorite_id (int): The ID of the favorite to delete.

        Returns:
            Optional[Dict[str, Any]]: The API response as a dictionary if successful, otherwise None.
        """
        result = await self.api_client.request_data("DELETE", f"/api/favorite/{favorite_id}")
        if result == {}:
            await async_log_event(
                "success",
                {"msg": "Favorite deleted successfully", "favorite_id": favorite_id}
            )
        else:
            await async_log_event(
                "error",
                {"msg": "Failed to delete favorite", "favorite_id": favorite_id}
            )
        return result
