# account.py
# ---------------------------------------------------
# Account management module.
#
# This module provides an AccountManager class which is responsible for 
# handling account-related actions using the provided ApiClient. It includes 
# methods for retrieving account information and logging errors if the account 
# data cannot be retrieved.
# ---------------------------------------------------

from typing import Optional, Dict, Any

from .client import ApiClient
from .logging import async_log_event


class AccountManager:
    """
    Manages account-related actions using the underlying ApiClient.

    This class serves as an interface to interact with account data. It 
    encapsulates the logic for sending requests to retrieve account details and 
    handling errors appropriately.

    Attributes:
        api_client (ApiClient): An instance of ApiClient used to make API requests.
    """

    def __init__(self, api_client: ApiClient) -> None:
        """
        Initializes the AccountManager with an instance of ApiClient.

        Args:
            api_client (ApiClient): The API client used to send requests.
        """
        self.api_client = api_client

    async def get_account(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves account information from the API.

        This asynchronous method sends a GET request to the account endpoint.
        If the response is None, it logs an error event asynchronously. Otherwise,
        it logs a success message with the retrieved account data.

        Returns:
            Optional[Dict[str, Any]]: The account information as a dictionary if available,
            otherwise None.
        """
        response = await self.api_client.request_data("GET", "/api/account/0")
        if response is None:
            await async_log_event(
                "error", {"msg": "Account information could not be retrieved", "endpoint": "/api/account/0"}
            )
        else:
            # Directly use the response as the account data since the API returns a JSON object
            await async_log_event(
                "success", {"msg": "Account information retrieved successfully", "account_summary": response}
            )
        return response
