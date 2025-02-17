#!/usr/bin/env python3
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
        
        # Accountgegevens ophalen
        if fetch_account:
            account_manager = AccountManager(api_client)
            print("Haal accountgegevens op...")
            account_data = await account_manager.get_account()
            print("Accountgegevens:")
            print(account_data)
        
        # Reserveringshistorie ophalen (als de API hiervoor een aparte endpoint heeft)
        if fetch_history:
            print("Haal reserveringshistorie op...")
            history = await api_client.get_history()  # Zorg dat deze methode bestaat en een JSON-object of lijst retourneert.
            print("Reserveringshistorie:")
            print(history)
        
        # Favorieten beheren
        if fetch_favorites:
            favorite_manager = FavoriteManager(api_client)
            print("Haal huidige favorieten op...")
            favorites = await favorite_manager.get_favorites()
            print("Favorieten:")
            print(favorites)
            
            # Voeg een nieuw favoriet-item toe
            print("\nNieuw favoriet-item toevoegen...")
            add_fav_result = await favorite_manager.add_favorite("Test Favorite", "TEST123")
            print("Toevoegresultaat:")
            print(add_fav_result)
            
            # Gebruik de sleutel "id" uit de response als identifier
            favorite_id = add_fav_result.get("id") if add_fav_result else None
            if not favorite_id:
                print("Favoriet-item kon niet worden toegevoegd. Afsluiten.")
                return
            
            # Wacht 5 seconden en update het favoriet-item
            await asyncio.sleep(5)
            print("\nFavoriet-item bijwerken...")
            update_fav_result = await favorite_manager.update_favorite(favorite_id, "Updated Favorite", "TEST123")
            print("Bijwerkresultaat:")
            print(update_fav_result)
            
            # Wacht nog 5 seconden en verwijder het favoriet-item
            await asyncio.sleep(5)
            print("\nFavoriet-item verwijderen...")
            delete_fav_result = await favorite_manager.delete_favorite(favorite_id)
            print("Verwijderresultaat:")
            print(delete_fav_result)
        
        # Reserveringen beheren
        if fetch_reservations:
            reservation_manager = ReservationManager(api_client)
            print("Haal huidige reserveringen op...")
            reservations = await reservation_manager.get_reservations()
            print("Reserveringen:")
            print(reservations)
            
            # Voeg een nieuw reservering-item toe
            now = datetime.now(timezone.utc)
            start_time = (now + timedelta(hours=1)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            end_time = (now + timedelta(hours=2)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            print("\nNieuw reservering-item toevoegen...")
            add_res_result = await reservation_manager.add_reservation("Test Reservation", "TEST123", start_time, end_time)
            print("Reservering toevoegen resultaat:")
            print(add_res_result)
            
            # Gebruik de sleutel "id" uit de response als identifier
            reservation_id = add_res_result.get("id") if add_res_result else None
            if not reservation_id:
                print("Reservering kon niet worden toegevoegd. Afsluiten.")
                return
            
            # Wacht 5 seconden en update de reservering (verleng de eindtijd)
            await asyncio.sleep(5)
            new_end_time = (now + timedelta(hours=3)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            print("\nReservering bijwerken...")
            update_res_result = await reservation_manager.update_reservation(reservation_id, new_end_time)
            print("Reservering bijwerk resultaat:")
            print(update_res_result)
            
            # Wacht nog 5 seconden en verwijder de reservering
            await asyncio.sleep(5)
            print("\nReservering verwijderen...")
            delete_res_result = await reservation_manager.delete_reservation(reservation_id)
            print("Reservering verwijder resultaat:")
            print(delete_res_result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Voer DHParkeren operaties uit: accountgegevens, reserveringshistorie, favorieten en reserveringen."
    )
    parser.add_argument("--account", action="store_true", default=False, help="Haal accountgegevens op.")
    parser.add_argument("--history", action="store_true", default=False, help="Haal reserveringshistorie op.")
    parser.add_argument("--favorites", action="store_true", default=False, help="Beheer favorieten (ophalen, toevoegen, bijwerken, verwijderen).")
    parser.add_argument("--reservations", action="store_true", default=False, help="Beheer reserveringen (ophalen, toevoegen, bijwerken, verwijderen).")
    args = parser.parse_args()
    
    asyncio.run(main(fetch_account=args.account,
                      fetch_history=args.history,
                      fetch_favorites=args.favorites,
                      fetch_reservations=args.reservations))
