import json
from pathlib import Path


def test_filtered_openapi_contains_only_client_endpoints():
    path = Path(__file__).resolve().parents[1] / "openapi" / "openapi-clients.json"
    assert path.exists(), "run scripts/filter_openapi_for_clients.py first"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert set(data["paths"].keys()) == {"/api/v1/instance", "/api/v1/report"}
