# jwt_handler.py
import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DELTA

def create_jwt(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_DELTA
    payload.update({"exp": expire})
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        # Convert "exp" from a timestamp to a datetime object
        expire = datetime.utcfromtimestamp(payload["exp"])
        return payload if expire >= datetime.utcnow() else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
