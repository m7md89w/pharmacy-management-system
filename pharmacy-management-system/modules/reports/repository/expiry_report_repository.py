from datetime import date
from models.all_models import MedicineBatch


class ExpiryReportRepository:

    def __init__(self, db):
        self.db = db

    def get_expired_batches(self):

        return (
            self.db.query(
                MedicineBatch
            )
            .filter(
                MedicineBatch.expiry_date
                < date.today()
            )
            .all()
        )