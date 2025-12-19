import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
  """Ensure in-memory activities are restored after each test."""
  snapshot = copy.deepcopy(activities)
  yield
  activities.clear()
  activities.update(copy.deepcopy(snapshot))


@pytest.fixture()
def client():
  return TestClient(app)


def test_get_activities_returns_data(client):
  response = client.get("/activities")
  assert response.status_code == 200
  data = response.json()
  assert "Chess Club" in data
  assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant(client):
  email = "newstudent@mergington.edu"
  response = client.post("/activities/Chess%20Club/signup", params={"email": email})
  assert response.status_code == 200
  assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_rejected(client):
  email = activities["Programming Class"]["participants"][0]
  response = client.post("/activities/Programming%20Class/signup", params={"email": email})
  assert response.status_code == 400


def test_unregister_participant(client):
  email = "remove_me@mergington.edu"
  activities["Gym Class"]["participants"].append(email)

  response = client.delete("/activities/Gym%20Class/participants", params={"email": email})

  assert response.status_code == 200
  assert email not in activities["Gym Class"]["participants"]


def test_unregister_missing_participant(client):
  response = client.delete(
    "/activities/Drama%20Club/participants", params={"email": "absent@mergington.edu"}
  )

  assert response.status_code == 404