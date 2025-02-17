# The Hague Visitor Parking API (dhparkeren)

## Overview

The `dhparkeren` project is a Python package designed to interact with The Hague's visitor parking system. It provides an API client, session management, account handling, reservation management, and other essential features to streamline communication with the official parking system. This package is particularly useful for integrating visitor parking functionalities within automation environments like Home Assistant.

## Key Features

- **API Client:** Perform requests to The Hague's parking system with error handling and retry logic.
- **Session Management:** Maintain and authenticate user sessions asynchronously.
- **Account Management:** Retrieve and manage user account details.
- **Reservation Handling:** Create, update, and delete visitor parking reservations.
- **Favorite Management:** Store and manage frequently used license plates and parking spots.
- **Validation & Logging:** Built-in input validation and asynchronous logging.
- **Error Handling:** A structured mapping of API error codes to user-friendly messages (see [`ERROR_MESSAGE.md`](dhparkeren/ERROR_MESSAGE.md)).

## Usage
For a more detailed breakdown of the package's architecture and functionality, refer to [`/dhparkeren/README.md`](dhparkeren/README.md).

## Contributing

Contributions to the project are welcome! If you find issues or have ideas for improvements, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See [`LICENSE`](dhparkeren/LICENSE) for details.

## Version

Current version: **0.1.0**

