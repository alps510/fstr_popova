from tests.conftest import client


def test_create_user():
    sample_payload = {
            "email": "qwerty1@mail.ru",
            "phone": "+7 777 777 77 74",
            "fam": "Пупкин",
            "name": "Василий",
            "otc": "Иванович"
        }
    response = client.post("/users/", json=sample_payload)
    assert response.status_code == 200


def test_read_user():
    user_id = 1
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "qwerty@mail.ru"
    assert data["id"] == user_id


def test_read_item():
    item_id = 2
    response = client.get(f"/items/{item_id}")
    data = response.json()
    assert data["title"] == "Пхия_updated"


def test_read_item_not_found():
    item_id = 5
    response = client.get(f"/items/{item_id}")
    data = response.json()
    assert data["message"] == "Item not found"


def test_read_data():
    user_id = 2
    response = client.get(f"/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


