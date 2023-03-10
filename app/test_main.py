from fastapi.testclient import TestClient

from .main import api

client = TestClient(api)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to My-API !"}


def test_get_user_valid_user():
    response = client.get("/user", auth=("captain", "nemo"))
    assert response.status_code == 200
    assert response.json() == {"message": "Hello captain"}


def test_get_user_invalid_user():
    response = client.get("/user", auth=("jule", "verne"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_retrieve_category_exist():
    response = client.get("/category/0", auth=("pierre", "arronax"))
    assert response.status_code == 200
    assert response.json() == {
        "id": 0,
        "name": "Category A",
        "slug": "category-a",
        "description": "This is category A",
        "parent": "p0"
    }


def test_retrieve_category_notexist():
    response = client.get("/category/9", auth=("pierre", "arronax"))
    assert response.status_code == 204


def test_delete_category_notused():
    response = client.delete("/category/7", auth=("captain", "nemo"))
    assert response.status_code == 204


def test_delete_category_used():
    response = client.delete("/category/0", auth=("captain", "nemo"))
    assert response.status_code == 400
