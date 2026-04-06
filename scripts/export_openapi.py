#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app

with open(ROOT / "openapi/openapi.json", "w", encoding="utf-8") as f:
    json.dump(app.openapi(), f, indent=2)
print("Wrote openapi/openapi.json")
