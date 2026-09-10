import os
import jwt

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()


# ==================================================
# CONFIGURATION
# ==================================================

SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")
ALGORITHM: str = "HS256"
TOKEN_EXPIRE_HOURS: int = int(os.environ.get("JWT_EXPIRE_HOURS", "24"))

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is not set. "
        "Copy .env.example to .env and set a strong secret key."
    )


# ==================================================
# JWT HANDLER
# ==================================================

class JWTHandler:

    @staticmethod
    def create_token(
        user_id: int,
        username: str,
        role_id: int
    ) -> str:
        """
        Creates a signed JWT access token.
        Uses timezone-aware UTC to avoid deprecation warnings in Python 3.12+.
        """
        payload = {
            "user_id": user_id,
            "username": username,
            "role_id": role_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Decodes and validates a JWT token.
        Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
        """
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])