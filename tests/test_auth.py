from http import HTTPStatus

from fastapi.testclient import TestClient

from app.models import User


def test_get_token(client: TestClient, user: User):
    response = client.post(
        '/auth/token/',
        data={
            'username': user.email,
            'password': 'testtest',
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
