"""Tests for doctor CRUD endpoints."""

from fastapi.testclient import TestClient


def _create_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    payload: dict,
) -> None:
    response = client.post("/api/v1/doctors/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    assert response.json()["message"] == "Doctor created successfully."


def _first_doctor_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.get("/api/v1/doctors/", headers=auth_headers)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert items, "Expected at least one doctor in the list"
    return int(items[0]["id"])


def test_doctors_require_auth(client: TestClient) -> None:
    """Doctor routes should reject requests without a JWT."""
    assert client.get("/api/v1/doctors/").status_code == 401
    assert client.post("/api/v1/doctors/", json={}).status_code == 401


def test_create_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Create should persist a doctor and return a success message."""
    _create_doctor(client, auth_headers, sample_doctor_payload)

    listed = client.get("/api/v1/doctors/", headers=auth_headers)
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Dr. Ahmed Khan"
    assert body["items"][0]["specialization"] == "Cardiology"


def test_create_doctor_rejects_duplicate_email(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Creating two doctors with the same email should fail."""
    _create_doctor(client, auth_headers, sample_doctor_payload)

    duplicate = {
        **sample_doctor_payload,
        "full_name": "Dr. Sara Ali",
        "phone": "03009998877",
    }
    response = client.post("/api/v1/doctors/", json=duplicate, headers=auth_headers)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_create_doctor_rejects_duplicate_phone(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Creating two doctors with the same phone should fail."""
    _create_doctor(client, auth_headers, sample_doctor_payload)

    duplicate = {
        **sample_doctor_payload,
        "full_name": "Dr. Sara Ali",
        "email": "sara.ali@hospital.com",
    }
    response = client.post("/api/v1/doctors/", json=duplicate, headers=auth_headers)
    assert response.status_code == 400
    assert "phone" in response.json()["detail"].lower()


def test_list_doctors_supports_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """List should support specialization filter and search."""
    _create_doctor(client, auth_headers, sample_doctor_payload)
    _create_doctor(
        client,
        auth_headers,
        {
            **sample_doctor_payload,
            "full_name": "Dr. Sara Ali",
            "specialization": "Dermatology",
            "email": "sara.ali@hospital.com",
            "phone": "03009998877",
            "salary": "120000.00",
        },
    )

    dermatology = client.get(
        "/api/v1/doctors/",
        params={"specialization": "Dermatology"},
        headers=auth_headers,
    )
    assert dermatology.status_code == 200
    body = dermatology.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Dr. Sara Ali"

    search = client.get(
        "/api/v1/doctors/",
        params={"search": "Ahmed"},
        headers=auth_headers,
    )
    assert search.status_code == 200
    assert search.json()["total"] == 1
    assert search.json()["items"][0]["full_name"] == "Dr. Ahmed Khan"


def test_get_doctor_by_id(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Detail endpoint should return the full doctor record."""
    _create_doctor(client, auth_headers, sample_doctor_payload)
    doctor_id = _first_doctor_id(client, auth_headers)

    response = client.get(f"/api/v1/doctors/{doctor_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == doctor_id
    assert body["full_name"] == "Dr. Ahmed Khan"
    assert body["email"] == "ahmed.khan@hospital.com"
    assert "created_at" in body
    assert "updated_at" in body


def test_get_doctor_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Missing doctor IDs should return 404."""
    response = client.get("/api/v1/doctors/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Update should change only the provided fields."""
    _create_doctor(client, auth_headers, sample_doctor_payload)
    doctor_id = _first_doctor_id(client, auth_headers)

    response = client.put(
        f"/api/v1/doctors/{doctor_id}",
        json={"full_name": "Dr. Ahmed Updated", "salary": "175000.00"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor updated successfully."

    detail = client.get(f"/api/v1/doctors/{doctor_id}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["full_name"] == "Dr. Ahmed Updated"
    assert body["salary"] == "175000.00"
    assert body["phone"] == sample_doctor_payload["phone"]


def test_delete_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> None:
    """Delete should remove the doctor record."""
    _create_doctor(client, auth_headers, sample_doctor_payload)
    doctor_id = _first_doctor_id(client, auth_headers)

    response = client.delete(f"/api/v1/doctors/{doctor_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor deleted successfully."

    missing = client.get(f"/api/v1/doctors/{doctor_id}", headers=auth_headers)
    assert missing.status_code == 404

    listed = client.get("/api/v1/doctors/", headers=auth_headers)
    assert listed.json()["total"] == 0


def test_delete_doctor_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Deleting a missing doctor should return 404."""
    response = client.delete("/api/v1/doctors/9999", headers=auth_headers)
    assert response.status_code == 404
