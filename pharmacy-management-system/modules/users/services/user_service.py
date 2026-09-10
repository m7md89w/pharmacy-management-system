from modules.auth.utils.password_handler import PasswordHandler
from modules.roles.repository.role_repository import RoleRepository
from modules.users.repository.user_repository import UserRepository


class UserService:

  def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
    self.user_repo = user_repo
    self.role_repo = role_repo

  def create_user(self, data: dict):
    role = self.role_repo.get_by_id(data["role_id"])

    if not role:
      raise ValueError("Role not found")

    existing_user = self.user_repo.get_by_username(data["username"])

    if existing_user:
      raise ValueError("Username already exists")

    # دعم استقبال كلمة المرور سواء عبر مفتاح "password" أو "password_hash"
    raw_password = data.get("password") or data.get("password_hash")
    if not raw_password:
      raise ValueError("Password is required")

    # تشفير كلمة المرور وتخزينها في password_hash
    data["password_hash"] = PasswordHandler.hash_password(raw_password)

    # إزالة مفتاح password العادي لكي لا يسبب مشكلة مع أعمدة جدول الـ User
    if "password" in data:
      data.pop("password")

    return self.user_repo.create(data)

  def get_user(self, user_id: int):
    user = self.user_repo.get_by_id(user_id)

    if not user:
      raise ValueError("User not found")

    return user

  def get_all_users(self):
    return self.user_repo.get_all()

  def update_user(self, user, data: dict):
    # إذا تم إرسال كلمة مرور جديدة، يتم تشفيرها
    raw_password = data.get("password") or data.get("password_hash")
    if raw_password:
      data["password_hash"] = PasswordHandler.hash_password(raw_password)
      if "password" in data:
        data.pop("password")
    else:
      # إذا لم يتم إرسال كلمة مرور جديدة، نمنع الكتابة فوق الـ password_hash بقيمة فارغة
      data.pop("password", None)
      data.pop("password_hash", None)

    fields = ["full_name", "email", "phone", "password_hash", "role_id"]

    for field in fields:
      if field in data:
        setattr(user, field, data[field])

    return self.user_repo.update(user)

  def deactivate_user(self, user):
    return self.user_repo.deactivate(user)