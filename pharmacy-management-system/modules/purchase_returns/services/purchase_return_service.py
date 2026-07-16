from decimal import Decimal

from modules.purchase_returns.repository.purchase_return_repository import (
    PurchaseReturnRepository
)

from modules.purchase_returns.repository.purchase_return_item_repository import (
    PurchaseReturnItemRepository
)

from modules.purchases.repository.purchase_order_repository import (
    PurchaseOrderRepository
)

from modules.purchases.repository.purchase_item_repository import (
    PurchaseItemRepository
)

from modules.users.repository.user_repository import (
    UserRepository
)

from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)

from modules.inventory.repository.inventory_repository import (
    InventoryRepository
)

from modules.stock_movements.repository.stock_movement_repository import (
    StockMovementRepository
)

from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)


class PurchaseReturnService:

    VALID_STATUSES = [
        "DRAFT",
        "COMPLETED",
        "CANCELLED"
    ]

    def __init__(
        self,
        return_repo: PurchaseReturnRepository,
        item_repo: PurchaseReturnItemRepository,
        purchase_repo: PurchaseOrderRepository,
        purchase_item_repo: PurchaseItemRepository,
        user_repo: UserRepository,
        batch_repo: MedicineBatchRepository,
        inventory_repo: InventoryRepository,
        movement_repo: StockMovementRepository,
        audit_repo: AuditLogRepository
    ):

        self.return_repo = return_repo
        self.item_repo = item_repo

        self.purchase_repo = purchase_repo
        self.purchase_item_repo = purchase_item_repo

        self.user_repo = user_repo

        self.batch_repo = batch_repo
        self.inventory_repo = inventory_repo
        self.movement_repo = movement_repo

        self.audit_repo = audit_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_return(
        self,
        data: dict
    ):

        purchase = self.purchase_repo.get_by_id(
            data["purchase_id"]
        )

        if not purchase:
            raise ValueError(
                "Purchase order not found"
            )

        if purchase.status != "RECEIVED":
            raise ValueError(
                "Only received purchase orders can be returned"
            )

        existing_draft = (
            self.return_repo.get_draft_by_purchase(
                data["purchase_id"]
            )
        )

        if existing_draft:
            return existing_draft

        user = self.user_repo.get_by_id(
            data["user_id"]
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        data.setdefault(
            "status",
            "DRAFT"
        )

        data.setdefault(
            "total_amount",
            Decimal("0")
        )

        purchase_return = self.return_repo.create(
            data
        )

        self.audit_repo.create({

            "user_id":
                purchase_return.user_id,

            "action":
                "CREATE_PURCHASE_RETURN",

            "table_name":
                "purchase_returns",

            "record_id":
                purchase_return.return_id,

            "details":
                f"Purchase Return #{purchase_return.return_id} created"

        })

        return purchase_return
    
    
        # ==================================================
    # GET BY ID
    # ==================================================
    def get_return(
        self,
        return_id: int
    ):

        purchase_return = self.return_repo.get_by_id(
            return_id
        )

        if not purchase_return:
            raise ValueError(
                "Purchase return not found"
            )

        return purchase_return


    # ==================================================
    # GET ALL
    # ==================================================
    def get_all_returns(
        self
    ):

        return self.return_repo.get_all()
    

        # ==================================================
    # GET RETURNS BY PURCHASE
    # ==================================================
    def get_returns_by_purchase(
        self,
        purchase_id: int
    ):

        purchase = self.purchase_repo.get_by_id(
            purchase_id
        )

        if not purchase:
            raise ValueError(
                "Purchase order not found"
            )

        return self.return_repo.get_by_purchase(
            purchase_id
        )


    # ==================================================
    # GET RETURNED PURCHASES
    # ==================================================
    def get_returned_purchases(
        self
    ):

        purchase_rows = (
            self.return_repo.get_returned_purchases()
        )

        result = []

        for row in purchase_rows:

            purchase = self.purchase_repo.get_by_id(
                row.purchase_id
            )

            if not purchase:
                continue

            returns = self.return_repo.get_by_purchase(
                row.purchase_id
            )

            completed_returns = [

                r

                for r in returns

                if r.status == "COMPLETED"

            ]

            total_returned = sum(

                Decimal(
                    str(r.total_amount)
                )

                for r in completed_returns

            )

            result.append({

                "purchase_id":
                    purchase.purchase_id,

                "returns_count":
                    len(completed_returns),

                "total_returned":
                    float(total_returned)

            })

        return result
    


    # ==================================================
    # COMPLETE RETURN
    # ==================================================
    def complete_return(
        self,
        purchase_return
    ):

        if purchase_return.status != "DRAFT":
            raise ValueError(
                "Only draft returns can be completed"
            )

        items = self.item_repo.get_by_return(
            purchase_return.return_id
        )

        if not items:
            raise ValueError(
                "Purchase return has no items"
            )

        purchase = self.purchase_repo.get_by_id(
            purchase_return.purchase_id
        )

        if not purchase:
            raise ValueError(
                "Purchase order not found"
            )

        total_return_amount = Decimal("0")

        for item in items:

            purchase_item = (
                self.purchase_item_repo.get_by_id(
                    item.purchase_item_id
                )
            )

            if not purchase_item:
                raise ValueError(
                    "Purchase item not found"
                )

            completed_returned = (
                self.item_repo.get_total_returned_quantity(
                    purchase_item.purchase_item_id
                )
            )

            if (
                completed_returned + item.quantity
                >
                purchase_item.quantity
            ):
                raise ValueError(
                    f"Returned quantity exceeds purchased quantity "
                    f"for Purchase Item "
                    f"#{purchase_item.purchase_item_id}"
                )

            batch = self.batch_repo.get_by_id(
                item.batch_id
            )

            if not batch:
                raise ValueError(
                    f"Batch {item.batch_id} not found"
                )

            if batch.quantity < item.quantity:
                raise ValueError(
                    "Not enough quantity in batch"
                )

            batch.quantity -= item.quantity

            self.batch_repo.update(
                batch
            )

            inventory = (
                self.inventory_repo.get_by_medicine(
                    item.medicine_id
                )
            )

            if not inventory:
                raise ValueError(
                    "Inventory record not found"
                )

            if inventory.quantity < item.quantity:
                raise ValueError(
                    "Not enough inventory quantity"
                )

            inventory.quantity -= item.quantity

            self.inventory_repo.update(
                inventory
            )

            # ==========================================
            # STOCK MOVEMENT
            # ==========================================
            self.movement_repo.create({

                "batch_id":
                    batch.batch_id,

                "movement_type":
                    "RETURN",

                "quantity_change":
                    -item.quantity,

                "reference_type":
                    "RETURN",

                "reference_id":
                    purchase_return.return_id,

                "notes":
                    f"Purchase Return #{purchase_return.return_id}",

                "created_by":
                    purchase_return.user_id

            })

            total_return_amount += Decimal(
                str(item.subtotal)
            )

        # ==========================================
        # UPDATE PURCHASE ORDER
        # ==========================================
        purchase.total_amount = (

            Decimal(
                str(purchase.total_amount)
            )

            - total_return_amount

        )

        if purchase.total_amount < 0:

            purchase.total_amount = Decimal("0")

        self.purchase_repo.update(
            purchase
        )

        # ==========================================
        # COMPLETE RETURN
        # ==========================================
        purchase_return.status = "COMPLETED"

        purchase_return.total_amount = total_return_amount

        self.audit_repo.create({

            "user_id":
                purchase_return.user_id,

            "action":
                "COMPLETE_PURCHASE_RETURN",

            "table_name":
                "purchase_returns",

            "record_id":
                purchase_return.return_id,

            "details":
                f"Purchase Return #{purchase_return.return_id} completed"

        })

        return self.return_repo.update(
            purchase_return
        )
    

        # ==================================================
    # DELETE
    # ==================================================
    def delete_return(
        self,
        purchase_return
    ):

        if purchase_return.status != "DRAFT":
            raise ValueError(
                "Only draft returns can be deleted"
            )

        items = self.item_repo.get_by_return(
            purchase_return.return_id
        )

        if items:
            raise ValueError(
                "Cannot delete a purchase return that contains items"
            )

        self.audit_repo.create({

            "user_id":
                purchase_return.user_id,

            "action":
                "DELETE_PURCHASE_RETURN",

            "table_name":
                "purchase_returns",

            "record_id":
                purchase_return.return_id,

            "details":
                f"Purchase Return #{purchase_return.return_id} deleted"

        })

        self.return_repo.delete(
            purchase_return
        )

        return True


    

