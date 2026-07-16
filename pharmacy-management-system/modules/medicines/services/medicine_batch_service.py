from modules.medicines.repository.medicine_batch_repository import MedicineBatchRepository
from modules.medicines.repository.medicine_repository import MedicineRepository
from modules.suppliers.repository.supplier_repository import SupplierRepository


class MedicineBatchService:

    def __init__(
        self,
        batch_repo: MedicineBatchRepository,
        medicine_repo: MedicineRepository,
        supplier_repo: SupplierRepository
    ):
        self.batch_repo = batch_repo
        self.medicine_repo = medicine_repo
        self.supplier_repo = supplier_repo

    def create_batch(self, data: dict):

        medicine = self.medicine_repo.get_by_id(
            data["medicine_id"]
        )

        if not medicine:
            raise ValueError("Medicine not found")

        if data.get("supplier_id"):
            supplier = self.supplier_repo.get_by_id(
                data["supplier_id"]
            )

            if not supplier:
                raise ValueError("Supplier not found")

        if int(data["quantity"]) < 0:
            raise ValueError("Quantity cannot be negative")

        if float(data["purchase_price"]) < 0:
            raise ValueError("Purchase price cannot be negative")

        if float(data["selling_price"]) < 0:
            raise ValueError("Selling price cannot be negative")

        return self.batch_repo.create(data)

    def get_batch(self, batch_id: int):

        batch = self.batch_repo.get_by_id(batch_id)

        if not batch:
            raise ValueError("Batch not found")

        return batch

    def get_all_batches(self):
        return self.batch_repo.get_all()

    def update_batch(self, batch, data: dict):

        fields = [
            "batch_number",
            "quantity",
            "purchase_price",
            "selling_price",
            "manufacture_date",
            "expiry_date"
        ]

        for field in fields:
            if field in data:
                setattr(batch, field, data[field])

        return self.batch_repo.update(batch)

    def delete_batch(self, batch):
        return self.batch_repo.delete(batch)

    def get_batches_by_medicine(
        self,
        medicine_id: int
    ):
        return self.batch_repo.get_by_medicine_id(
            medicine_id
        )

    def get_batches_by_supplier(
        self,
        supplier_id: int
    ):
        return self.batch_repo.get_by_supplier_id(
            supplier_id
        )