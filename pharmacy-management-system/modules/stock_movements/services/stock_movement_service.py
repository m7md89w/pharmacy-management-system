from modules.stock_movements.repository.stock_movement_repository import StockMovementRepository
from modules.medicines.repository.medicine_batch_repository import MedicineBatchRepository


class StockMovementService:

    VALID_MOVEMENT_TYPES = [
        "PURCHASE",
        "SALE",
        "ADJUSTMENT",
        "RETURN",
        "DAMAGE",
        "EXPIRED"
    ]

    VALID_REFERENCE_TYPES = [
        "PURCHASE",
        "SALE",
        "RETURN",
        "EXPIRED",
        "ADJUSTMENT"
    ]

    def __init__(
        self,
        movement_repo: StockMovementRepository,
        batch_repo: MedicineBatchRepository
    ):
        self.movement_repo = movement_repo
        self.batch_repo = batch_repo

    def create_movement(
        self,
        data: dict
    ):

        batch = self.batch_repo.get_by_id(
            data["batch_id"]
        )

        if not batch:
            raise ValueError(
                "Batch not found"
            )

        if (
            data["movement_type"]
            not in self.VALID_MOVEMENT_TYPES
        ):
            raise ValueError(
                "Invalid movement type"
            )

        if (
            data["reference_type"]
            not in self.VALID_REFERENCE_TYPES
        ):
            raise ValueError(
                "Invalid reference type"
            )

        quantity_change = int(
            data["quantity_change"]
        )

        if quantity_change == 0:
            raise ValueError(
                "Quantity change cannot be zero"
            )

        movement = self.movement_repo.create(
            data
        )

        return movement

    def get_movement(
        self,
        movement_id: int
    ):

        movement = self.movement_repo.get_by_id(
            movement_id
        )

        if not movement:
            raise ValueError(
                "Stock movement not found"
            )

        return movement

    def get_all_movements(self):
        return self.movement_repo.get_all()

    def get_batch_movements(
        self,
        batch_id: int
    ):
        return self.movement_repo.get_by_batch(
            batch_id
        )

    def delete_movement(
        self,
        movement
    ):
        return self.movement_repo.delete(
            movement
        )