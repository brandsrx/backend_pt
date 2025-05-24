import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from flask_jwt_extended import create_access_token
from app.run import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING":True,
    })
    yield app
    
@pytest.fixture()
def client(app):
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


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