import jwt

from datetime import datetime
from datetime import timedelta



SECRET_KEY = "4b00d21aed0caedeaf0845d1d34bebc2695f0c20a15675d7c4fef8d44a2e622f"
ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 24


class JWTHandler:

    @staticmethod
    def create_token(
        user_id: int,
        username: str,
        role_id: int
    ):

        payload = {
            "user_id": user_id,
            "username": username,
            "role_id": role_id,
            "exp": datetime.utcnow()
            + timedelta(
                hours=TOKEN_EXPIRE_HOURS
            )
        }

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return token

    @staticmethod
    def verify_token(
        token: str
    ):

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload