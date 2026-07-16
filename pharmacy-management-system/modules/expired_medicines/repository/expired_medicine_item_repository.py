from sqlalchemy.orm import Session
from models.all_models import ExpiredMedicineItem


class ExpiredMedicineItemRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        data: dict
    ) -> ExpiredMedicineItem:

        item = ExpiredMedicineItem(**data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def get_by_id(
        self,
        expired_item_id: int
    ) -> ExpiredMedicineItem | None:

        return (
            self.db.query(ExpiredMedicineItem)
            .filter(
                ExpiredMedicineItem.expired_item_id
                == expired_item_id
            )
            .first()
        )

    def get_by_expired(
        self,
        expired_id: int
    ):

        return (
            self.db.query(ExpiredMedicineItem)
            .filter(
                ExpiredMedicineItem.expired_id
                == expired_id
            )
            .all()
        )

    def delete(
        self,
        item: ExpiredMedicineItem
    ):

        self.db.delete(item)
        self.db.commit()