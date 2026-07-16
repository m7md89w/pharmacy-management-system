from modules.expired_medicines.repository.expired_medicine_item_repository import (
    ExpiredMedicineItemRepository
)
from modules.expired_medicines.repository.expired_medicine_repository import (
    ExpiredMedicineRepository
)
from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)
from modules.inventory.repository.inventory_repository import (
    InventoryRepository
)
from modules.stock_movements.repository.stock_movement_repository import (
    StockMovementRepository
)


class ExpiredMedicineItemService:

    def __init__(
        self,
        item_repo: ExpiredMedicineItemRepository,
        expired_repo: ExpiredMedicineRepository,
        medicine_repo: MedicineRepository,
        batch_repo: MedicineBatchRepository,
        inventory_repo: InventoryRepository,
        movement_repo: StockMovementRepository
    ):
        self.item_repo = item_repo
        self.expired_repo = expired_repo
        self.medicine_repo = medicine_repo
        self.batch_repo = batch_repo
        self.inventory_repo = inventory_repo
        self.movement_repo = movement_repo

    def create_item(
        self,
        data: dict
    ):

        expired = self.expired_repo.get_by_id(
            data["expired_id"]
        )

        if not expired:
            raise ValueError(
                "Expired record not found"
            )

        medicine = self.medicine_repo.get_by_id(
            data["medicine_id"]
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        batch = self.batch_repo.get_by_id(
            data["batch_id"]
        )

        if not batch:
            raise ValueError(
                "Batch not found"
            )

        quantity = int(
            data["quantity"]
        )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        if batch.quantity < quantity:
            raise ValueError(
                "Insufficient batch quantity"
            )

        item = self.item_repo.create(
            data
        )

        # خصم من الباتش
        batch.quantity -= quantity

        self.batch_repo.update(
            batch
        )

        # خصم من الانفنتري
        inventory = (
            self.inventory_repo.get_by_medicine(
                medicine.medicine_id
            )
        )

        if inventory:

            inventory.quantity -= quantity

            if inventory.quantity < 0:
                inventory.quantity = 0

            self.inventory_repo.update(
                inventory
            )

        # إنشاء حركة مخزون
        self.movement_repo.create({
            "batch_id": batch.batch_id,
            "movement_type": "EXPIRED",
            "quantity_change": -quantity,
            "reference_type": "EXPIRED",
            "reference_id": expired.expired_id,
            "notes": (
                f"Expired Medicine "
                f"#{expired.expired_id}"
            ),
            "created_by": expired.user_id
        })

        return item

    def get_item(
        self,
        expired_item_id: int
    ):

        item = self.item_repo.get_by_id(
            expired_item_id
        )

        if not item:
            raise ValueError(
                "Expired item not found"
            )

        return item

    def get_items_by_expired(
        self,
        expired_id: int
    ):
        return self.item_repo.get_by_expired(
            expired_id
        )

    def delete_item(
        self,
        item
    ):
        return self.item_repo.delete(
            item
        )