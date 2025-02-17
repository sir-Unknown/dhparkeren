"""""
# test_live.py

This script interacts with the DHParkeren API to perform various operations:
- Retrieve account information
- Fetch reservation history
- Manage favorites (retrieve, add, update, delete)
- Manage reservations (retrieve, add, update, delete)

## Usage:
Run the script with the desired arguments to perform specific operations:

```sh
python test_live.py --account --history --favorites --reservations
```

To execute the script, ensure you have set the required environment variables:

```sh
export DHPARKEREN_USERNAME="your_username"
export DHPARKEREN_PASSWORD="your_password"
```

Alternatively, on Windows (PowerShell):

```powershell
$env:DHPARKEREN_USERNAME="your_username"
$env:DHPARKEREN_PASSWORD="your_password"
```
"""

import os
import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from dhparkeren.config import Config, Secrets
from dhparkeren.session import SessionManager
from dhparkeren.client import ApiClient
from dhparkeren.account import AccountManager
from dhparkeren.favorites import FavoriteManager
from dhparkeren.reservations import ReservationManager

async def main(fetch_account: bool, fetch_history: bool, fetch_favorites: bool, fetch_reservations: bool):
    """
    Main function to handle API interactions based on provided arguments.
    
    Parameters:
    - fetch_account (bool): Retrieve account details.
    - fetch_history (bool): Fetch reservation history.
    - fetch_favorites (bool): Manage favorites (retrieve, add, update, delete).
    - fetch_reservations (bool): Manage reservations (retrieve, add, update, delete).
    """
    config = Config(base_url="https://parkerendenhaag.denhaag.nl")
    
    # Retrieve login credentials from environment variables
    username = os.environ.get("DHPARKEREN_USERNAME")
    password = os.environ.get("DHPARKEREN_PASSWORD")
    
    if not username or not password:
        print("Error: Environment variables DHPARKEREN_USERNAME and DHPARKEREN_PASSWORD must be set.")
        return
    
    secrets = Secrets(username=username, password=password)
    
    async with SessionManager(secrets, config) as session_manager:
        api_client = ApiClient(session_manager)
        
        if fetch_account:
            account_manager = AccountManager(api_client)
            print("Retrieving account details...")
            account_data = await account_manager.get_account()
            print("Account details:")
            print(account_data)
        
        if fetch_history:
            print("Fetching reservation history...")
            history = await api_client.get_history()
            print("Reservation history:")
            print(history)
        
        if fetch_favorites:
            favorite_manager = FavoriteManager(api_client)
            print("Retrieving current favorites...")
            favorites = await favorite_manager.get_favorites()
            print("Favorites:")
            print(favorites)
            
            print("\nAdding a new favorite item...")
            add_fav_result = await favorite_manager.add_favorite("Test Favorite", "TEST123")
            print("Addition result:")
            print(add_fav_result)
            
            favorite_id = add_fav_result.get("id") if add_fav_result else None
            if not favorite_id:
                print("Failed to add favorite. Exiting.")
                return
            
            await asyncio.sleep(5)
            print("\nUpdating favorite item...")
            update_fav_result = await favorite_manager.update_favorite(favorite_id, "Updated Favorite", "TEST123")
            print("Update result:")
            print(update_fav_result)
            
            await asyncio.sleep(5)
            print("\nDeleting favorite item...")
            delete_fav_result = await favorite_manager.delete_favorite(favorite_id)
            print("Deletion result:")
            print(delete_fav_result)
        
        if fetch_reservations:
            reservation_manager = ReservationManager(api_client)
            print("Retrieving current reservations...")
            reservations = await reservation_manager.get_reservations()
            print("Reservations:")
            print(reservations)
            
            now = datetime.now(timezone.utc)
            
            # Example values (commented out for reference)
            # start_time = "2025-02-15T10:00:00Z"
            start_time = (now + timedelta(hours=1)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            
            # end_time = "2025-02-15T11:00:00Z"
            end_time = (now + timedelta(hours=2)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            
            print("\nAdding a new reservation...")
            add_res_result = await reservation_manager.add_reservation("Test Reservation", "TEST123", start_time, end_time)
            print("Reservation addition result:")
            print(add_res_result)
            
            reservation_id = add_res_result.get("id") if add_res_result else None
            if not reservation_id:
                print("Failed to add reservation. Exiting.")
                return
            
            await asyncio.sleep(5)
            new_end_time = (now + timedelta(hours=3)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            print("\nUpdating reservation...")
            update_res_result = await reservation_manager.update_reservation(reservation_id, new_end_time)
            print("Update result:")
            print(update_res_result)
            
            await asyncio.sleep(5)
            print("\nDeleting reservation...")
            delete_res_result = await reservation_manager.delete_reservation(reservation_id)
            print("Deletion result:")
            print(delete_res_result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform DHParkeren operations: account details, reservation history, favorites, and reservations."
    )
    parser.add_argument("--account", action="store_true", default=False, help="Retrieve account details.")
    parser.add_argument("--history", action="store_true", default=False, help="Fetch reservation history.")
    parser.add_argument("--favorites", action="store_true", default=False, help="Manage favorites (retrieve, add, update, delete).")
    parser.add_argument("--reservations", action="store_true", default=False, help="Manage reservations (retrieve, add, update, delete).")
    args = parser.parse_args()
    
    asyncio.run(main(fetch_account=args.account,
                      fetch_history=args.history,
                      fetch_favorites=args.favorites,
                      fetch_reservations=args.reservations))
