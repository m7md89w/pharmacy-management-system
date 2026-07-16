from sqlalchemy import func
from sqlalchemy.orm import Session

from models.all_models import (
    SaleItem,
    SalesInvoice
)


class SaleItemRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # CREATE
    # ==================================================
    def create(
        self,
        item_data: dict
    ) -> SaleItem:

        item = SaleItem(
            **item_data
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
        sale_item_id: int
    ) -> SaleItem | None:

        return (
            self.db.query(SaleItem)
            .filter(
                SaleItem.sale_item_id
                == sale_item_id
            )
            .first()
        )

    # ==================================================
    # GET ALL
    # ==================================================
    def get_all(self):

        return (
            self.db.query(SaleItem)
            .all()
        )

    # ==================================================
    # GET BY INVOICE
    # ==================================================
    def get_by_invoice(
        self,
        invoice_id: int
    ):

        return (
            self.db.query(SaleItem)
            .filter(
                SaleItem.invoice_id
                == invoice_id
            )
            .all()
        )

    # ==================================================
    # TOTAL SOLD BY BATCH
    # ==================================================
    def get_total_sold_by_batch(
        self,
        batch_id: int
    ):

        total = (

            self.db.query(

                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                    ),
                    0
                )

            )

            .join(
                SalesInvoice,
                SalesInvoice.invoice_id
                ==
                SaleItem.invoice_id
            )

            .filter(

                SaleItem.batch_id
                ==
                batch_id,

                SalesInvoice.status
                ==
                "COMPLETED"

            )

            .scalar()

        )

        return total or 0

    # ==================================================
    # UPDATE
    # ==================================================
    def update(
        self,
        item: SaleItem
    ):

        self.db.commit()
        self.db.refresh(item)

        return item

    # ==================================================
    # DELETE
    # ==================================================
    def delete(
        self,
        item: SaleItem
    ):

        self.db.delete(item)
        self.db.commit()