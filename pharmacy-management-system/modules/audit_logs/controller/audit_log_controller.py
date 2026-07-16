from flask import (
    Blueprint,
    jsonify
)

from database.session import SessionLocal

from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)
from modules.audit_logs.services.audit_log_service import (
    AuditLogService
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

audit_log_controller = Blueprint(
    "audit_logs",
    __name__,
    url_prefix="/audit-logs"
)

@audit_log_controller.route(
    "/",
    methods=["GET"]
)
@auth_required
@role_required([1])
def get_logs():

    db = SessionLocal()

    try:

        repo = AuditLogRepository(db)
        service = AuditLogService(repo)

        logs = service.get_all_logs()

        return jsonify([
            {
                "log_id":
                log.log_id,
                "user_id":
                log.user_id,
                "action":
                log.action,
                "table_name":
                log.table_name,
                "record_id":
                log.record_id,
                "details":
                log.details,
                "created_at":
                str(log.created_at)
            }
            for log in logs
        ])

    finally:
        db.close()