"""MVP access control: enrollment tokens and admin guard."""


def test_lesson_without_token_rejected(client, enrollment):
    response = client.get(f"/api/enrollments/{enrollment['enrollment_id']}/lesson")
    assert response.status_code == 401


def test_dashboard_with_forged_token_rejected(client, enrollment):
    response = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/dashboard",
        headers={"X-Enrollment-Token": "not-the-real-token"},
    )
    assert response.status_code == 401


def test_unknown_enrollment_returns_404(client):
    response = client.get(
        "/api/enrollments/99999/lesson",
        headers={"X-Enrollment-Token": "anything"},
    )
    assert response.status_code == 404


def test_admin_requires_token(client):
    assert client.get("/api/admin/students").status_code == 401
    assert client.get("/api/admin/students", headers={"X-Admin-Token": "wrong"}).status_code == 401


def test_admin_default_token_grants_access(client):
    response = client.get("/api/admin/students", headers={"X-Admin-Token": "pyschool-admin"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cors_origin_not_wildcard(client):
    """The wildcard-with-credentials configuration must not come back."""
    origin = "http://localhost:5173"
    response = client.get("/api/health", headers={"Origin": origin})
    assert response.headers.get("access-control-allow-origin") == origin
