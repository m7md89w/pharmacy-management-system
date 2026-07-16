from datetime import datetime

from modules.prescriptions.repository.prescription_repository import (
    PrescriptionRepository
)
from modules.customers.repository.customer_repository import (
    CustomerRepository
)


class PrescriptionService:

    def __init__(
        self,
        prescription_repo: PrescriptionRepository,
        customer_repo: CustomerRepository
    ):
        self.prescription_repo = (
            prescription_repo
        )
        self.customer_repo = (
            customer_repo
        )

    def create_prescription(
        self,
        data: dict
    ):

        customer_id = data.get(
            "customer_id"
        )

        if customer_id:

            customer = (
                self.customer_repo.get_by_id(
                    customer_id
                )
            )

            if not customer:
                raise ValueError(
                    "Customer not found"
                )

        if data.get("issue_date"):

            data["issue_date"] = (
                datetime.strptime(
                    data["issue_date"],
                    "%Y-%m-%d"
                ).date()
            )

        return (
            self.prescription_repo.create(
                data
            )
        )

    def get_prescription(
        self,
        prescription_id: int
    ):

        prescription = (
            self.prescription_repo.get_by_id(
                prescription_id
            )
        )

        if not prescription:
            raise ValueError(
                "Prescription not found"
            )

        return prescription

    def get_all_prescriptions(
        self
    ):
        return (
            self.prescription_repo.get_all()
        )

    def get_by_customer(
        self,
        customer_id: int
    ):
        return (
            self.prescription_repo.get_by_customer(
                customer_id
            )
        )

    def update_prescription(
        self,
        prescription,
        data: dict
    ):

        if "doctor_name" in data:
            prescription.doctor_name = data[
                "doctor_name"
            ]

        if "prescription_image" in data:
            prescription.prescription_image = data[
                "prescription_image"
            ]

        if (
            "issue_date" in data
            and data["issue_date"]
        ):
            prescription.issue_date = (
                datetime.strptime(
                    data["issue_date"],
                    "%Y-%m-%d"
                ).date()
            )

        if "notes" in data:
            prescription.notes = data[
                "notes"
            ]

        return (
            self.prescription_repo.update(
                prescription
            )
        )

    def delete_prescription(
        self,
        prescription
    ):

        return (
            self.prescription_repo.delete(
                prescription
            )
        )