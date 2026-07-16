from datetime import date

from modules.purchases.repository.purchase_order_repository import PurchaseOrderRepository
from modules.suppliers.repository.supplier_repository import SupplierRepository
from modules.purchases.repository.purchase_item_repository import PurchaseItemRepository
from modules.medicines.repository.medicine_batch_repository import MedicineBatchRepository
from modules.stock_movements.repository.stock_movement_repository import StockMovementRepository
from modules.inventory.repository.inventory_repository import InventoryRepository
from modules.audit_logs.repository.audit_log_repository import AuditLogRepository


class PurchaseOrderService:

    VALID_STATUSES = [
        "PENDING",
        "RECEIVED",
        "CANCELLED"
    ]

    def __init__(
        self,
        order_repo: PurchaseOrderRepository,
        supplier_repo: SupplierRepository,
        item_repo: PurchaseItemRepository,
        batch_repo: MedicineBatchRepository,
        movement_repo: StockMovementRepository,
        inventory_repo: InventoryRepository,
        audit_repo: AuditLogRepository
    ):
        self.order_repo = order_repo
        self.supplier_repo = supplier_repo
        self.item_repo = item_repo
        self.batch_repo = batch_repo
        self.movement_repo = movement_repo
        self.inventory_repo = inventory_repo
        self.audit_repo = audit_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_order(
        self,
        data: dict
    ):

        supplier = self.supplier_repo.get_by_id(
            data["supplier_id"]
        )

        if not supplier:
            raise ValueError(
                "Supplier not found"
            )

        data.setdefault(
            "status",
            "PENDING"
        )

        data.setdefault(
            "total_amount",
            0
        )

        order = self.order_repo.create(
            data
        )

        self.audit_repo.create({
            "user_id": order.user_id,
            "action": "CREATE_PURCHASE",
            "table_name": "purchase_orders",
            "record_id": order.purchase_id,
            "details":
                f"Purchase Order #{order.purchase_id} created"
        })

        return order

    # ==================================================
    # GET
    # ==================================================
    def get_order(
        self,
        purchase_id: int
    ):

        order = self.order_repo.get_by_id(
            purchase_id
        )

        if not order:
            raise ValueError(
                "Purchase order not found"
            )

        return order

    def get_all_orders(
        self
    ):

        return self.order_repo.get_all()
    

        # ==================================================
    # UPDATE
    # ==================================================
    def update_order(
        self,
        order,
        data: dict
    ):

        if "status" in data:

            new_status = data["status"]

            if new_status not in self.VALID_STATUSES:
                raise ValueError(
                    "Invalid status"
                )

            if (
                order.status == "RECEIVED"
                and
                new_status != "RECEIVED"
            ):
                raise ValueError(
                    "Cannot modify received order"
                )

            # ==================================================
            # RECEIVE PURCHASE
            # ==================================================
            if (
                new_status == "RECEIVED"
                and
                order.status != "RECEIVED"
            ):

                items = self.item_repo.get_by_purchase(
                    order.purchase_id
                )

                if not items:
                    raise ValueError(
                        "Purchase order has no items"
                    )

                for item in items:

                    if item.batch_id:
                        continue

                    if item.quantity <= 0:
                        raise ValueError(
                            f"Purchase item #{item.purchase_item_id} has invalid quantity."
                        )

                    # ==========================================
                    # CHECK SUPPLIER BATCH NUMBER
                    # ==========================================
                    if self.batch_repo.batch_number_has_different_dates(
                        item.medicine_id,
                        item.batch_number,
                        item.manufacture_date,
                        item.expiry_date
                    ):
                        raise ValueError(
                            "Batch number already exists with different manufacture or expiry date."
                        )

                    # ==========================================
                    # CREATE INTERNAL BATCH
                    # ==========================================
                    batch = self.batch_repo.create({
                        "medicine_id": item.medicine_id,
                        "supplier_id": order.supplier_id,
                        "batch_number": item.batch_number,
                        "quantity": item.quantity,
                        "purchase_price": item.unit_cost,
                        "selling_price": item.selling_price,
                        "manufacture_date": item.manufacture_date,
                        "expiry_date": item.expiry_date
                    })

                    # ==========================================
                    # UPDATE INVENTORY
                    # ==========================================
                    inventory = self.inventory_repo.get_by_medicine(
                        item.medicine_id
                    )

                    if inventory:

                        inventory.quantity += item.quantity

                        self.inventory_repo.update(
                            inventory
                        )

                    else:

                        self.inventory_repo.create({
                            "medicine_id": item.medicine_id,
                            "quantity": item.quantity,
                            "min_stock_level": 0,
                            "location": None
                        })

                    # ==========================================
                    # STOCK MOVEMENT
                    # ==========================================
                    self.movement_repo.create({
                        "batch_id": batch.batch_id,
                        "movement_type": "PURCHASE",
                        "quantity_change": item.quantity,
                        "reference_type": "PURCHASE",
                        "reference_id": order.purchase_id,
                        "notes": f"Purchase Order #{order.purchase_id}",
                        "created_by": order.user_id
                    })

                    # ==========================================
                    # LINK PURCHASE ITEM TO BATCH
                    # ==========================================
                    item.batch_id = batch.batch_id

                    self.item_repo.update(
                        item
                    )

                order.received_date = date.today()

                self.audit_repo.create({
                    "user_id": order.user_id,
                    "action": "RECEIVE_PURCHASE",
                    "table_name": "purchase_orders",
                    "record_id": order.purchase_id,
                    "details": f"Purchase Order #{order.purchase_id} received"
                })

            elif order.status != new_status:

                self.audit_repo.create({
                    "user_id": order.user_id,
                    "action": "UPDATE_PURCHASE_STATUS",
                    "table_name": "purchase_orders",
                    "record_id": order.purchase_id,
                    "details": f"Status changed from {order.status} to {new_status}"
                })

            order.status = new_status

        if "received_date" in data:
            order.received_date = data["received_date"]

        return self.order_repo.update(
            order
        )
    
        # ==================================================
    # DELETE
    # ==================================================
    def delete_order(
        self,
        order
    ):

        if order.status == "RECEIVED":
            raise ValueError(
                "Cannot delete received order"
            )

        self.audit_repo.create({
            "user_id": order.user_id,
            "action": "DELETE_PURCHASE",
            "table_name": "purchase_orders",
            "record_id": order.purchase_id,
            "details":
                f"Purchase Order #{order.purchase_id} deleted"
        })

        return self.order_repo.delete(
            order
        )

    # ==================================================
    # GET BY SUPPLIER
    # ==================================================
    def get_orders_by_supplier(
        self,
        supplier_id: int
    ):

        supplier = self.supplier_repo.get_by_id(
            supplier_id
        )

        if not supplier:
            raise ValueError(
                "Supplier not found"
            )

        return self.order_repo.get_by_supplier(
            supplier_id
        )

    # ==================================================
    # GET BY STATUS
    # ==================================================
    def get_orders_by_status(
        self,
        status: str
    ):

        if status not in self.VALID_STATUSES:
            raise ValueError(
                "Invalid status"
            )

        return self.order_repo.get_by_status(
            status
        )
    

