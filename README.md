
# The Hague Visitor Parking API

The Hague Visitor Parking API is a Python library designed to interact with The Hague Visitor Parking system. It provides a collection of tools and classes to manage API calls, sessions, reservations, favorites, and input validation, while also offering comprehensive logging and error handling.

> **Disclaimer:** This module has been developed specifically to be used within [Home Assistant](https://www.home-assistant.io/). It is designed to integrate with Home Assistant environments, and while it may be adaptable for other uses, its primary focus is Home Assistant integration.

## Features

- **API Client**: Performs API calls with built-in retry logic, error handling, and logging.
- **Session Management**: Manages HTTP sessions and authentication using asynchronous context management.
- **Account Management**: Retrieves account information from the API.
- **Reservation Management**: Handles creation, updating, and deletion of parking reservations.
- **Favorite Management**: Manages favorite parking spots or items.
- **Input Validation**: Validates and normalizes inputs such as license plates and ISO 8601 timestamps.
- **Logging**: Provides asynchronous logging for events and errors.
- **Error Handling**: A dedicated document ([ERROR_MESSAGE.md](ERROR_MESSAGE.md)) maps API error codes to human-readable messages.

## Installation

You can install the package via pip (if published) or clone the repository and install it manually:

```bash
pip install dhparkeren
```

Or install from source:

```bash
git clone https://github.com/sir-Unknown/dhparkeren.git
cd dhparkeren
pip install .
```

## Usage

Below is an example of how to use the library in your project:

```python
import asyncio
from dhparkeren import (
    ApiClient,
    AccountManager,
    ReservationManager,
    FavoriteManager,
    SessionManager,
    Config,
    Secrets,
    init_logging,
)

async def main():
    # Setup configuration and secrets
    config = Config(base_url="https://parkerendenhaag.denhaag.nl/", log_level="DEBUG")
    secrets = Secrets(username="your_username", password="your_password")
    
    # Initialize logging
    init_logging(config)
    
    # Create a session manager with asynchronous context management
    async with SessionManager(secrets, config) as session_manager:
        # Initialize the API client using the session manager
        api_client = ApiClient(session_manager)
        
        # Create manager instances
        account_manager = AccountManager(api_client)
        reservation_manager = ReservationManager(api_client)
        favorite_manager = FavoriteManager(api_client)
        
        # Retrieve account details
        account_info = await account_manager.get_account()
        print("Account Info:", account_info)
        
        # Add a new reservation
        reservation = await reservation_manager.add_reservation(
            name="Test Reservation",
            license_plate="ABC123",
            start_time="2025-03-01T10:00:00",
            end_time="2025-03-01T12:00:00"
        )
        print("Reservation:", reservation)
        
        # Add a favorite item
        favorite = await favorite_manager.add_favorite(
            name="Home",
            license_plate="ABC123"
        )
        print("Favorite:", favorite)

if __name__ == "__main__":
    asyncio.run(main())
```

A more detailed example showcasing every function can be found in [/tests/test_live.py](/tests/test_live.py).

## Error Messages

For a complete list of error codes and their corresponding messages, please refer to the [ERROR_MESSAGE.md](ERROR_MESSAGE.md) file. This document provides a mapping of API error codes to human-readable messages and includes a code example demonstrating how to use the error message mapping in your code.

## Documentation

The source code is extensively documented with clear, comprehensive docstrings. Each module (such as `client.py`, `session.py`, `validators.py`, etc.) provides detailed descriptions of its functionality, making it easy to understand and extend the library.

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or improvements, please fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Version

Current version: **0.1.0**
