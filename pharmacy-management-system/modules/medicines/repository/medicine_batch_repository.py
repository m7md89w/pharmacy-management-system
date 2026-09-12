from datetime import date

from models.all_models import MedicineBatch
from sqlalchemy.orm import Session


class MedicineBatchRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, batch_data: dict) -> MedicineBatch:
        batch = MedicineBatch(**batch_data)
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_by_id(self, batch_id: int) -> MedicineBatch | None:
        return (
            self.db.query(MedicineBatch)
            .filter(MedicineBatch.batch_id == batch_id)
            .first()
        )

    def get_all(self) -> list[MedicineBatch]:
        return self.db.query(MedicineBatch).all()

    def update(self, batch: MedicineBatch) -> MedicineBatch:
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def delete(self, batch: MedicineBatch):
        self.db.delete(batch)
        self.db.commit()

    def get_by_medicine_id(self, medicine_id: int) -> list[MedicineBatch]:
        return (
            self.db.query(MedicineBatch)
            .filter(MedicineBatch.medicine_id == medicine_id)
            .all()
        )

    def get_by_supplier_id(self, supplier_id: int) -> list[MedicineBatch]:
        return (
            self.db.query(MedicineBatch)
            .filter(MedicineBatch.supplier_id == supplier_id)
            .all()
        )

    def get_available_batches(self, medicine_id: int) -> list[MedicineBatch]:
        return (
            self.db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity > 0,
                MedicineBatch.expiry_date > date.today()  # noqa: DTZ011
            )
            .order_by(
                MedicineBatch.expiry_date.asc(),
                MedicineBatch.created_at.asc()
            )
            .all()
        )

    # ==================================================
    # GET ALL BY MEDICINE & BATCH NUMBER
    # ==================================================
    def get_all_by_medicine_and_batch(
        self, 
        medicine_id: int, 
        batch_number: str
    ) -> list[MedicineBatch]:
        return (
            self.db.query(MedicineBatch)
            .filter(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.batch_number == batch_number
            )
            .all()
        )
    

        # ==================================================
    # GET SINGLE BATCH
    # ==================================================
    def get_by_medicine_batch_and_dates(
        self,
        medicine_id: int,
        batch_number: str,
        manufacture_date,
        expiry_date
    ) -> MedicineBatch | None:

        return (

            self.db.query(
                MedicineBatch
            )

            .filter(

                MedicineBatch.medicine_id
                == medicine_id,

                MedicineBatch.batch_number
                == batch_number,

                MedicineBatch.manufacture_date
                == manufacture_date,

                MedicineBatch.expiry_date
                == expiry_date

            )

            .first()

        )

    # ==================================================
    # CHECK IF SAME BATCH NUMBER HAS DIFFERENT DATES
    # ==================================================
    def batch_number_has_different_dates(
        self,
        medicine_id: int,
        batch_number: str,
        manufacture_date,
        expiry_date
    ) -> bool:

        batches = self.get_all_by_medicine_and_batch(
            medicine_id,
            batch_number
        )

        for batch in batches:

            if (

                batch.manufacture_date
                != manufacture_date

                or

                batch.expiry_date
                != expiry_date

            ):

                return True

        return False


    # ==================================================
    # INCREASE BATCH QUANTITY
    # ==================================================
    def increase_quantity(
        self,
        batch: MedicineBatch,
        quantity: int,
        purchase_price,
        selling_price
    ):

        batch.quantity += quantity

        batch.purchase_price = purchase_price

        batch.selling_price = selling_price

        self.db.commit()

        self.db.refresh(batch)

        return batch