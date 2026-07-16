from modules.notifications.repository.notification_repository import (
    NotificationRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)

from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)


class NotificationService:

    VALID_TYPES = [
        "LOW_STOCK",
        "EXPIRY",
        "SYSTEM",
        "OTHER"
    ]

    VALID_SEVERITIES = [
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    def __init__(
        self,
        notification_repo: NotificationRepository,
        medicine_repo: MedicineRepository,
        batch_repo: MedicineBatchRepository
    ):
        self.notification_repo = (
            notification_repo
        )
        self.medicine_repo = (
            medicine_repo
        )
        self.batch_repo = (
            batch_repo
        )

    def create_notification(
        self,
        data: dict
    ):

        notification_type = data.get(
            "type"
        )

        if (
            notification_type
            not in self.VALID_TYPES
        ):
            raise ValueError(
                "Invalid notification type"
            )

        severity = data.get(
            "severity",
            "MEDIUM"
        )

        if (
            severity
            not in self.VALID_SEVERITIES
        ):
            raise ValueError(
                "Invalid severity"
            )

        if data.get("medicine_id"):

            medicine = (
                self.medicine_repo.get_by_id(
                    data["medicine_id"]
                )
            )

            if not medicine:
                raise ValueError(
                    "Medicine not found"
                )

        if data.get("batch_id"):

            batch = (
                self.batch_repo.get_by_id(
                    data["batch_id"]
                )
            )

            if not batch:
                raise ValueError(
                    "Batch not found"
                )

        data.setdefault(
            "is_read",
            False
        )

        return (
            self.notification_repo.create(
                data
            )
        )

    def get_notification(
        self,
        notification_id: int
    ):

        notification = (
            self.notification_repo.get_by_id(
                notification_id
            )
        )

        if not notification:
            raise ValueError(
                "Notification not found"
            )

        return notification

    def get_all_notifications(
        self
    ):
        return (
            self.notification_repo.get_all()
        )

    def get_unread_notifications(
        self
    ):
        return (
            self.notification_repo.get_unread()
        )

    def mark_as_read(
        self,
        notification
    ):

        notification.is_read = True

        return (
            self.notification_repo.update(
                notification
            )
        )

    def delete_notification(
        self,
        notification
    ):

        return (
            self.notification_repo.delete(
                notification
            )
        )