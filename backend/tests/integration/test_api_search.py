from backend.tests.conftest import client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200


