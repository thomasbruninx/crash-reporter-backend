INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


def validate_metadata_for_mongo(metadata: dict[str, object]) -> None:
    _validate_value(value=metadata, path="metadata")


def _validate_value(value: object, path: str) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} has a non-string key")
            _validate_value(value=nested_value, path=f"{path}.{key}")
        return

    if isinstance(value, list):
        for index, nested_value in enumerate(value):
            _validate_value(value=nested_value, path=f"{path}[{index}]")
        return

    if isinstance(value, bool):
        return

    if isinstance(value, int):
        if value < INT64_MIN or value > INT64_MAX:
            raise ValueError(f"{path} contains an integer outside MongoDB int64 range")
        return

