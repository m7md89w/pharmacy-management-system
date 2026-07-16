from sqlalchemy import func
from models.all_models import SalesInvoice, SaleItem


class SalesReportRepository:

    def __init__(self, db):
        self.db = db

    def get_summary(
        self,
        start_date=None,
        end_date=None
    ):

        query = self.db.query(
            func.count(
                SalesInvoice.invoice_id
            ),
            func.coalesce(
                func.sum(
                    SalesInvoice.total_amount
                ),
                0
            )
        )

        if start_date:
            query = query.filter(
                SalesInvoice.created_at >= start_date
            )

        if end_date:
            query = query.filter(
                SalesInvoice.created_at <= end_date
            )

        invoices_count, total_sales = query.first()

        total_items = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                    ),
                    0
                )
            )
            .scalar()
        )

        return {
            "invoices_count": invoices_count,
            "total_sales": float(total_sales),
            "total_items_sold": total_items
        }