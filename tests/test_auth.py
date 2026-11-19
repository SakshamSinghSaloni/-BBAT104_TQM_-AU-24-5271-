"""
Integration tests for Teacher/User Authentication & Identity (API Layer).
Covers registration, duplicate email prevention, login, credential verification, and session logout.
"""

import pytest


def test_register_teacher_success(client):
    """Verify that teacher registration succeeds with valid data and sets session cookie."""
    resp = client.post(
        "/api/auth/register",
        json={
            "name": "Prof. Jane Smith",
            "email": "jane.smith@example.edu",
            "password": "strongpassword123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Prof. Jane Smith"
    assert data["email"] == "jane.smith@example.edu"
    assert data["role"] == "teacher"
    assert "password" not in data
    assert "password_hash" not in data

    # Verify session cookie was set
    assert "quiz_session" in resp.cookies


def test_register_duplicate_email_rejected(client):
    """Verify that registering an existing email address is rejected with 409 Conflict."""
    payload = {
        "name": "Prof. Alex Morgan",
        "email": "alex.morgan@example.edu",
        "password": "password123",
    }
    first_resp = client.post("/api/auth/register", json=payload)
    assert first_resp.status_code == 201

    # Duplicate attempt
    dup_resp = client.post("/api/auth/register", json=payload)
    assert dup_resp.status_code == 409
    assert "already exists" in dup_resp.json()["detail"]


def test_register_invalid_inputs(client):
    """Verify that invalid inputs (short password, invalid email) fail validation."""
    # Short password (< 6 chars)
    resp = client.post(
        "/api/auth/register",
        json={"name": "Teacher", "email": "valid@example.com", "password": "123"},
    )
    assert resp.status_code == 422

    # Malformed email
    resp2 = client.post(
        "/api/auth/register",
        json={"name": "Teacher", "email": "not-an-email", "password": "password123"},
    )
    assert resp2.status_code == 422


def test_login_teacher_success(client):
    """Verify that valid credentials log the teacher in and set a signed session cookie."""
    # First register
    client.post(
        "/api/auth/register",
        json={"name": "Prof. John", "email": "john@example.edu", "password": "password123"},
    )

    # Login
    resp = client.post(
        "/api/auth/login",
        json={"email": "john@example.edu", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "john@example.edu"
    assert "quiz_session" in resp.cookies


def test_login_invalid_password(client):
    """Verify that an incorrect password returns 401 Unauthorized."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. John", "email": "john2@example.edu", "password": "correctpassword"},
    )

    resp = client.post(
        "/api/auth/login",
        json={"email": "john2@example.edu", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_login_nonexistent_user(client):
    """Verify that unknown email returns 401 Unauthorized."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.edu", "password": "anyPassword123"},
    )
    assert resp.status_code == 401


def test_auth_me_endpoint(client):
    """Verify that /api/auth/me returns current user when authenticated, 401 when not."""
    # Unauthenticated
    unauth_resp = client.get("/api/auth/me")
    assert unauth_resp.status_code == 401

    # Register & Login
    client.post(
        "/api/auth/register",
        json={"name": "Prof. Sarah", "email": "sarah@example.edu", "password": "password123"},
    )

    # Authenticated me
    auth_resp = client.get("/api/auth/me")
    assert auth_resp.status_code == 200
    assert auth_resp.json()["email"] == "sarah@example.edu"


def test_logout(client):
    """Verify that logout clears the session cookie."""
    # Log in first
    client.post(
        "/api/auth/register",
        json={"name": "Prof. Tom", "email": "tom@example.edu", "password": "password123"},
    )
    assert "quiz_session" in client.cookies

    # Logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    # Cookie should be deleted / expired
    cookie = logout_resp.cookies.get("quiz_session")
    assert cookie is None or cookie == '""'
