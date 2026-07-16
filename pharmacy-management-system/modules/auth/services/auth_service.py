from modules.users.repository.user_repository import UserRepository

from modules.auth.utils.password_handler import PasswordHandler
from modules.auth.utils.jwt_handler import JWTHandler


class AuthService:

    def __init__(
        self,
        user_repo: UserRepository
    ):
        self.user_repo = user_repo

    def login(
        self,
        username: str,
        password: str
    ):

        user = self.user_repo.get_by_username(
            username
        )

        if not user:
            raise ValueError(
                "Invalid username or password"
            )

        if not user.is_active:
            raise ValueError(
                "User is inactive"
            )

        password_valid = (
            PasswordHandler.verify_password(
                password,
                user.password_hash
            )
        )

        if not password_valid:
            raise ValueError(
                "Invalid username or password"
            )

        token = JWTHandler.create_token(
            user_id=user.user_id,
            username=user.username,
            role_id=user.role_id
        )

        return {
            "access_token": token,
            "user_id": user.user_id,
            "username": user.username,
            "role_id": user.role_id
        }