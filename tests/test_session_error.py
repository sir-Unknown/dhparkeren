# tests/test_session_error.py
import pytest
from dhparkeren.session import SessionManager
from dhparkeren.config import Config, Secrets

# Hergebruik FakeResponse uit het vorige voorbeeld.
class FakeResponse:
    def __init__(self, status: int, cookie_value: str = None):
        self.status = status
        self.cookies = {}
        if cookie_value:
            self.cookies["session"] = type("FakeCookie", (), {"value": cookie_value})()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

# FakeAiohttpSession die een foutmelding simuleert door een response met status 500 terug te geven.
class FakeAiohttpSessionError:
    def get(self, url, headers):
        return FakeResponse(500)  # Status 500 simuleert een serverfout

    async def close(self):
        pass

# Subklasse van SessionManager om te maskeren (kan ook gewoon de basisklasse gebruiken)
class TestSessionManager(SessionManager):
    async def fetch_new_session(self) -> str:
        cookie = await super().fetch_new_session()
        if cookie is not None:
            return "MASKED_SESSION"
        return None

@pytest.mark.asyncio
async def test_fetch_new_session_error():
    """Test dat bij een fout bij het ophalen van een sessie (bijv. status 500)
    de fetch_new_session methode None retourneert."""
    dummy_config = Config(base_url="http://example.com")
    dummy_secrets = Secrets(username="dummy_user", password="dummy_pass")
    
    # Gebruik de FakeAiohttpSessionError die status 500 retourneert
    fake_session = FakeAiohttpSessionError()
    
    sm = TestSessionManager(dummy_secrets, dummy_config)
    sm.session = fake_session  # Vervang de echte sessie door onze fake sessie
    
    session_value = await sm.fetch_new_session()
    assert session_value is None
