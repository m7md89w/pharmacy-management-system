from sqlalchemy import func
from models.all_models import (
    PurchaseOrder,
    PurchaseItem
)


class PurchaseReportRepository:

    def __init__(self, db):
        self.db = db

    def get_summary(self):

        orders_count, total_amount = (
            self.db.query(
                func.count(
                    PurchaseOrder.purchase_id
                ),
                func.coalesce(
                    func.sum(
                        PurchaseOrder.total_amount
                    ),
                    0
                )
            )
            .first()
        )

        total_items = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        PurchaseItem.quantity
                    ),
                    0
                )
            )
            .scalar()
        )

        return {
            "purchase_orders": orders_count,
            "total_purchases": float(
                total_amount
            ),
            "total_items_purchased":
            total_items
        }