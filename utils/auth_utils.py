from fastapi import HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

from sqlalchemy.orm import Session

from ..models import User


SECRET_KEY = "7f3c64622007ae3a085708c6d00dcd7ccaae3047ecf1872ad0846659038e1115"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashed_password(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_current_user(db: Session, user_id: int = 1) -> User:
    """Get current user (simplified - use JWT in production)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
):
    encode = data.copy()
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
