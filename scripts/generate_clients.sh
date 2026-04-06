#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PARENT_DIR="$(cd "$ROOT_DIR/.." && pwd)"

python3 "$SCRIPT_DIR/export_openapi.py"
python3 "$SCRIPT_DIR/filter_openapi_for_clients.py"

SPEC="$ROOT_DIR/openapi/openapi-clients.json"

generate() {
  local generator="$1"
  local output="$2"
  npx -y @openapitools/openapi-generator-cli generate -g "$generator" -i "$SPEC" -o "$output"
}

generate go "$PARENT_DIR/crash-reporter-go"
generate typescript-axios "$PARENT_DIR/crash-reporter-ts"
generate java "$PARENT_DIR/crash-reporter-java"
generate csharp "$PARENT_DIR/crash-reporter-dotnet"
generate c "$PARENT_DIR/crash-reporter-lib"
generate python "$PARENT_DIR/crash-reporter-python"

echo "Clients generated."
