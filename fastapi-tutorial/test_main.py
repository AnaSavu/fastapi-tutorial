from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_get_nested_models():
    response = client.post("/nested/models",
                           json={"item_id": "1", "tags": ["ana", "banana"]})
    assert response.status_code == 200
    assert response.json() == {"item_id": "1", "tags": ["ana", "banana"]}

