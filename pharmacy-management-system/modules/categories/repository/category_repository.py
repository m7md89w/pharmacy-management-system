from sqlalchemy.orm import Session
from models.all_models import Category


class CategoryRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        category = Category(
            **data
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def get_by_id(
        self,
        category_id: int
    ):

        return (
            self.db.query(Category)
            .filter(
                Category.category_id == category_id
            )
            .first()
        )

    def get_by_name(
        self,
        category_name: str
    ):

        return (
            self.db.query(Category)
            .filter(
                Category.category_name == category_name
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(Category)
            .all()
        )

    def update(
        self,
        category
    ):

        self.db.commit()
        self.db.refresh(category)

        return category

    def delete(
        self,
        category
    ):

        self.db.delete(category)
        self.db.commit()