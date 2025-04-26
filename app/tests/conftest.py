import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from app.config import Config
from app.run import app as aplication
from flask_jwt_extended import create_access_token
@pytest.fixture
def app():
    aplication.config['TESTING'] = True
    aplication.config.from_object(Config)
    return aplication

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_user_service():
    with patch('app.controllers.auth_controller.UserService') as mock:
        yield mock

@pytest.fixture
def mock_jwt():
    with patch('app.controllers.auth_controller.create_access_token') as mock:
        mock.return_value = 'mocked_jwt_token'
        yield mock
        
@pytest.fixture
def auth_headers():
    """Fixture para crear headers de Authorization para los tests."""
    token = create_access_token(
        identity="1234567890abcdef",
        additional_claims={"username":"tesuser"}
    )
    return {
        "Authorization": f"Bearer {token}"
    }