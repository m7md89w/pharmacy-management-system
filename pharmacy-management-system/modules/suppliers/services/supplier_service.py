from modules.suppliers.repository.supplier_repository import SupplierRepository


class SupplierService:

    def __init__(self, repo: SupplierRepository):
        self.repo = repo

    def create_supplier(self, data: dict):
        # 1. تحقق بسيط
        if not data.get("name"):
            raise ValueError("Supplier name is required")

        # 2. ممكن لاحقاً نضيف check للتكرار
        # existing = self.repo.search_by_name(data["name"])
        # if existing:
        #     raise ValueError("Supplier already exists")

        return self.repo.create(data)

    def get_supplier(self, supplier_id: int):
        supplier = self.repo.get_by_id(supplier_id)

        if not supplier:
            raise ValueError("Supplier not found")

        return supplier

    def get_all_suppliers(self):
        return self.repo.get_all()

    def update_supplier(self, supplier, data: dict):
        # supplier لازم يكون object موجود مسبقاً
        if "name" in data:
            supplier.name = data["name"]

        if "phone" in data:
            supplier.phone = data["phone"]

        if "email" in data:
            supplier.email = data["email"]

        if "address" in data:
            supplier.address = data["address"]

        return self.repo.update(supplier)

    def deactivate_supplier(self, supplier):
        return self.repo.deactivate(supplier)

    def search_suppliers(self, name: str):
        return self.repo.search_by_name(name)