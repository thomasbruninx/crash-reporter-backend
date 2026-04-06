#!/usr/bin/env python3
import json

IN_PATH = "openapi/openapi.json"
OUT_PATH = "openapi/openapi-clients.json"
ALLOWED = {"/api/v1/instance": {"post"}, "/api/v1/report": {"post"}}

with open(IN_PATH, "r", encoding="utf-8") as f:
    doc = json.load(f)

new_paths = {}
for path, ops in doc.get("paths", {}).items():
    if path not in ALLOWED:
        continue
    allowed_ops = ALLOWED[path]
    picked = {m: op for m, op in ops.items() if m.lower() in allowed_ops}
    if picked:
        new_paths[path] = picked

doc["paths"] = new_paths

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2)

print(f"Wrote {OUT_PATH}")
