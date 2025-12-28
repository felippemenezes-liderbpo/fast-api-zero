from http import HTTPStatus

from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_must_return_ok_headers_json_and_message_hello_world() -> None:
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'].startswith('application/json')
    assert response.json() == {'message': 'Hello World!'}


def test_html_must_return_ok_headers_html_and_title_hello_world() -> None:
    response = client.get('/html')
    soup = BeautifulSoup(response.text, 'html.parser')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'].startswith('text/html')
    assert soup.title is not None
    assert soup.title.get_text(strip=True) == 'Hello World'
