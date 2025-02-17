#!/usr/bin/env python3
import os
import argparse
import asyncio

from dhparkeren.config import Config, Secrets
from dhparkeren.session import SessionManager
from dhparkeren.client import ApiClient
from dhparkeren.account import AccountManager
from dhparkeren.favorites import FavoriteManager
from dhparkeren.reservations import ReservationManager

async def main(fetch_account: bool, fetch_reservations: bool):
    # Gebruik de opgegeven base_url
    config = Config(base_url="https://parkerendenhaag.denhaag.nl")
    
    # Haal de inloggegevens uit de omgevingsvariabelen
    username = os.environ.get("DHPARKEREN_USERNAME")
    password = os.environ.get("DHPARKEREN_PASSWORD")
    
    if not username or not password:
        print("Error: Environment variables DHPARKEREN_USERNAME and DHPARKEREN_PASSWORD must be set.")
        return
    
    secrets = Secrets(username=username, password=password)
    
    # Creëer een sessiemanager in een asynchrone context
    async with SessionManager(secrets, config) as session_manager:
        # Maak een API-client
        api_client = ApiClient(session_manager)
        
        # Optioneel: Haal en toon accountgegevens op
        if fetch_account:
            account_manager = AccountManager(api_client)
            print("Haal accountgegevens op...")
            account_data = await account_manager.get_account()
            print("Accountgegevens:")
            print(account_data)
        
        # Optioneel: Haal en toon reserveringen op
        if fetch_reservations:
            reservation_manager = ReservationManager(api_client)
            print("Haal reserveringen op...")
            reservations_response = await reservation_manager.get_reservations()
            # Afhankelijk van de API-response kan dit een dictionary of lijst zijn:
            if isinstance(reservations_response, dict):
                reservations = reservations_response.get("reservations", [])
            elif isinstance(reservations_response, list):
                reservations = reservations_response
            else:
                reservations = []
            print("Reserveringen:")
            print(reservations)
        
        # Favorieten beheren:
        favorite_manager = FavoriteManager(api_client)
        
        # 1. Haal de huidige favorieten op en toon deze
        print("\nHuidige favorieten:")
        current_favorites = await favorite_manager.get_favorites()
        print(current_favorites)
        
        # 2. Voeg een nieuw favoriet-item toe
        print("\nNieuw favoriet-item toevoegen...")
        add_result = await favorite_manager.add_favorite("Test Favorite", "TEST123")
        print("Toevoegresultaat:")
        print(add_result)
        
        # Ga ervan uit dat de response een 'favorite_id' bevat
        favorite_id = add_result.get("id") if add_result else None
        if not favorite_id:
            print("Favoriet-item kon niet worden toegevoegd. Afsluiten.")
            return
        
        # 3. Wacht 5 seconden en update vervolgens het favoriet-item
        await asyncio.sleep(5)
        print("\nFavoriet-item bijwerken...")
        update_result = await favorite_manager.update_favorite(favorite_id, "Updated Favorite", "TEST123")
        print("Bijwerkresultaat:")
        print(update_result)
        
        # 4. Wacht nog eens 5 seconden en verwijder het favoriet-item
        await asyncio.sleep(5)
        print("\nFavoriet-item verwijderen...")
        delete_result = await favorite_manager.delete_favorite(favorite_id)
        print("Verwijderresultaat:")
        print(delete_result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Voer DHParkeren operaties uit: accountgegevens, reserveringen en favorieten."
    )
    parser.add_argument(
        "--account", action="store_true", default=False,
        help="Haal accountgegevens op."
    )
    parser.add_argument(
        "--reservations", action="store_true", default=False,
        help="Haal reserveringen op."
    )
    args = parser.parse_args()
    
    asyncio.run(main(fetch_account=args.account, fetch_reservations=args.reservations))

