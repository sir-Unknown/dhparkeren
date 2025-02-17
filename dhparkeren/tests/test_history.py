# tests/test_history.py
import pytest
from dhparkeren.client import ApiClient
from dhparkeren.config import Config


# We definiëren een fake session manager en een fake API-client.
class FakeSessionManager:
    def __init__(self):
        # We hoeven enkel een minimale config te bieden
        self.config = Config(base_url="http://fake.api")
        # Overige attributen worden niet gebruikt in deze test.
        self.session_cookie = "fake_cookie"
    def create_headers(self):
        return {"Accept": "application/json"}

# Maak een subclass van ApiClient die request_data overschrijft
class FakeApiClient(ApiClient):
    async def request_data(self, method: str, endpoint: str, extra_headers=None):
        if method == "GET" and endpoint == "/api/history":
            return {
                "history": [
                    {
                        "license_plate": "AB-123-CD",
                        "start_time": "2025-02-15T10:00:00Z",
                        "end_time": "2025-02-14T17:11:00Z",
                        "minutes_used": 0
                    },
                    {
                        "license_plate": "AB-123-CD",
                        "start_time": "2025-03-13T20:06:00Z",
                        "end_time": "2025-02-13T22:21:00Z",
                        "minutes_used": 0
                    },
                    # Je kunt hier extra entries toevoegen als dat nodig is.
                ]
            }
        return None

@pytest.mark.asyncio
async def test_get_history():
    """Test dat ApiClient.get_history() de verwachte history data retourneert."""
    fake_session_manager = FakeSessionManager()
    # Voor deze test zijn Secrets niet van belang; we geven dummy waarden.
    # We maken een FakeApiClient met onze fake session manager.
    api_client = FakeApiClient(fake_session_manager, max_retries=1)
    
    history_data = await api_client.get_history()
    assert history_data is not None, "Er werd geen history data geretourneerd."
    assert "history" in history_data, "De key 'history' ontbreekt in de response."
    history_list = history_data["history"]
    assert isinstance(history_list, list), "'history' moet een lijst zijn."
    # Controleer de eerste entry op de verwachte keys
    if history_list:
        expected_keys = {"license_plate", "start_time", "end_time", "minutes_used"}
        first_entry_keys = set(history_list[0].keys())
        assert expected_keys.issubset(first_entry_keys), f"Verwachte keys {expected_keys} ontbreken in de entry: {first_entry_keys}"
