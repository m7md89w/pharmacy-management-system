from sqlalchemy.orm import Session

from models.all_models import (
    SalesReturn,
    SalesReturnItem
)


class SalesReturnItemRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # CREATE
    # ==========================================
    def create(
        self,
        data: dict
    ):

        item = SalesReturnItem(**data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    # ==========================================
    # GET BY ID
    # ==========================================
    def get_by_id(
        self,
        return_item_id: int
    ):

        return (
            self.db.query(SalesReturnItem)
            .filter(
                SalesReturnItem.return_item_id
                == return_item_id
            )
            .first()
        )

    # ==========================================
    # GET BY RETURN
    # ==========================================
    def get_by_return(
        self,
        return_id: int
    ):

        return (
            self.db.query(SalesReturnItem)
            .filter(
                SalesReturnItem.return_id
                == return_id
            )
            .all()
        )

    # ==========================================
    # GET BY SALE ITEM
    # ==========================================
    def get_by_sale_item(
        self,
        sale_item_id: int
    ):

        return (
            self.db.query(SalesReturnItem)
            .filter(
                SalesReturnItem.sale_item_id
                == sale_item_id
            )
            .all()
        )

    # ==========================================
    # GET COMPLETED BY SALE ITEM
    # ==========================================
    def get_completed_by_sale_item(
        self,
        sale_item_id: int
    ):

        return (
            self.db.query(SalesReturnItem)
            .join(
                SalesReturn,
                SalesReturn.return_id
                == SalesReturnItem.return_id
            )
            .filter(
                SalesReturnItem.sale_item_id
                == sale_item_id,
                SalesReturn.status == "COMPLETED"
            )
            .all()
        )
    
    # ==========================================
# GET COMPLETED BY INVOICE
# ==========================================
    def get_completed_by_invoice(
        self,
       invoice_id: int
    ):

       return (
        self.db.query(SalesReturnItem)
        .join(
            SalesReturn,
            SalesReturn.return_id
            == SalesReturnItem.return_id
        )
        .filter(
            SalesReturn.invoice_id == invoice_id,
            SalesReturn.status == "COMPLETED"
        )
        .all()
         )

    # ==========================================
    # TOTAL RETURNED QUANTITY
    # ==========================================
    def get_total_returned_quantity(
        self,
        sale_item_id: int
    ):

        items = self.get_completed_by_sale_item(
            sale_item_id
        )

        return sum(
            item.quantity
            for item in items
        )

    # ==========================================
    # UPDATE
    # ==========================================
    def update(
        self,
        item
    ):

        self.db.commit()
        self.db.refresh(item)

        return item

    # ==========================================
    # DELETE
    # ==========================================
    def delete(
        self,
        item
    ):

        self.db.delete(item)
        self.db.commit()

        return True