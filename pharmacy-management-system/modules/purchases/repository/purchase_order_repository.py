from sqlalchemy.orm import Session

from models.all_models import PurchaseOrder


class PurchaseOrderRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, order_data: dict) -> PurchaseOrder:
        order = PurchaseOrder(**order_data)

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def get_by_id(self, purchase_id: int) -> PurchaseOrder | None:
        return (
            self.db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.purchase_id == purchase_id
            )
            .first()
        )

    def get_all(self) -> list[PurchaseOrder]:
        return (
            self.db.query(PurchaseOrder)
            .all()
        )

    def update(
        self,
        purchase_order: PurchaseOrder
    ) -> PurchaseOrder:

        self.db.commit()
        self.db.refresh(purchase_order)

        return purchase_order

    def delete(
        self,
        purchase_order: PurchaseOrder
    ):

        self.db.delete(purchase_order)
        self.db.commit()

    def get_by_supplier(
        self,
        supplier_id: int
    ) -> list[PurchaseOrder]:

        return (
            self.db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.supplier_id == supplier_id
            )
            .all()
        )

    def get_by_status(
        self,
        status: str
    ) -> list[PurchaseOrder]:

        return (
            self.db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.status == status
            )
            .all()
        )