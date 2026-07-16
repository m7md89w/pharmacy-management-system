from sqlalchemy.orm import Session

from models.all_models import Supplier


class SupplierRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, supplier_data: dict) -> Supplier:
        supplier = Supplier(**supplier_data)

        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)

        return supplier

    def get_by_id(self, supplier_id: int) -> Supplier | None:
        return (
            self.db.query(Supplier)
            .filter(Supplier.supplier_id == supplier_id)
            .first()
        )

    def get_all(self) -> list[Supplier]:
        return (
            self.db.query(Supplier)
            .filter(Supplier.is_active.is_(True))
            .all()
        )

    def update(self, supplier: Supplier) -> Supplier:
        self.db.commit()
        self.db.refresh(supplier)

        return supplier

    def deactivate(self, supplier: Supplier) -> Supplier:
        supplier.is_active = False

        self.db.commit()
        self.db.refresh(supplier)

        return supplier

    def search_by_name(self, name: str) -> list[Supplier]:
        return (
            self.db.query(Supplier)
            .filter(
                Supplier.name.ilike(f"%{name}%"),
                Supplier.is_active.is_(True)
            )
            .all()
        )