from modules.inventory.repository.inventory_repository import InventoryRepository
from modules.medicines.repository.medicine_repository import MedicineRepository


class InventoryService:

    def __init__(
        self,
        inventory_repo: InventoryRepository,
        medicine_repo: MedicineRepository
    ):
        self.inventory_repo = inventory_repo
        self.medicine_repo = medicine_repo

    def create_inventory(
        self,
        data: dict
    ):

        medicine = self.medicine_repo.get_by_id(
            data["medicine_id"]
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        existing = self.inventory_repo.get_by_medicine(
            data["medicine_id"]
        )

        if existing:
            raise ValueError(
                "Inventory already exists for this medicine"
            )

        data.setdefault(
            "quantity",
            0
        )

        data.setdefault(
            "min_stock_level",
            0
        )

        return self.inventory_repo.create(
            data
        )

    def get_inventory(
        self,
        inventory_id: int
    ):

        inventory = self.inventory_repo.get_by_id(
            inventory_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        return inventory

    def get_inventory_by_medicine(
        self,
        medicine_id: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        return inventory

    def get_all_inventory(self):

        return self.inventory_repo.get_all()

    def update_inventory(
        self,
        inventory,
        data: dict
    ):

        if "quantity" in data:

            quantity = int(
                data["quantity"]
            )

            if quantity < 0:
                raise ValueError(
                    "Quantity cannot be negative"
                )

            inventory.quantity = quantity

        if "min_stock_level" in data:

            level = int(
                data["min_stock_level"]
            )

            if level < 0:
                raise ValueError(
                    "Minimum stock cannot be negative"
                )

            inventory.min_stock_level = level

        if "location" in data:

            inventory.location = data[
                "location"
            ]

        return self.inventory_repo.update(
            inventory
        )

    def delete_inventory(
        self,
        inventory
    ):

        return self.inventory_repo.delete(
            inventory
        )

    def increase_stock(
        self,
        medicine_id: int,
        quantity: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        inventory.quantity += quantity

        return self.inventory_repo.update(
            inventory
        )

    def decrease_stock(
        self,
        medicine_id: int,
        quantity: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        if inventory.quantity < quantity:
            raise ValueError(
                "Insufficient stock"
            )

        inventory.quantity -= quantity

        return self.inventory_repo.update(
            inventory
        )

    def get_low_stock(self):

        inventories = self.inventory_repo.get_all()

        return [
            inventory
            for inventory in inventories
            if inventory.quantity <= inventory.min_stock_level
        ]