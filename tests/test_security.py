from app.core.security import create_token, decode_token


def test_token_roundtrip():
    token = create_token("abc", ["report.create"], 60, instance_uuid="inst-1")
    claims = decode_token(token)
    assert claims["sub"] == "abc"
    assert "report.create" in claims["scopes"]
    assert claims["instance_uuid"] == "inst-1"
