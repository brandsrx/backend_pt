import pytest
from flask import Flask
from unittest.mock import MagicMock
from bson import ObjectId
from datetime import datetime, timedelta

path_signup = "/api/auth/signup"
path_login = "/api/auth/login"

def test_signup_success(client, mock_user_service, mock_jwt):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'bio': 'Test bio',
        'profile_pic_url': 'http://example.com/pic.jpg',
        'is_private': True
    }
    user_id = str(ObjectId())
    mock_user_service.create_user.return_value = user_id
    mock_jwt.return_value = 'mocked_jwt_token'

    response = client.post(path_signup, json=user_data)

    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'
    assert response.json['token'] == 'mocked_jwt_token'
    assert response.json['user_id'] == user_id
    mock_user_service.create_user.assert_called_once_with(
        username='testuser',
        email='test@example.com',
        password='password123',
        bio='Test bio',
        profile_pic_url='http://example.com/pic.jpg',
        is_private=True
    )

def test_signup_missing_required_fields(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com'
        # Falta password
    }

    response = client.post(path_signup, json=user_data)

    assert response.status_code == 400
    assert 'message' in response.json

def test_signup_value_error(client, mock_user_service):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    mock_user_service.create_user.side_effect = ValueError('Username already exists')

    response = client.post(path_signup, json=user_data)

    assert response.status_code == 400
    assert response.json['message'] == 'Username already exists'

def test_signup_internal_error(client, mock_user_service):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    mock_user_service.create_user.side_effect = Exception('Database error')

    response = client.post(path_signup, json=user_data)

    assert response.status_code == 500
    assert response.json['message'] == 'Error registering user'

def test_login_success(client, mock_user_service, mock_jwt):
    credentials = {
        'username_or_email': 'testuser',
        'password': 'password123'
    }
    user_id = str(ObjectId())
    user_data = {
        '_id': ObjectId(user_id),
        'username': 'testuser',
        'email': 'test@example.com'
    }
    mock_user_service.authenticate_user.return_value = user_data
    mock_jwt.return_value = 'mocked_jwt_token'

    response = client.post(path_login, json=credentials)

    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'
    assert response.json['token'] == 'mocked_jwt_token'
    assert response.json['user']['id'] == user_id
    assert response.json['user']['username'] == 'testuser'
    assert response.json['user']['email'] == 'test@example.com'
    mock_user_service.authenticate_user.assert_called_once_with('testuser', 'password123')

def test_login_missing_credentials(client):
    credentials = {
        'username_or_email': 'testuser'
        # Falta password
    }

    response = client.post(path_login, json=credentials)

    assert response.status_code == 400
    assert response.json['message'] == 'Missing username/email or password'

def test_login_invalid_credentials(client, mock_user_service):
    credentials = {
        'username_or_email': 'testuser',
        'password': 'wrongpassword'
    }
    mock_user_service.authenticate_user.return_value = None

    response = client.post(path_login, json=credentials)

    assert response.status_code == 401
    assert response.json['message'] == 'Invalid credentials'

def test_login_internal_error(client, mock_user_service):
    credentials = {
        'username_or_email': 'testuser',
        'password': 'password123'
    }
    mock_user_service.authenticate_user.side_effect = Exception('Database error')

    response = client.post(path_login, json=credentials)

    assert response.status_code == 500
    assert response.json['message'] == 'Error logging in'