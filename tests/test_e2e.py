from fastapi.testclient import TestClient
from app.main import app
from app.config import MODULES
def test_all_pages_and_api():
    with TestClient(app) as c:
        for slug,label in MODULES:
            assert c.get("/"+slug).status_code==200
            assert c.get("/api/"+slug).status_code==200
def test_run_and_stale_api():
    with TestClient(app) as c:
        a=c.post("/api/runs",json={"sample":"dirty"}).json();rid=a["manifest"]["run_id"]
        assert c.post(f"/api/runs/{rid}/review",json={"revision":1,"decision":"通过"}).status_code==200
        assert c.post(f"/api/runs/{rid}/review",json={"revision":1,"decision":"通过"}).status_code==409
        assert c.get(f"/api/runs/{rid}/evidence.csv").status_code==200
def test_bad_input_api():
    with TestClient(app) as c:assert c.post("/api/runs",json={"text":"wrong"}).status_code==422
