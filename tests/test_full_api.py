import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.api.rest import app
from src.core.database import async_session
from src.core.user_engine import User
from src.modules.music.models import Track
from datetime import datetime

client = TestClient(app)

# Mock database dependency
async def override_get_db():
    mock_session = AsyncMock()
    yield mock_session

app.dependency_overrides[async_session] = override_get_db

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_login():
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401

def test_admin_users():
    response = client.get("/admin/users/", headers={"Authorization": "Bearer fake"})
    assert response.status_code == 403  # چون توکن فیک

def test_music_tracks():
    response = client.get("/admin/music/tracks")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_user():
    from src.core.user_engine import create_user_if_not_exists
    db = AsyncMock()
    db.execute.return_value.scalars.return_value.first.return_value = None
    user = await create_user_if_not_exists(db, 123456, "Test User", "testuser")
    assert user.full_name == "Test User"
    db.add.assert_called_once()
    db.commit.assert_called()

@pytest.mark.asyncio
async def test_music_service_search():
    from src.modules.music.service import music_service
    db = AsyncMock()
    db.execute.return_value.scalars.return_value.all.return_value = []
    tracks = await music_service.search_tracks(db, "test")
    assert tracks == []

# تست‌های بیشتر برای wallet, transactions, tickets...
