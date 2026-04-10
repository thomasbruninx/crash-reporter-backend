import pytest
from fastapi import HTTPException

from app.api.routes import (
    INSTANCE_SORT_FIELDS,
    PROJECT_SORT_FIELDS,
    REPORT_SORT_FIELDS,
    sql_sort_dir,
    validate_sort,
)


def test_validate_sort_accepts_supported_fields():
    validate_sort("name", PROJECT_SORT_FIELDS)
    validate_sort("uuid", INSTANCE_SORT_FIELDS)
    validate_sort("timestamp", REPORT_SORT_FIELDS)
    validate_sort(None, REPORT_SORT_FIELDS)


def test_validate_sort_rejects_unknown_field():
    with pytest.raises(HTTPException) as exc:
        validate_sort("unknown", PROJECT_SORT_FIELDS)
    assert exc.value.status_code == 422
    assert "Unsupported sort_by" in str(exc.value.detail)


def test_sql_sort_dir_desc():
    assert sql_sort_dir("desc") is True
    assert sql_sort_dir("asc") is False
