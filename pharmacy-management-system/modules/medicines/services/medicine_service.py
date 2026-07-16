from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)


class MedicineService:

    def __init__(
        self,
        repo: MedicineRepository
    ):
        self.repo = repo

    # ==========================================
    # CREATE
    # ==========================================
    def create_medicine(
        self,
        data: dict
    ):

        if not data.get("scientific_name"):
            raise ValueError(
                "Scientific name is required"
            )

        if not data.get("commercial_name"):
            raise ValueError(
                "Commercial name is required"
            )

        if not data.get("barcode"):
            raise ValueError(
                "Barcode is required"
            )

        # البحث حتى في الأدوية المحذوفة
        existing = self.repo.get_by_barcode_any(
            data["barcode"]
        )

        if existing:

            if not existing.is_active:
                raise ValueError(
                    "Medicine exists but is inactive."
                )

            raise ValueError(
                "Barcode already exists."
            )

        if data.get("selling_price") is None:
            raise ValueError(
                "Selling price is required"
            )

        if float(data["selling_price"]) < 0:
            raise ValueError(
                "Selling price cannot be negative"
            )

        return self.repo.create(data)

    # ==========================================
    # RESTORE
    # ==========================================
    def restore_medicine(
        self,
        barcode: str
    ):

        medicine = (
            self.repo.get_by_barcode_any(
                barcode
            )
        )

        if not medicine:
            raise ValueError(
                "Medicine not found."
            )

        if medicine.is_active:
            raise ValueError(
                "Medicine is already active."
            )

        return self.repo.restore(
            medicine
        )

    # ==========================================
    # GET BY ID
    # ==========================================
    def get_medicine(
        self,
        medicine_id: int
    ):

        medicine = self.repo.get_by_id(
            medicine_id
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        return medicine

    # ==========================================
    # GET ALL
    # ==========================================
    def get_all_medicines(self):
        return self.repo.get_all()

    # ==========================================
    # UPDATE
    # ==========================================
    def update_medicine(
        self,
        medicine,
        data: dict
    ):

        if (
            "barcode" in data
            and data["barcode"] != medicine.barcode
        ):

            existing = self.repo.get_by_barcode(
                data["barcode"]
            )

            if existing:
                raise ValueError(
                    "Barcode already exists."
                )

        fields = [
            "scientific_name",
            "commercial_name",
            "barcode",
            "description",
            "dosage_form",
            "requires_prescription",
            "category_id",
            "manufacturer_id",
            "selling_price"
        ]

        for field in fields:

            if field in data:

                if (
                    field == "selling_price"
                    and float(data[field]) < 0
                ):
                    raise ValueError(
                        "Selling price cannot be negative"
                    )

                setattr(
                    medicine,
                    field,
                    data[field]
                )

        return self.repo.update(
            medicine
        )

    # ==========================================
    # DEACTIVATE
    # ==========================================
    def deactivate_medicine(
        self,
        medicine
    ):
        return self.repo.deactivate(
            medicine
        )

    # ==========================================
    # SEARCH
    # ==========================================
    def search_medicines(
        self,
        name: str
    ):
        return self.repo.search_by_name(
            name
        )