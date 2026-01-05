from http import HTTPStatus

from fastapi.testclient import TestClient

from app.models import User
from app.schemas import UserPublic


def test_create_user(client: TestClient) -> None:
    user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=user,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': user['username'],
        'email': user['email'],
    }


def test_read_users_with_user(client: TestClient, user: User) -> None:
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [user_schema],
    }


def test_read_users_empty(client: TestClient):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_update_user(client: TestClient, user: User):
    new_user: dict[str, str] = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'newpassword',
    }
    response = client.put('/users/1', json=new_user)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': new_user['username'],
        'email': new_user['email'],
    }


def test_update_integrity_error(client: TestClient, user: User):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client: TestClient, user: User):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
