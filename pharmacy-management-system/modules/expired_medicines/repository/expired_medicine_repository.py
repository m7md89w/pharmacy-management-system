from sqlalchemy.orm import Session
from models.all_models import ExpiredMedicine


class ExpiredMedicineRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        data: dict
    ) -> ExpiredMedicine:

        expired = ExpiredMedicine(**data)

        self.db.add(expired)
        self.db.commit()
        self.db.refresh(expired)

        return expired

    def get_by_id(
        self,
        expired_id: int
    ) -> ExpiredMedicine | None:

        return (
            self.db.query(ExpiredMedicine)
            .filter(
                ExpiredMedicine.expired_id == expired_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(ExpiredMedicine)
            .all()
        )

    def update(
        self,
        expired: ExpiredMedicine
    ):

        self.db.commit()
        self.db.refresh(expired)

        return expired

    def delete(
        self,
        expired: ExpiredMedicine
    ):

        self.db.delete(expired)
        self.db.commit()