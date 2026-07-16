from sqlalchemy.orm import Session

from models.all_models import Notification


class NotificationRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        notification = Notification(
            **data
        )

        self.db.add(
            notification
        )
        self.db.commit()
        self.db.refresh(
            notification
        )

        return notification

    def get_by_id(
        self,
        notification_id: int
    ):

        return (
            self.db.query(
                Notification
            )
            .filter(
                Notification.notification_id
                == notification_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(
                Notification
            )
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    def get_unread(self):

        return (
            self.db.query(
                Notification
            )
            .filter(
                Notification.is_read.is_(
                    False
                )
            )
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    def update(
        self,
        notification
    ):

        self.db.commit()
        self.db.refresh(
            notification
        )

        return notification

    def delete(
        self,
        notification
    ):

        self.db.delete(
            notification
        )
        self.db.commit()