#!/usr/bin/env python3
import argparse
from uuid import uuid4

from sqlalchemy import select

from app.core.security import ALL_SCOPES, hash_password, create_token
from app.db.sql import Base, engine, SessionLocal
from app.models.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Create user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.username == args.username)).scalar_one_or_none()
        if existing:
            print("User already exists")
            return
        user = User(uuid=str(uuid4()), username=args.username, password_hash=hash_password(args.password))
        db.add(user)
        db.commit()
        token = create_token(sub=user.uuid, scopes=ALL_SCOPES, expires_seconds=3600)
        print(f"Created user {user.username} ({user.uuid})")
        print(f"Sample login-equivalent token: {token}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
