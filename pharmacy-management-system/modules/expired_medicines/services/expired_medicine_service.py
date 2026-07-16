from modules.expired_medicines.repository.expired_medicine_repository import (
    ExpiredMedicineRepository
)
from modules.users.repository.user_repository import UserRepository


class ExpiredMedicineService:

    def __init__(
        self,
        expired_repo: ExpiredMedicineRepository,
        user_repo: UserRepository
    ):
        self.expired_repo = expired_repo
        self.user_repo = user_repo

    def create_expired(
        self,
        data: dict
    ):

        user = self.user_repo.get_by_id(
            data["user_id"]
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        return self.expired_repo.create(
            data
        )

    def get_expired(
        self,
        expired_id: int
    ):

        expired = self.expired_repo.get_by_id(
            expired_id
        )

        if not expired:
            raise ValueError(
                "Expired record not found"
            )

        return expired

    def get_all_expired(self):
        return self.expired_repo.get_all()

    def delete_expired(
        self,
        expired
    ):
        return self.expired_repo.delete(
            expired
        )