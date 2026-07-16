from modules.prescriptions.repository.prescription_item_repository import (
    PrescriptionItemRepository
)
from modules.prescriptions.repository.prescription_repository import (
    PrescriptionRepository
)
from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)


class PrescriptionItemService:

    def __init__(
        self,
        item_repo: PrescriptionItemRepository,
        prescription_repo: PrescriptionRepository,
        medicine_repo: MedicineRepository
    ):
        self.item_repo = item_repo
        self.prescription_repo = (
            prescription_repo
        )
        self.medicine_repo = (
            medicine_repo
        )

    def create_item(
        self,
        data: dict
    ):

        prescription = (
            self.prescription_repo.get_by_id(
                data["prescription_id"]
            )
        )

        if not prescription:
            raise ValueError(
                "Prescription not found"
            )

        medicine = (
            self.medicine_repo.get_by_id(
                data["medicine_id"]
            )
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        return (
            self.item_repo.create(
                data
            )
        )

    def get_item(
        self,
        prescription_item_id: int
    ):

        item = (
            self.item_repo.get_by_id(
                prescription_item_id
            )
        )

        if not item:
            raise ValueError(
                "Prescription item not found"
            )

        return item

    def get_items_by_prescription(
        self,
        prescription_id: int
    ):

        return (
            self.item_repo.get_by_prescription(
                prescription_id
            )
        )

    def delete_item(
        self,
        item
    ):

        return (
            self.item_repo.delete(
                item
            )
        )