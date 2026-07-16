from flask import (
    Blueprint,
    request,
    jsonify
)

from database.session import SessionLocal

from modules.notifications.repository.notification_repository import (
    NotificationRepository
)
from modules.notifications.services.notification_service import (
    NotificationService
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)


notification_controller = Blueprint(
    "notifications",
    __name__,
    url_prefix="/notifications"
)


@notification_controller.route(
    "/",
    methods=["POST"]
)
@auth_required
@role_required([1, 2])
def create_notification():

    db = SessionLocal()

    try:

        notification_repo = (
            NotificationRepository(db)
        )

        medicine_repo = (
            MedicineRepository(db)
        )

        batch_repo = (
            MedicineBatchRepository(db)
        )

        service = NotificationService(
            notification_repo,
            medicine_repo,
            batch_repo
        )

        notification = (
            service.create_notification(
                request.get_json()
            )
        )

        return jsonify({
            "message":
            "Notification created successfully",
            "notification_id":
            notification.notification_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@notification_controller.route(
    "/",
    methods=["GET"]
)
@auth_required
def get_notifications():

    db = SessionLocal()

    try:

        service = NotificationService(
            NotificationRepository(db),
            MedicineRepository(db),
            MedicineBatchRepository(db)
        )

        notifications = (
            service.get_all_notifications()
        )

        return jsonify([
            {
                "notification_id":
                n.notification_id,
                "type":
                n.type,
                "medicine_id":
                n.medicine_id,
                "batch_id":
                n.batch_id,
                "message":
                n.message,
                "severity":
                n.severity,
                "is_read":
                n.is_read,
                "created_at":
                str(n.created_at)
            }
            for n in notifications
        ])

    finally:
        db.close()


@notification_controller.route(
    "/unread",
    methods=["GET"]
)
@auth_required
def get_unread_notifications():

    db = SessionLocal()

    try:

        service = NotificationService(
            NotificationRepository(db),
            MedicineRepository(db),
            MedicineBatchRepository(db)
        )

        notifications = (
            service.get_unread_notifications()
        )

        return jsonify([
            {
                "notification_id":
                n.notification_id,
                "type":
                n.type,
                "message":
                n.message,
                "severity":
                n.severity,
                "is_read":
                n.is_read
            }
            for n in notifications
        ])

    finally:
        db.close()


@notification_controller.route(
    "/<int:notification_id>",
    methods=["GET"]
)
@auth_required
def get_notification(
    notification_id
):

    db = SessionLocal()

    try:

        service = NotificationService(
            NotificationRepository(db),
            MedicineRepository(db),
            MedicineBatchRepository(db)
        )

        notification = (
            service.get_notification(
                notification_id
            )
        )

        return jsonify({
            "notification_id":
            notification.notification_id,
            "type":
            notification.type,
            "medicine_id":
            notification.medicine_id,
            "batch_id":
            notification.batch_id,
            "message":
            notification.message,
            "severity":
            notification.severity,
            "is_read":
            notification.is_read,
            "created_at":
            str(notification.created_at)
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@notification_controller.route(
    "/<int:notification_id>/read",
    methods=["PUT"]
)
@auth_required
def mark_as_read(
    notification_id
):

    db = SessionLocal()

    try:

        service = NotificationService(
            NotificationRepository(db),
            MedicineRepository(db),
            MedicineBatchRepository(db)
        )

        notification = (
            service.get_notification(
                notification_id
            )
        )

        service.mark_as_read(
            notification
        )

        return jsonify({
            "message":
            "Notification marked as read"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@notification_controller.route(
    "/<int:notification_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_notification(
    notification_id
):

    db = SessionLocal()

    try:

        service = NotificationService(
            NotificationRepository(db),
            MedicineRepository(db),
            MedicineBatchRepository(db)
        )

        notification = (
            service.get_notification(
                notification_id
            )
        )

        service.delete_notification(
            notification
        )

        return jsonify({
            "message":
            "Notification deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()