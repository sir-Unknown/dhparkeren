# config.py
# ---------------------------------------------------
# Configuration Classes
#
# This module defines classes for storing configuration settings and secrets.
# The Secrets class holds login credentials, while the Config class manages
# configuration variables like the base URL.
# ---------------------------------------------------

class Secrets:
    """
    Stores login credentials.

    Attributes:
        username (str): The username used for authentication.
        password (str): The password used for authentication.
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes the Secrets instance with a username and password.

        Args:
            username (str): The username for login.
            password (str): The password for login.
        """
        self.username = username
        self.password = password


class Config:
    """
    Stores configuration variables.

    Attributes:
        base_url (str): The base URL for API requests.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initializes the Config instance with a base URL.

        Args:
            base_url (str): The base URL for API requests.
        """
        self.base_url = base_url
