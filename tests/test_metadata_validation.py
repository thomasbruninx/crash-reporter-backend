import pytest

from app.core.metadata_validation import normalize_metadata_for_mongo


def test_normalize_metadata_accepts_int64_limits():
    metadata = {"min": -(2**63), "max": 2**63 - 1}
    normalized = normalize_metadata_for_mongo(metadata)
    assert normalized == metadata


def test_normalize_metadata_converts_int_overflow_in_nested_structure_to_string():
    metadata = {"events": [{"payload": {"counter": 2**80}}]}
    normalized = normalize_metadata_for_mongo(metadata)
    assert normalized["events"][0]["payload"]["counter"] == str(2**80)


def test_normalize_metadata_rejects_non_string_keys():
    with pytest.raises(ValueError, match=r"metadata has a non-string key"):
        normalize_metadata_for_mongo({1: "bad"})
