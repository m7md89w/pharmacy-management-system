class AuditLogService:

    def __init__(
        self,
        repo
    ):
        self.repo = repo

    def create_log(
        self,
        data: dict
    ):
        return self.repo.create(
            data
        )

    def get_all_logs(self):
        return self.repo.get_all()

    def get_user_logs(
        self,
        user_id: int
    ):
        return self.repo.get_by_user(
            user_id
        )