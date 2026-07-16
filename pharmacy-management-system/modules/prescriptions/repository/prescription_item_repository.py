from sqlalchemy.orm import Session
from models.all_models import (
    PrescriptionItem
)


class PrescriptionItemRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        item = PrescriptionItem(
            **data
        )

        self.db.add(
            item
        )

        self.db.commit()
        self.db.refresh(
            item
        )

        return item

    def get_by_id(
        self,
        prescription_item_id: int
    ):

        return (
            self.db.query(
                PrescriptionItem
            )
            .filter(
                PrescriptionItem.prescription_item_id
                == prescription_item_id
            )
            .first()
        )

    def get_by_prescription(
        self,
        prescription_id: int
    ):

        return (
            self.db.query(
                PrescriptionItem
            )
            .filter(
                PrescriptionItem.prescription_id
                == prescription_id
            )
            .all()
        )

    def delete(
        self,
        item
    ):

        self.db.delete(
            item
        )
        self.db.commit()