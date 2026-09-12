from sqlalchemy.orm import Session
from models.all_models import Medicine


class MedicineRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # CREATE
    # ==========================================
    def create(
        self,
        medicine_data: dict
    ) -> Medicine:

        try:
            medicine = Medicine(
                **medicine_data
            )

            self.db.add(medicine)
            self.db.commit()
            self.db.refresh(medicine)

            return medicine

        except Exception:
            self.db.rollback()
            raise

    # ==========================================
    # GET BY ID
    # ==========================================
    def get_by_id(
        self,
        medicine_id: int
    ) -> Medicine | None:

        return (
            self.db.query(Medicine)
            .filter(
                Medicine.medicine_id == medicine_id
            )
            .first()
        )

    # ==========================================
    # GET BY BARCODE (ACTIVE ONLY)
    # ==========================================
    def get_by_barcode(
        self,
        barcode: str
    ) -> Medicine | None:

        return (
            self.db.query(Medicine)
            .filter(
                Medicine.barcode == barcode,
                Medicine.is_active.is_(True)
            )
            .first()
        )

    # ==========================================
    # GET BY BARCODE (INCLUDING INACTIVE)
    # ==========================================
    def get_by_barcode_any(
        self,
        barcode: str
    ) -> Medicine | None:

        return (
            self.db.query(Medicine)
            .filter(
                Medicine.barcode == barcode
            )
            .first()
        )

    # ==========================================
    # GET ALL
    # ==========================================
    def get_all(
        self
    ) -> list[Medicine]:

        return (
            self.db.query(Medicine)
            .filter(
                Medicine.is_active.is_(True)
            )
            .all()
        )

    # ==========================================
    # SEARCH
    # ==========================================
    def search_by_name(
        self,
        name: str
    ) -> list[Medicine]:

        return (
            self.db.query(Medicine)
            .filter(
                (
                    Medicine.commercial_name.ilike(
                        f"%{name}%"
                    )
                )
                |
                (
                    Medicine.scientific_name.ilike(
                        f"%{name}%"
                    )
                ),
                Medicine.is_active.is_(True)
            )
            .all()
        )

    # ==========================================
    # UPDATE
    # ==========================================
    def update(
        self,
        medicine: Medicine
    ) -> Medicine:

        self.db.commit()
        self.db.refresh(medicine)

        return medicine

    # ==========================================
    # DEACTIVATE
    # ==========================================
    def deactivate(
        self,
        medicine: Medicine
    ) -> Medicine:

        medicine.is_active = False

        self.db.commit()
        self.db.refresh(medicine)

        return medicine

    # ==========================================
    # RESTORE
    # ==========================================
    def restore(
        self,
        medicine: Medicine
    ) -> Medicine:

        medicine.is_active = True

        self.db.commit()
        self.db.refresh(medicine)

        return medicine