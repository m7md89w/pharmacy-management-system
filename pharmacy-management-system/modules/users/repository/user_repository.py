from sqlalchemy.orm import Session

from models.all_models import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_data: dict
    ) -> User:

        user = User(**user_data)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(
        self,
        user_id: int
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.user_id == user_id
            )
            .first()
        )

    def get_by_username(
        self,
        username: str
    ):

        return (
            self.db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(User)
            .all()
        )

    def update(
        self,
        user: User
    ):

        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate(
        self,
        user: User
    ):

        user.is_active = False

        self.db.commit()
        self.db.refresh(user)

        return user