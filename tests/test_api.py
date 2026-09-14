from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "documentation" in data

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["valid_regions"]) == 7
    assert data["parameters"]["num_beams"] == 4

def test_regions_endpoint():
    response = client.get("/api/regions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    assert all("examples" in r for r in data)
    assert all("bleu" in r for r in data)

def test_insights_endpoint():
    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert "overall_benchmarks" in data
    assert "per_region_banglat5" in data
    assert len(data["per_region_banglat5"]) == 7

def test_translate_valid_request():
    payload = {
        "region": "Chittagong",
        "sentence": "ক্যান আছু?",
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "translation" in data
    assert data["mode"] == "simulation"

def test_translate_invalid_region():
    payload = {
        "region": "Sylhet", # Sylhet was excluded from final scope
        "sentence": "কিতা খবর?",
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 400
    assert "Invalid region" in response.json()["detail"]

def test_translate_empty_sentence():
    payload = {
        "region": "Barishal",
        "sentence": "   ",
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 400
    assert "Please type a dialect sentence" in response.json()["detail"]
