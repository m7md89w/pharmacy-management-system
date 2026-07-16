from sqlalchemy import func
from sqlalchemy.orm import Session

from models.all_models import (
    PurchaseReturn,
    PurchaseReturnItem
)


class PurchaseReturnItemRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # CREATE
    # ==================================================
    def create(
        self,
        data: dict
    ) -> PurchaseReturnItem:

        item = PurchaseReturnItem(
            **data
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    # ==================================================
    # GET BY ID
    # ==================================================
    def get_by_id(
        self,
        return_item_id: int
    ) -> PurchaseReturnItem | None:

        return (
            self.db.query(
                PurchaseReturnItem
            )
            .filter(
                PurchaseReturnItem.return_item_id
                == return_item_id
            )
            .first()
        )

    # ==================================================
    # GET BY RETURN
    # ==================================================
    def get_by_return(
        self,
        return_id: int
    ) -> list[PurchaseReturnItem]:

        return (
            self.db.query(
                PurchaseReturnItem
            )
            .filter(
                PurchaseReturnItem.return_id
                == return_id
            )
            .all()
        )

    # ==================================================
    # GET BY PURCHASE ITEM
    # ==================================================
    def get_by_purchase_item(
        self,
        purchase_item_id: int
    ) -> list[PurchaseReturnItem]:

        return (
            self.db.query(
                PurchaseReturnItem
            )
            .filter(
                PurchaseReturnItem.purchase_item_id
                == purchase_item_id
            )
            .all()
        )

    # ==================================================
    # TOTAL COMPLETED RETURNED QUANTITY
    # ==================================================
    def get_total_returned_quantity(
        self,
        purchase_item_id: int
    ) -> int:

        total = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        PurchaseReturnItem.quantity
                    ),
                    0
                )
            )
            .join(
                PurchaseReturn,
                PurchaseReturn.return_id
                == PurchaseReturnItem.return_id
            )
            .filter(
                PurchaseReturnItem.purchase_item_id
                == purchase_item_id,

                PurchaseReturn.status
                == "COMPLETED"
            )
            .scalar()
        )

        return total or 0

    # ==================================================
    # GET COMPLETED ITEMS BY PURCHASE
    # ==================================================
    def get_by_completed_purchase(
        self,
        purchase_id: int
    ) -> list[PurchaseReturnItem]:

        return (
            self.db.query(
                PurchaseReturnItem
            )
            .join(
                PurchaseReturn,
                PurchaseReturn.return_id
                == PurchaseReturnItem.return_id
            )
            .filter(
                PurchaseReturn.purchase_id
                == purchase_id,

                PurchaseReturn.status
                == "COMPLETED"
            )
            .all()
        )

    # ==================================================
    # UPDATE
    # ==================================================
    def update(
        self,
        item: PurchaseReturnItem
    ) -> PurchaseReturnItem:

        self.db.commit()
        self.db.refresh(item)

        return item

    # ==================================================
    # DELETE
    # ==================================================
    def delete(
        self,
        item: PurchaseReturnItem
    ) -> bool:

        self.db.delete(item)
        self.db.commit()

        return True