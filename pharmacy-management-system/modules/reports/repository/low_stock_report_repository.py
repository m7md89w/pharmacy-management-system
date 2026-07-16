from models.all_models import Inventory


class LowStockReportRepository:

    def __init__(self, db):
        self.db = db

    def get_low_stock(self):

        inventories = (
            self.db.query(
                Inventory
            )
            .filter(
                Inventory.quantity
                <= Inventory.min_stock_level
            )
            .all()
        )

        return inventories