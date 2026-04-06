from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)

ALL_SCOPES = [
    "user.create",
    "project.create",
    "project.read",
    "project.update",
    "project.delete",
    "instance.read",
    "instance.update",
    "instance.delete",
    "report.create",
    "report.read",
    "report.update",
    "report.delete",
]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(sub: str, scopes: list[str], expires_seconds: int, instance_uuid: str | None = None) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": sub,
        "scopes": scopes,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_seconds)).timestamp()),
    }
    if instance_uuid:
        payload["instance_uuid"] = instance_uuid
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def get_current_claims(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    if credentials is not None:
        return decode_token(credentials.credentials)

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return decode_token(cookie_token)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")


def require_scope(required_scope: str):
    def checker(claims: dict = Depends(get_current_claims)) -> dict:
        scopes = claims.get("scopes", [])
        if required_scope not in scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scope: {required_scope}")
        return claims

    return checker
