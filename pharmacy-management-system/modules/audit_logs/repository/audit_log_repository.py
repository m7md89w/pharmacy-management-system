from sqlalchemy.orm import Session
from models.all_models import AuditLog


class AuditLogRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        log = AuditLog(
            **data
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def get_all(self):

        return (
            self.db.query(
                AuditLog
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

    def get_by_user(
        self,
        user_id: int
    ):

        return (
            self.db.query(
                AuditLog
            )
            .filter(
                AuditLog.user_id == user_id
            )
            .all()
        )