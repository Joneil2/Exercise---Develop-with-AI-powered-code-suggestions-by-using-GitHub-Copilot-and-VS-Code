import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has the required fields
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up with a test email
    test_email = "test@example.com"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200
    result = response.json()
    assert "message" in result

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert test_email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test that duplicate signups are rejected"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up with a test email
    test_email = "duplicate@example.com"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200

    # Try to sign up again - should fail
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signing up for non-existent activity"""
    response = client.post(
        "/activities/NonExistentActivity/signup",
        params={"email": "test@example.com"}
    )
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect():
    """Test that root redirects to static index"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]