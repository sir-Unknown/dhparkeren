# logging.py
# ---------------------------------------------------
# Logging Configuration & Async Logging Helper
#
# This module provides an asynchronous logging helper function for logging events.
#
# IMPORTANT:
#   This library does not configure logging (e.g., by calling logging.basicConfig).
#   It is the responsibility of the end-user (or the application that imports this
#   library) to set up the desired logging configuration. For example:
#
#       import logging
#
#       logging.basicConfig(
#           level=logging.DEBUG,  # Set the desired log level
#           format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#       )
#
#   This approach allows the end-user full control over logging behavior without
#   imposing a default configuration that might conflict with their application's setup.
#
# ---------------------------------------------------

import json
import logging
from typing import Any, Dict

# Set up a global logger for the module.
LOGGER = logging.getLogger(__name__)

async def async_log_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Asynchronously logs an event with its details.

    Args:
        event_type (str): The type of event (e.g., 'error', 'info', 'warning', 'debug', 'success').
        details (Dict[str, Any]): A dictionary containing event-specific details.
    """
    log_data = {"event": event_type, "details": details}
    # Route the log message to the appropriate logging level.
    event_type_lower = event_type.lower()
    if event_type_lower == "error":
        LOGGER.error(json.dumps(log_data))
    elif event_type_lower == "warning":
        LOGGER.warning(json.dumps(log_data))
    elif event_type_lower == "debug":
        LOGGER.debug(json.dumps(log_data))
    elif event_type_lower == "success":
        # For 'success', we log it as INFO level.
        LOGGER.info(json.dumps(log_data))
    else:
        # Default to INFO level if event type is unrecognized.
        LOGGER.info(json.dumps(log_data))
