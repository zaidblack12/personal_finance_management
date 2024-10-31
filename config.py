# config.py
import os
from datetime import timedelta

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(minutes=30)
