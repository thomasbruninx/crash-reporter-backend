INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


def normalize_metadata_for_mongo(metadata: dict[str, object]) -> dict[str, object]:
    return _normalize_value(value=metadata, path="metadata")


def _normalize_value(value: object, path: str) -> object:
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} has a non-string key")
            normalized[key] = _normalize_value(value=nested_value, path=f"{path}.{key}")
        return normalized

    if isinstance(value, list):
        return [_normalize_value(value=nested_value, path=f"{path}[{index}]") for index, nested_value in enumerate(value)]

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value < INT64_MIN or value > INT64_MAX:
            return str(value)
        return value

    return value
