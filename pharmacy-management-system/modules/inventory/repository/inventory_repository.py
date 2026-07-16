from sqlalchemy.orm import Session

from models.all_models import Inventory


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        inventory_data: dict
    ) -> Inventory:

        inventory = Inventory(
            **inventory_data
        )

        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def get_by_id(
        self,
        inventory_id: int
    ) -> Inventory | None:

        return (
            self.db.query(Inventory)
            .filter(
                Inventory.inventory_id == inventory_id
            )
            .first()
        )

    def get_by_medicine(
        self,
        medicine_id: int
    ) -> Inventory | None:

        return (
            self.db.query(Inventory)
            .filter(
                Inventory.medicine_id == medicine_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(Inventory)
            .all()
        )

    def update(
        self,
        inventory: Inventory
    ):

        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def delete(
        self,
        inventory: Inventory
    ):

        self.db.delete(inventory)
        self.db.commit()