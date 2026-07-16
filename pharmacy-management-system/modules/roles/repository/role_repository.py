from sqlalchemy.orm import Session

from models.all_models import Role


class RoleRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        role_data: dict
    ) -> Role:

        role = Role(**role_data)

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        return role

    def get_by_id(
        self,
        role_id: int
    ) -> Role | None:

        return (
            self.db.query(Role)
            .filter(
                Role.role_id == role_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(Role)
            .all()
        )

    def update(
        self,
        role: Role
    ):

        self.db.commit()
        self.db.refresh(role)

        return role

    def delete(
        self,
        role: Role
    ):

        self.db.delete(role)
        self.db.commit()

    def get_by_name(
        self,
        role_name: str
    ):

        return (
            self.db.query(Role)
            .filter(
                Role.role_name == role_name
            )
            .first()
        )