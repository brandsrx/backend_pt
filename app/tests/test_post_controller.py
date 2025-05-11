
import json
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

@pytest.fixture
def mock_user_id():
    return "1234567890abcdef"

@pytest.fixture
def mock_user_data():
    return {
        "_id": "1234567890abcdef",
        "username": "testuser",
        "email": "test@example.com",
        "bio": "Test bio",
        "profile_pic_url": "https://example.com/pic.jpg",
        "password": "hashed_password",
        "created_at": "2023-01-01T00:00:00",
        "privacy": {
            "is_private": False,
            "show_email": True,
            "allow_mentions": True
        }
    }

@pytest.fixture
def mock_post_data():
    return {
        "_id": "1234567890abcdef",
        "username": "testuser",
        "email": "test@example.com",
        "bio": "Test bio",
        "profile_pic_url": "https://example.com/pic.jpg",
        "password": "hashed_password",
        "created_at": "2023-01-01T00:00:00",
        "privacy": {
            "is_private": False,
            "show_email": True,
            "allow_mentions": True
        }
    }


def test_view_post_empty(client):
    response = client.get("/api/posts/")
    print(response.status_code)
    assert response.status_code == 200
    assert response.json != None
    
    