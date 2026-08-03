"""Tests for patient CRUD endpoints."""

from fastapi.testclient import TestClient


def _create_patient(
    client: TestClient,
    auth_headers: dict[str, str],
    payload: dict,
) -> None:
    response = client.post("/api/v1/patients/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    assert response.json()["message"] == "Patient created successfully."


def _first_patient_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.get("/api/v1/patients/", headers=auth_headers)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert items, "Expected at least one patient in the list"
    return int(items[0]["id"])


def test_patients_require_auth(client: TestClient) -> None:
    """Patient routes should reject requests without a JWT."""
    assert client.get("/api/v1/patients/").status_code == 401
    assert client.post("/api/v1/patients/", json={}).status_code == 401


def test_create_patient(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Create should persist a patient and return a success message."""
    _create_patient(client, auth_headers, sample_patient_payload)

    listed = client.get("/api/v1/patients/", headers=auth_headers)
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["counts"]["all"] == 1
    assert body["counts"]["active"] == 1
    assert body["items"][0]["full_name"] == "Ali Khan"
    assert body["items"][0]["status"] == "active"
    assert body["items"][0]["doctor_id"] == sample_patient_payload["doctor_id"]
    assert body["items"][0]["doctor"]["full_name"] == "Dr. Ahmed Khan"


def test_create_patient_rejects_duplicate_phone(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Creating two patients with the same phone should fail."""
    _create_patient(client, auth_headers, sample_patient_payload)

    duplicate = {
        **sample_patient_payload,
        "full_name": "Sara Khan",
        "email": "sara.khan@example.com",
    }
    response = client.post("/api/v1/patients/", json=duplicate, headers=auth_headers)
    assert response.status_code == 400
    assert "phone" in response.json()["detail"].lower()


def test_list_patients_supports_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """List should support gender and status filters."""
    _create_patient(client, auth_headers, sample_patient_payload)
    _create_patient(
        client,
        auth_headers,
        {
            **sample_patient_payload,
            "full_name": "Sara Khan",
            "gender": "female",
            "status": "inactive",
            "phone": "03007654321",
            "email": "sara.khan@example.com",
            "diseases": ["Asthma"],
        },
    )

    female = client.get(
        "/api/v1/patients/",
        params={"gender": "female"},
        headers=auth_headers,
    )
    assert female.status_code == 200
    female_body = female.json()
    assert female_body["total"] == 1
    assert female_body["items"][0]["full_name"] == "Sara Khan"
    assert female_body["counts"]["all"] == 2
    assert female_body["counts"]["active"] == 1

    inactive = client.get(
        "/api/v1/patients/",
        params={"status": "inactive"},
        headers=auth_headers,
    )
    assert inactive.status_code == 200
    assert inactive.json()["total"] == 1
    assert inactive.json()["items"][0]["status"] == "inactive"


def test_get_patient_by_id(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Detail endpoint should return the full patient record."""
    _create_patient(client, auth_headers, sample_patient_payload)
    patient_id = _first_patient_id(client, auth_headers)

    response = client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == patient_id
    assert body["full_name"] == "Ali Khan"
    assert body["email"] == "ali.khan@example.com"
    assert body["diseases"] == ["Diabetes", "Hypertension"]
    assert "created_at" in body
    assert "updated_at" in body


def test_get_patient_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Missing patient IDs should return 404."""
    response = client.get("/api/v1/patients/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_patient(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Update should change only the provided fields."""
    _create_patient(client, auth_headers, sample_patient_payload)
    patient_id = _first_patient_id(client, auth_headers)

    response = client.patch(
        f"/api/v1/patients/{patient_id}",
        json={"full_name": "Ali Updated", "age": 36},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Patient updated successfully."

    detail = client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["full_name"] == "Ali Updated"
    assert body["age"] == 36
    assert body["phone"] == sample_patient_payload["phone"]


def test_update_patient_status(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Status can be toggled through the update endpoint."""
    _create_patient(client, auth_headers, sample_patient_payload)
    patient_id = _first_patient_id(client, auth_headers)

    response = client.patch(
        f"/api/v1/patients/{patient_id}",
        json={"status": "inactive"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    detail = client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert detail.json()["status"] == "inactive"

    listed = client.get("/api/v1/patients/", headers=auth_headers)
    assert listed.json()["counts"]["active"] == 0
    assert listed.json()["counts"]["all"] == 1


def test_delete_patient(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Delete should remove the patient record."""
    _create_patient(client, auth_headers, sample_patient_payload)
    patient_id = _first_patient_id(client, auth_headers)

    response = client.delete(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Patient deleted successfully."

    missing = client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)
    assert missing.status_code == 404

    listed = client.get("/api/v1/patients/", headers=auth_headers)
    assert listed.json()["total"] == 0
    assert listed.json()["counts"]["all"] == 0


def test_delete_patient_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Deleting a missing patient should return 404."""
    response = client.delete("/api/v1/patients/9999", headers=auth_headers)
    assert response.status_code == 404


def test_search_patients_by_name(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Search should match patient names."""
    _create_patient(client, auth_headers, sample_patient_payload)
    _create_patient(
        client,
        auth_headers,
        {
            **sample_patient_payload,
            "full_name": "Sara Ahmed",
            "phone": "03001112233",
            "email": "sara.ahmed@example.com",
            "diseases": ["Flu"],
        },
    )

    response = client.get(
        "/api/v1/patients/",
        params={"search": "Sara"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Sara Ahmed"


def test_create_patient_rejects_missing_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Creating a patient without a valid doctor should fail."""
    payload = {**sample_patient_payload, "doctor_id": 9999}
    response = client.post("/api/v1/patients/", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "doctor" in response.json()["detail"].lower()


def test_list_patients_filter_by_doctor(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
    sample_doctor_payload: dict,
) -> None:
    """List should support filtering by assigned doctor."""
    _create_patient(client, auth_headers, sample_patient_payload)

    second_doctor = {
        **sample_doctor_payload,
        "full_name": "Dr. Sara Ali",
        "email": "sara.ali@hospital.com",
        "phone": "03009998877",
    }
    created = client.post("/api/v1/doctors/", json=second_doctor, headers=auth_headers)
    assert created.status_code == 201
    doctors = client.get("/api/v1/doctors/", headers=auth_headers)
    second_id = next(
        item["id"]
        for item in doctors.json()["items"]
        if item["full_name"] == "Dr. Sara Ali"
    )

    _create_patient(
        client,
        auth_headers,
        {
            **sample_patient_payload,
            "full_name": "Sara Ahmed",
            "phone": "03007654321",
            "email": "sara.ahmed@example.com",
            "doctor_id": second_id,
        },
    )

    filtered = client.get(
        "/api/v1/patients/",
        params={"doctor_id": second_id},
        headers=auth_headers,
    )
    assert filtered.status_code == 200
    body = filtered.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Sara Ahmed"
    assert body["items"][0]["doctor_id"] == second_id


def test_cannot_delete_doctor_with_assigned_patients(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_patient_payload: dict,
) -> None:
    """Doctors with assigned patients cannot be deleted."""
    _create_patient(client, auth_headers, sample_patient_payload)
    doctor_id = sample_patient_payload["doctor_id"]

    response = client.delete(f"/api/v1/doctors/{doctor_id}", headers=auth_headers)
    assert response.status_code == 400
    assert "patient" in response.json()["detail"].lower()
