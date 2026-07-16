from sqlalchemy import func
from models.all_models import Inventory


class InventoryReportRepository:

    def __init__(self, db):
        self.db = db

    def get_summary(self):

        total_quantity = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        Inventory.quantity
                    ),
                    0
                )
            )
            .scalar()
        )

        medicines_count = (
            self.db.query(
                func.count(
                    Inventory.inventory_id
                )
            )
            .scalar()
        )

        return {
            "medicines_count":
            medicines_count,

            "total_quantity":
            total_quantity
        }