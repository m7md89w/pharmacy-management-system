from datetime import date
from sqlalchemy.orm import Session, joinedload
from models.all_models import AuditLog, User


class AuditLogRepository:

  def __init__(self, db: Session):
    self.db = db

  def create(self, data: dict):
    log = AuditLog(**data)
    self.db.add(log)
    self.db.commit()
    self.db.refresh(log)
    return log

  def get_all(self):
    return (
        self.db.query(AuditLog)
        .options(
            joinedload(AuditLog.user)
        )  # تحميل بيانات المستخدم مسبقاً لمنع N+1 Query
        .order_by(AuditLog.created_at.desc())
        .all()
    )

  def get_by_user(self, user_id: int):
    return (
        self.db.query(AuditLog)
        .options(joinedload(AuditLog.user))
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

  def get_filtered(
      self,
      user_email: str | None = None,
      action: str | None = None,
      start_date: date | None = None,
      end_date: date | None = None,
  ):
    """جلب سجلات التدقيق مع دعم فلاتر متقدمة: إيميل الموظف، الأكشن، وتاريخ البداية والنهاية."""
    query = self.db.query(AuditLog).options(joinedload(AuditLog.user))

    # إذا تم تمرير إيميل، نقوم بالربط مع جدول المستخدمين للبحث الجزئي في البريد الإلكتروني
    if user_email:
      query = query.join(User, AuditLog.user_id == User.user_id).filter(
          User.email.ilike(f"%{user_email}%")
      )

    # فلترة حسب الإجراء (Action) بشرط ألا يكون الخيار هو الكل (ALL)
    if action and action != "ALL":
      query = query.filter(AuditLog.action == action)

    # فلترة حسب تاريخ البداية (مقارنة مع حقل created_at أو timestamp حسب الموديل)
    if start_date:
      query = query.filter(AuditLog.created_at >= start_date)

    # فلترة حسب تاريخ النهاية
    if end_date:
      query = query.filter(AuditLog.created_at <= end_date)

    return query.order_by(AuditLog.created_at.desc()).all()