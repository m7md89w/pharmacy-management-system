from sqlalchemy.orm import Session

from models.all_models import PurchaseItem


class PurchaseItemRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        item_data: dict
    ) -> PurchaseItem:

        item = PurchaseItem(**item_data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def get_by_id(
        self,
        purchase_item_id: int
    ) -> PurchaseItem | None:

        return (
            self.db.query(PurchaseItem)
            .filter(
                PurchaseItem.purchase_item_id
                == purchase_item_id
            )
            .first()
        )

    def get_by_purchase(
        self,
        purchase_id: int
    ) -> list[PurchaseItem]:

        return (
            self.db.query(PurchaseItem)
            .filter(
                PurchaseItem.purchase_id
                == purchase_id
            )
            .all()
        )

    def update(
        self,
        item: PurchaseItem
    ) -> PurchaseItem:

        self.db.commit()
        self.db.refresh(item)

        return item

    def delete(
        self,
        item: PurchaseItem
    ):

        self.db.delete(item)
        self.db.commit()