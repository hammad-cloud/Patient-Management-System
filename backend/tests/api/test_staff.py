"""Tests for staff CRUD endpoints."""

from fastapi.testclient import TestClient


def _create_staff(
    client: TestClient,
    auth_headers: dict[str, str],
    payload: dict,
) -> None:
    response = client.post("/api/v1/staff/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    assert response.json()["message"] == "Staff created successfully."


def _first_staff_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.get("/api/v1/staff/", headers=auth_headers)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert items, "Expected at least one staff member in the list"
    return int(items[0]["id"])


def test_staff_require_auth(client: TestClient) -> None:
    """Staff routes should reject requests without a JWT."""
    assert client.get("/api/v1/staff/").status_code == 401
    assert client.post("/api/v1/staff/", json={}).status_code == 401


def test_create_staff(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Create should persist a staff member and return a success message."""
    _create_staff(client, auth_headers, sample_staff_payload)

    listed = client.get("/api/v1/staff/", headers=auth_headers)
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Fatima Noor"
    assert body["items"][0]["role"] == "Nurse"
    assert body["items"][0]["shift"] == "morning"


def test_list_staff_supports_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """List should support role/shift filters and search."""
    _create_staff(client, auth_headers, sample_staff_payload)
    _create_staff(
        client,
        auth_headers,
        {
            **sample_staff_payload,
            "full_name": "Hassan Ali",
            "role": "Receptionist",
            "shift": "night",
            "email": "hassan.ali@hospital.com",
            "phone": "03008887766",
            "salary": "40000.00",
        },
    )

    night = client.get(
        "/api/v1/staff/",
        params={"shift": "night"},
        headers=auth_headers,
    )
    assert night.status_code == 200
    night_body = night.json()
    assert night_body["total"] == 1
    assert night_body["items"][0]["full_name"] == "Hassan Ali"

    nurses = client.get(
        "/api/v1/staff/",
        params={"role": "Nurse"},
        headers=auth_headers,
    )
    assert nurses.status_code == 200
    assert nurses.json()["total"] == 1
    assert nurses.json()["items"][0]["role"] == "Nurse"

    search = client.get(
        "/api/v1/staff/",
        params={"search": "Hassan"},
        headers=auth_headers,
    )
    assert search.status_code == 200
    assert search.json()["total"] == 1
    assert search.json()["items"][0]["full_name"] == "Hassan Ali"


def test_get_staff_by_id(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Detail endpoint should return the full staff record."""
    _create_staff(client, auth_headers, sample_staff_payload)
    staff_id = _first_staff_id(client, auth_headers)

    response = client.get(f"/api/v1/staff/{staff_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == staff_id
    assert body["full_name"] == "Fatima Noor"
    assert body["role"] == "Nurse"
    assert "created_at" in body
    assert "updated_at" in body


def test_get_staff_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Missing staff IDs should return 404."""
    response = client.get("/api/v1/staff/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_staff(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Update should change only the provided fields."""
    _create_staff(client, auth_headers, sample_staff_payload)
    staff_id = _first_staff_id(client, auth_headers)

    response = client.put(
        f"/api/v1/staff/{staff_id}",
        json={"role": "Senior Nurse", "shift": "evening", "salary": "52000.00"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Staff updated successfully."

    detail = client.get(f"/api/v1/staff/{staff_id}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["role"] == "Senior Nurse"
    assert body["shift"] == "evening"
    assert body["salary"] == "52000.00"
    assert body["full_name"] == sample_staff_payload["full_name"]


def test_create_staff_rejects_duplicate_email(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Creating two staff members with the same email should fail."""
    _create_staff(client, auth_headers, sample_staff_payload)
    duplicate = {
        **sample_staff_payload,
        "full_name": "Another Nurse",
        "phone": "03001112233",
    }
    response = client.post("/api/v1/staff/", json=duplicate, headers=auth_headers)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_create_staff_rejects_duplicate_phone(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Creating two staff members with the same phone should fail."""
    _create_staff(client, auth_headers, sample_staff_payload)
    duplicate = {
        **sample_staff_payload,
        "full_name": "Another Nurse",
        "email": "another.nurse@hospital.com",
    }
    response = client.post("/api/v1/staff/", json=duplicate, headers=auth_headers)
    assert response.status_code == 400
    assert "phone" in response.json()["detail"].lower()


def test_create_staff_rejects_invalid_shift(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Invalid shift values should return a validation error."""
    response = client.post(
        "/api/v1/staff/",
        json={**sample_staff_payload, "shift": "afternoon"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_delete_staff(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_staff_payload: dict,
) -> None:
    """Delete should remove the staff record."""
    _create_staff(client, auth_headers, sample_staff_payload)
    staff_id = _first_staff_id(client, auth_headers)

    response = client.delete(f"/api/v1/staff/{staff_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Staff deleted successfully."

    missing = client.get(f"/api/v1/staff/{staff_id}", headers=auth_headers)
    assert missing.status_code == 404

    listed = client.get("/api/v1/staff/", headers=auth_headers)
    assert listed.json()["total"] == 0


def test_delete_staff_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Deleting a missing staff member should return 404."""
    response = client.delete("/api/v1/staff/9999", headers=auth_headers)
    assert response.status_code == 404
