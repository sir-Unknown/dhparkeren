# tests/test_account.py
import pytest
from dhparkeren.account import AccountManager

# Fake ApiClient die een succesvolle response simuleert
class FakeApiClient:
    async def request_data(self, method: str, endpoint: str):
        if method == "GET" and endpoint == "/api/account/0":
            return {
                "id": 632458,
                "debit_minutes": 760,
                "credit_minutes": 0,
                "notifications_enabled": True,
                "reminders_enabled": True,
                "language": "nl",
                "created": "2018-02-13T14:43:50.550Z",
                "mod": "2025-02-15T17:11:52.426Z",
                "is_company": False,
                "reservation_count": "0",
                "zone": {
                    "id": "30",
                    "name": "Centrum Zuid",
                    "end_time": "2025-02-17T23:00:00Z",
                    "start_time": "2025-02-17T08:00:00Z"
                }
            }
        return None

@pytest.mark.asyncio
async def test_get_account_success():
    """Test dat AccountManager de juiste accountgegevens retourneert."""
    fake_client = FakeApiClient()
    account_manager = AccountManager(fake_client)
    account_data = await account_manager.get_account()
    
    expected = {
        "id": 632458,
        "debit_minutes": 9160,
        "credit_minutes": 0,
        "notifications_enabled": True,
        "reminders_enabled": True,
        "language": "nl",
        "created": "2019-01-13T14:41:50.550Z",
        "mod": "2025-02-14T17:11:52.426Z",
        "is_company": False,
        "reservation_count": "0",
        "zone": {
            "id": "30",
            "name": "Centrum Zuid",
            "end_time": "2025-02-17T23:00:00Z",
            "start_time": "2025-02-17T08:00:00Z"
        }
    }
    assert account_data == expected
