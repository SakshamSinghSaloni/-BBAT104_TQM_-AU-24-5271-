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


def test_update_profile_success(client):
    """Verify that authenticated teacher can update their display name."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. Original", "email": "prof.orig@example.edu", "password": "password123"},
    )

    resp = client.put(
        "/api/auth/profile",
        json={"name": "Prof. Renamed Instructor"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Prof. Renamed Instructor"

    # Verify /me reflects updated name
    me_resp = client.get("/api/auth/me")
    assert me_resp.json()["name"] == "Prof. Renamed Instructor"


def test_update_profile_blank_name_rejected(client):
    """Tier 2: Verify that empty or whitespace-only name updates are rejected."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. Valid", "email": "prof.valid@example.edu", "password": "password123"},
    )

    # Empty string
    resp1 = client.put("/api/auth/profile", json={"name": ""})
    assert resp1.status_code == 422

    # Whitespace only
    resp2 = client.put("/api/auth/profile", json={"name": "   "})
    assert resp2.status_code == 422


def test_change_password_success(client):
    """Verify that teacher can change their password and authenticate with the new credentials."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. PwdTest", "email": "prof.pwd@example.edu", "password": "oldPassword123"},
    )

    resp = client.put(
        "/api/auth/change-password",
        json={"current_password": "oldPassword123", "new_password": "newSecurePassword456"},
    )
    assert resp.status_code == 200
    assert "Password updated successfully" in resp.json()["message"]

    # Log out
    client.post("/api/auth/logout")

    # Old password must now fail
    old_login = client.post(
        "/api/auth/login",
        json={"email": "prof.pwd@example.edu", "password": "oldPassword123"},
    )
    assert old_login.status_code == 401

    # New password must succeed
    new_login = client.post(
        "/api/auth/login",
        json={"email": "prof.pwd@example.edu", "password": "newSecurePassword456"},
    )
    assert new_login.status_code == 200


def test_change_password_invalid_current_rejected(client):
    """Verify that providing an incorrect current password rejects the update."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. SecCheck", "email": "prof.sec@example.edu", "password": "correctPassword123"},
    )

    resp = client.put(
        "/api/auth/change-password",
        json={"current_password": "incorrectPassword", "new_password": "newSecurePassword456"},
    )
    assert resp.status_code == 401
    assert "Current password is incorrect" in resp.json()["detail"]


def test_update_profile_unauthenticated_rejected(client):
    """Verify that unauthenticated callers cannot update profile."""
    resp = client.put("/api/auth/profile", json={"name": "Attacker"})
    assert resp.status_code == 401


def test_change_password_short_password_rejected(client):
    """Verify that attempting to change password to < 6 chars is rejected."""
    client.post(
        "/api/auth/register",
        json={"name": "Prof. ShortPwd", "email": "prof.short@example.edu", "password": "validPassword123"},
    )
    resp = client.put(
        "/api/auth/change-password",
        json={"current_password": "validPassword123", "new_password": "123"},
    )
    assert resp.status_code == 422
