from modules.users.repository.user_repository import UserRepository
from modules.roles.repository.role_repository import RoleRepository
from modules.auth.utils.password_handler import PasswordHandler

class UserService:

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def create_user(
        self,
        data: dict
    ):

        role = self.role_repo.get_by_id(
            data["role_id"]
        )

        if not role:
            raise ValueError(
                "Role not found"
            )

        existing_user = (
            self.user_repo.get_by_username(
                data["username"]
            )
        )

        if existing_user:
            raise ValueError(
                "Username already exists"
            )

        if not data.get("password_hash"):
            raise ValueError(
                "Password is required"
            )
        data["password_hash"] = (
             PasswordHandler.hash_password(
             data["password_hash"]
              )
            )
        return self.user_repo.create(
            data
        )

    def get_user(
        self,
        user_id: int
    ):

        user = self.user_repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        return user

    def get_all_users(self):

        return self.user_repo.get_all()

    def update_user(
        self,
        user,
        data: dict
    ):

        fields = [
            "full_name",
            "email",
            "phone",
            "password_hash",
            "role_id"
        ]

        for field in fields:

            if field in data:
                setattr(
                    user,
                    field,
                    data[field]
                )

        return self.user_repo.update(
            user
        )

    def deactivate_user(
        self,
        user
    ):

        return self.user_repo.deactivate(
            user
        )