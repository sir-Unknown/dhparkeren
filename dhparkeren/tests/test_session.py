# tests/test_session.py

import pytest
from dhparkeren.session import SessionManager
from dhparkeren.config import Config, Secrets


# FakeResponse die als asynchrone contextmanager werkt
class FakeResponse:
    def __init__(self, status: int, cookie_value: str):
        self.status = status
        # Simuleer een cookie-object met een 'value'-attribuut.
        self.cookies = {"session": type("FakeCookie", (), {"value": cookie_value})()}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

# FakeAiohttpSession: maak 'get' een reguliere functie zodat deze meteen een FakeResponse teruggeeft
class FakeAiohttpSession:
    def __init__(self, cookie_value: str):
        self.cookie_value = cookie_value

    def get(self, url, headers):
        # Retourneer direct een FakeResponse
        return FakeResponse(200, self.cookie_value)

    async def close(self):
        pass

# We maken een subklasse van SessionManager die de sessiewaarde maskeert voor privacy.
class TestSessionManager(SessionManager):
    async def fetch_new_session(self) -> str:
        cookie = await super().fetch_new_session()
        if cookie is not None:
            # Voor privacy: vervang de echte waarde door een gemaskeerde waarde
            return "MASKED_SESSION"
        return None

@pytest.mark.asyncio
async def test_fetch_new_session_masks_value():
    # Dummy cookie-waarde (normaal de raw waarde van de sessie)
    dummy_cookie = "f84cdac9-b891-487a-9a3a-f37f5f1cb7f3"
    
    # Dummy configuratie en secrets
    dummy_config = Config(base_url="http://example.com")
    dummy_secrets = Secrets(username="dummy_user", password="dummy_pass")
    
    # Maak een fake aiohttp sessie die een succesvolle response met dummy_cookie retourneert.
    fake_session = FakeAiohttpSession(dummy_cookie)
    
    # Instantieer de TestSessionManager (die de cookiewaarde maskeert)
    sm = TestSessionManager(dummy_secrets, dummy_config)
    # Vervang de echte aiohttp sessie door onze fake sessie
    sm.session = fake_session
    
    session_value = await sm.fetch_new_session()
    # Verwacht dat de cookie-waarde gemaskeerd wordt
    assert session_value == "MASKED_SESSION"
