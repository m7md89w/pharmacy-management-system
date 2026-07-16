from sqlalchemy import func
from models.all_models import (
    SalesInvoice,
    PurchaseOrder
)


class ProfitReportRepository:

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

        return {
            "total_sales":
            float(sales),

            "total_purchases":
            float(purchases),

            "profit":
            float(sales - purchases)
        }