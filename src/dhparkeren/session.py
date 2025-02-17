# session.py
# ---------------------------------------------------
# Session Management (SessionManager)
#
# This module provides the SessionManager class for handling HTTP sessions
# and authentication using asynchronous context management. It includes methods
# for creating standard HTTP headers, fetching a new session, and closing the session.
# ---------------------------------------------------

import asyncio
import base64
from typing import Dict, Optional
import aiohttp

from .config import Secrets, Config
from .logging import LOGGER, async_log_event


class SessionManager:
    """
    Manages the HTTP session and authentication with asynchronous context management.

    This class handles the creation and maintenance of an HTTP session, including
    fetching new session cookies using basic authentication and providing standard
    headers for JSON communication.
    """

    def __init__(
        self, secrets: Secrets, config: Config, session_timeout: int = 30
    ) -> None:
        """
        Initializes the SessionManager with provided secrets, configuration, and session timeout.

        Args:
            secrets (Secrets): The secrets containing username and password.
            config (Config): The configuration instance containing the base URL and log level.
            session_timeout (int, optional): The timeout for the HTTP session in seconds. Defaults to 30.
        """
        self.secrets = secrets
        self.config = config
        self.session_cookie: Optional[str] = None
        self.session_timeout = session_timeout
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=10),
            timeout=aiohttp.ClientTimeout(total=self.session_timeout),
        )
        self._session_lock = asyncio.Lock()
        LOGGER.info("SessionManager initialized with session timeout %d seconds", self.session_timeout)

    async def __aenter__(self) -> "SessionManager":
        """
        Asynchronously enters the runtime context related to this object.

        Returns:
            SessionManager: The current instance.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Asynchronously exits the runtime context and closes the HTTP session.

        Args:
            exc_type: The exception type.
            exc: The exception instance.
            tb: The traceback.
        """
        await self.close()
        await async_log_event("session", {"msg": "HTTP session closed"})

    async def close(self) -> None:
        """
        Closes the HTTP session.
        """
        await self.session.close()
        LOGGER.debug("HTTP session closed.")

    def create_headers(self) -> Dict[str, str]:
        """
        Returns standard HTTP headers for JSON communication.

        Returns:
            Dict[str, str]: A dictionary containing standard headers.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "angular",
        }
        LOGGER.debug("Created headers: %s", headers)
        return headers

    async def fetch_new_session(self) -> Optional[str]:
        """
        Fetches a new session cookie if there is no valid session available.

        This method acquires a lock to ensure only one session request is made at a time.
        It uses basic authentication to request a new session and returns the session cookie.

        Returns:
            Optional[str]: The new session cookie if successful, otherwise None.
        """
        async with self._session_lock:
            if self.session_cookie:
                await async_log_event(
                    "session",
                    {"msg": "Reusing existing session", "cookie": self.session_cookie},
                )
                LOGGER.debug("Reusing existing session cookie: %s", self.session_cookie)
                return self.session_cookie

            await async_log_event("session", {"msg": "Requesting new session..."})
            credentials = f"{self.secrets.username}:{self.secrets.password}".encode()
            auth = "Basic " + base64.b64encode(credentials).decode()
            headers = self.create_headers()
            headers["Authorization"] = auth

            url = f"{self.config.base_url}/api/session"
            LOGGER.debug("Fetching new session from URL: %s with headers: %s", url, headers)
            try:
                async with self.session.get(url, headers=headers) as response:
                    if response.status not in range(200, 300):
                        await async_log_event(
                            "error",
                            {
                                "msg": "Session request failed",
                                "status": response.status,
                                "url": url,
                            },
                        )
                        LOGGER.error("Session request failed with status %d for URL: %s", response.status, url)
                        return None

                    # Retrieve the session cookie value from the response
                    cookie = response.cookies.get("session")
                    if cookie is not None:
                        self.session_cookie = cookie.value
                        LOGGER.debug("Received new session cookie: %s", self.session_cookie)
                    else:
                        self.session_cookie = None
                        LOGGER.error("No session cookie found in response from URL: %s", url)
                    await async_log_event(
                        "session",
                        {"msg": "New session acquired", "cookie": self.session_cookie, "url": url},
                    )
                    return self.session_cookie
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                LOGGER.exception("Error fetching new session: %s", e)
                await async_log_event(
                    "error",
                    {"msg": "Exception occurred while fetching new session", "error": str(e), "url": url},
                )
                return None
