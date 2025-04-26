import pytest

@pytest.fixture
def new_user():
    return {
        '_id': '1234567890abcdef',
        'username': 'testuser',
        'email': 'test@example.com',
        'bio': 'Test bio',
        'profile_pic_url': 'http://example.com/pic.jpg',
        'is_private': False
    }
    
    
def test_get_profile(client, monkeypatch, mock_user_service, auth_headers):
    user_id = "1234567890abcdef"
    # Mock get_jwt_identity para devolver el ID del usuario creado
    def mock_get_identity():
        return user_id

    # Reemplazar la función get_jwt_identity con el mock
    monkeypatch.setattr('flask_jwt_extended.get_jwt_identity', mock_get_identity)
    print(auth_headers)
    # Hacer la solicitud con headers de autenticación
    response = client.get('/api/users/profile', headers=auth_headers)

    # Verificar la respuesta
    assert response.status_code == 200
    assert response.json['user_id'] == user_id