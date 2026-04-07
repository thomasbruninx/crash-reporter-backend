import pytest

from app.core.metadata_validation import validate_metadata_for_mongo


def test_validate_metadata_accepts_int64_limits():
    metadata = {"min": -(2**63), "max": 2**63 - 1}
    validate_metadata_for_mongo(metadata)


def test_validate_metadata_rejects_int_overflow_in_nested_structure():
    metadata = {"events": [{"payload": {"counter": 2**80}}]}

    with pytest.raises(ValueError, match=r"metadata\.events\[0\]\.payload\.counter"):
        validate_metadata_for_mongo(metadata)
