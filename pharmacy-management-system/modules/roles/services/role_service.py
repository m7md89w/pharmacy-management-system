from modules.roles.repository.role_repository import RoleRepository


class RoleService:

    def __init__(
        self,
        role_repo: RoleRepository
    ):
        self.role_repo = role_repo

    def create_role(
        self,
        data: dict
    ):

        if not data.get("role_name"):
            raise ValueError(
                "Role name is required"
            )

        existing = self.role_repo.get_by_name(
            data["role_name"]
        )

        if existing:
            raise ValueError(
                "Role already exists"
            )

        return self.role_repo.create(
            data
        )

    def get_role(
        self,
        role_id: int
    ):

        role = self.role_repo.get_by_id(
            role_id
        )

        if not role:
            raise ValueError(
                "Role not found"
            )

        return role

    def get_all_roles(self):

        return self.role_repo.get_all()

    def update_role(
        self,
        role,
        data: dict
    ):

        if "role_name" in data:
            role.role_name = data["role_name"]

        if "description" in data:
            role.description = data["description"]

        return self.role_repo.update(
            role
        )

    def delete_role(
        self,
        role
    ):

        return self.role_repo.delete(
            role
        )