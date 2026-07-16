from sqlalchemy import func

from models.all_models import (
    SalesInvoice,
    PurchaseOrder,
    Inventory,
    MedicineBatch
)

from datetime import date


class DashboardRepository:

    def __init__(self, db):
        self.db = db

    def get_summary(self):

        sales = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        SalesInvoice.total_amount
                    ),
                    0
                )
            )
            .scalar()
        )

        purchases = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        PurchaseOrder.total_amount
                    ),
                    0
                )
            )
            .scalar()
        )

        medicines = (
            self.db.query(
                func.count(
                    Inventory.inventory_id
                )
            )
            .scalar()
        )

        low_stock = (
            self.db.query(
                Inventory
            )
            .filter(
                Inventory.quantity
                <= Inventory.min_stock_level
            )
            .count()
        )

        expired = (
            self.db.query(
                MedicineBatch
            )
            .filter(
                MedicineBatch.expiry_date
                < date.today()
            )
            .count()
        )

        return {
            "total_sales":
            float(sales),

            "total_purchases":
            float(purchases),

            "profit":
            float(sales - purchases),

            "medicines_count":
            medicines,

            "low_stock_count":
            low_stock,

            "expired_batches":
            expired
        }