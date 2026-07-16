from sqlalchemy.orm import Session
from models.all_models import Prescription


class PrescriptionRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        prescription = Prescription(
            **data
        )

        self.db.add(
            prescription
        )

        self.db.commit()
        self.db.refresh(
            prescription
        )

        return prescription

    def get_by_id(
        self,
        prescription_id: int
    ):

        return (
            self.db.query(
                Prescription
            )
            .filter(
                Prescription.prescription_id
                == prescription_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(
                Prescription
            )
            .all()
        )

    def get_by_customer(
        self,
        customer_id: int
    ):

        return (
            self.db.query(
                Prescription
            )
            .filter(
                Prescription.customer_id
                == customer_id
            )
            .all()
        )

    def update(
        self,
        prescription
    ):

        self.db.commit()
        self.db.refresh(
            prescription
        )

        return prescription

    def delete(
        self,
        prescription
    ):

        self.db.delete(
            prescription
        )
        self.db.commit()