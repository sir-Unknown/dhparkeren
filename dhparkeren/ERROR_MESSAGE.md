# Error Messages

This document provides an overview of the error messages returned by the API. Each error code is mapped to a clear, human-readable message. Users of the library can refer to this documentation to better understand the meaning of each error code.

## Error Code Mapping

The following error codes and messages are provided by the API:

- **PV00019**: License plate not found
- **PV00020**: You have an invalid permit type
- **PV00046**: You have no valid parking permit
- **PV00051**: Maximum reservations reached
- **PV00052**: Insufficient balance
- **PV00063**: This license plate is already reserved at this time
- **PV00071**: Upstream server not reachable
- **PV00072**: No parking in selected zone
- **PV00074**: Invalid start time
- **PV00075**: Invalid end time
- **PV00076**: No paid parking at this time
- **PV00077**: No valid session found
- **PV00097**: Incorrect license plate
- **PV000111**: Incorrect credentials supplied
- **dit_kenteken_is_reeds_aangemeld**: License plate is already registered
- **account_already_linked**: This account is already linked
- **ilp**: Enter the license plate number without punctuation marks please
- **npvs_offline**: The parking registry is not available at this time.

If an error code is received that is not listed here, the default message is:

> "Your data has not been saved"

## Example Usage

Below is an example of how you can use the error code mapping in your code to display a clear message to your users:

```python
# error_messages.py

ERROR_MESSAGES = {
    "PV00019": "License plate not found",
    "PV00020": "You have an invalid permit type",
    "PV00046": "You have no valid parking permit",
    "PV00051": "Maximum reservations reached",
    "PV00052": "Insufficient balance",
    "PV00063": "This license plate is already reserved at this time",
    "PV00071": "Upstream server not reachable",
    "PV00072": "No parking in selected zone",
    "PV00074": "Invalid start time",
    "PV00075": "Invalid end time",
    "PV00076": "No paid parking at this time",
    "PV00077": "No valid session found",
    "PV00097": "Incorrect license plate",
    "PV000111": "Incorrect credentials supplied",
    "dit_kenteken_is_reeds_aangemeld": "License plate is already registered",
    "account_already_linked": "This account is already linked",
    "ilp": "Enter the license plate number without punctuation marks please",
    "npvs_offline": "The parking registry is not available at this time.",
}

def get_error_message(code: str) -> str:
    """
    Returns the corresponding error message for a given error code.

    Args:
        code (str): The error code returned by the API.

    Returns:
        str: The error message if the code is found, or a default message.
    """
    return ERROR_MESSAGES.get(code, "Your data has not been saved")


# Example usage:
if __name__ == "__main__":
    # Simulate receiving an error code from the API.
    error_code = "PV00020"
    print(f"Error [{error_code}]: {get_error_message(error_code)}")
```

## Summary

This mapping is intended to provide clarity for API error codes. By using the helper function `get_error_message`, users can easily convert error codes into descriptive messages, improving the overall user experience.
