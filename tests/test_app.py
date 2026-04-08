import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["grace@mergington.edu", "maya@mergington.edu"]
    },
    "Music Band": {
        "description": "Learn and perform music in various genres",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["james@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["isabella@mergington.edu"]
    }
}

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data to initial state before each test."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirect():
    """Test that GET / redirects to the static index page."""
    # Arrange
    # (No special setup needed)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test successful retrieval of all activities."""
    # Arrange
    # (Data is reset by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
    assert len(data) == 7  # All activities present


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"

    # Verify the participant was added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up."""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity():
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_delete_participant_success():
    """Test successful removal of a participant."""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Removed {email} from {activity}"

    # Verify the participant was removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email not in activities_data[activity]["participants"]


def test_delete_participant_not_found():
    """Test deletion fails when participant is not in the activity."""
    # Arrange
    email = "nonexistent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"


def test_delete_invalid_activity():
    """Test deletion fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Invalid Activity"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"