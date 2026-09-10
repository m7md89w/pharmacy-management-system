from datetime import date
from modules.audit_logs.repository.audit_log_repository import AuditLogRepository


class AuditLogService:

  def __init__(self, repo: AuditLogRepository):
    self.repo = repo

  def create_log(self, data: dict):
    return self.repo.create(data)

  def _format_log(self, log):
    """دالة مساعدة لتحويل كائن قاعدة البيانات إلى قاموس جاهز للإرسال للواجهة"""
    return {
        "log_id": getattr(log, "id", getattr(log, "log_id", None)),
        "user_id": log.user_id,
        "user_email": log.user.email if getattr(log, "user", None) else "N/A",
        "username": (
            log.user.username if getattr(log, "user", None) else "System"
        ),
        "action": log.action,
        "table_name": getattr(log, "table_name", None),
        "record_id": getattr(log, "record_id", None),
        "details": getattr(
            log, "details", getattr(log, "description", "N/A")
        ),
        "created_at": (
            log.created_at.isoformat()
            if getattr(log, "created_at", None)
            else (
                log.timestamp.isoformat()
                if getattr(log, "timestamp", None)
                else None
            )
        ),
    }

  def get_all_logs(self):
    logs = self.repo.get_all()
    return [self._format_log(log) for log in logs]

  def get_user_logs(self, user_id: int):
    logs = self.repo.get_by_user(user_id)
    return [self._format_log(log) for log in logs]

  def get_filtered_logs(
      self,
      user_email: str | None = None,
      action: str | None = None,
      start_date: date | None = None,
      end_date: date | None = None,
  ):
    """جلب سجلات التدقيق مفلترة بناءً على الإيميل، نوع الإجراء، وتاريخ البداية والنهاية."""
    logs = self.repo.get_filtered(
        user_email=user_email,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )
    return [self._format_log(log) for log in logs]