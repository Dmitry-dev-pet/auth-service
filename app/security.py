from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from .main import get_settings

settings = get_settings()

SECRET_KEY = settings.AUTH_JWT_SECRET_KEY
ALGORITHM = settings.AUTH_JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
