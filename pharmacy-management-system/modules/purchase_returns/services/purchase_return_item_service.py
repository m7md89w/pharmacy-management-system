from decimal import Decimal

from modules.purchase_returns.repository.purchase_return_item_repository import (
    PurchaseReturnItemRepository
)
from modules.purchase_returns.repository.purchase_return_repository import (
    PurchaseReturnRepository
)

from modules.purchases.repository.purchase_item_repository import (
    PurchaseItemRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)

from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)


class PurchaseReturnItemService:

    def __init__(
        self,
        item_repo: PurchaseReturnItemRepository,
        return_repo: PurchaseReturnRepository,
        purchase_item_repo: PurchaseItemRepository,
        medicine_repo: MedicineRepository,
        batch_repo: MedicineBatchRepository,
        audit_repo: AuditLogRepository
    ):
        self.item_repo = item_repo
        self.return_repo = return_repo
        self.purchase_item_repo = purchase_item_repo
        self.medicine_repo = medicine_repo
        self.batch_repo = batch_repo
        self.audit_repo = audit_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_item(
        self,
        data: dict
    ):

        purchase_return = self.return_repo.get_by_id(
            data["return_id"]
        )

        if not purchase_return:
            raise ValueError(
                "Purchase return not found"
            )

        if purchase_return.status != "DRAFT":
            raise ValueError(
                "Cannot modify completed purchase return"
            )

        purchase_item = self.purchase_item_repo.get_by_id(
            data["purchase_item_id"]
        )

        if not purchase_item:
            raise ValueError(
                "Purchase item not found"
            )

        medicine = self.medicine_repo.get_by_id(
            purchase_item.medicine_id
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        batch = self.batch_repo.get_by_id(
            purchase_item.batch_id
        )

        if not batch:
            raise ValueError(
                "Batch not found"
            )

        quantity = int(
            data["quantity"]
        )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        completed_returned = (
            self.item_repo.get_total_returned_quantity(
                purchase_item.purchase_item_id
            )
        )

        draft_returned = 0

        draft_items = self.item_repo.get_by_return(
            purchase_return.return_id
        )

        for existing in draft_items:

            if (
                existing.purchase_item_id
                ==
                purchase_item.purchase_item_id
            ):

                draft_returned += existing.quantity

        purchase_remaining = (
            purchase_item.quantity
            -
            completed_returned
            -
            draft_returned
        )

        batch_available = (
            batch.quantity
            -
            draft_returned
        )

        available_quantity = min(
            purchase_remaining,
            batch_available
        )

        if available_quantity <= 0:
            raise ValueError(
                "No quantity available for return."
            )

        if quantity > available_quantity:
            raise ValueError(
                f"Only {available_quantity} item(s) can be returned."
            )

        unit_cost = Decimal(
            str(
                purchase_item.unit_cost
            )
        )

        subtotal = (
            Decimal(str(quantity))
            *
            unit_cost
        )

        item = self.item_repo.create({

            "return_id":
                purchase_return.return_id,

            "purchase_item_id":
                purchase_item.purchase_item_id,

            "medicine_id":
                purchase_item.medicine_id,

            "batch_id":
                purchase_item.batch_id,

            "quantity":
                quantity,

            "unit_cost":
                unit_cost,

            "subtotal":
                subtotal,

            "reason":
                data.get("reason")

        })

        purchase_return.total_amount = (
            Decimal(
                str(
                    purchase_return.total_amount
                )
            )
            +
            subtotal
        )

        self.return_repo.update(
            purchase_return
        )

        self.audit_repo.create({

            "user_id":
                purchase_return.user_id,

            "action":
                "CREATE_PURCHASE_RETURN_ITEM",

            "table_name":
                "purchase_return_items",

            "record_id":
                item.return_item_id,

            "details":
                f"Added Purchase Return Item #{item.return_item_id}"

        })

        return item
        # ==================================================
    # UPDATE
    # ==================================================
    def update_item(
        self,
        item,
        quantity: int
    ):

        purchase_return = self.return_repo.get_by_id(
            item.return_id
        )

        if not purchase_return:
            raise ValueError(
                "Purchase return not found"
            )

        if purchase_return.status != "DRAFT":
            raise ValueError(
                "Cannot modify completed purchase return"
            )

        purchase_item = self.purchase_item_repo.get_by_id(
            item.purchase_item_id
        )

        if not purchase_item:
            raise ValueError(
                "Purchase item not found"
            )

        batch = self.batch_repo.get_by_id(
            purchase_item.batch_id
        )

        if not batch:
            raise ValueError(
                "Batch not found"
            )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        completed_returned = (
            self.item_repo.get_total_returned_quantity(
                purchase_item.purchase_item_id
            )
        )

        draft_returned = 0

        draft_items = self.item_repo.get_by_return(
            purchase_return.return_id
        )

        for existing in draft_items:

            if (
                existing.purchase_item_id
                == purchase_item.purchase_item_id
                and
                existing.return_item_id != item.return_item_id
            ):

                draft_returned += existing.quantity

        purchase_remaining = (
            purchase_item.quantity
            -
            completed_returned
            -
            draft_returned
        )

        batch_available = (
            batch.quantity
            -
            draft_returned
        )

        available_quantity = min(
            purchase_remaining,
            batch_available
        )

        if available_quantity <= 0:
            raise ValueError(
                "No quantity available for return."
            )

        if quantity > available_quantity:
            raise ValueError(
                f"Only {available_quantity} item(s) can be returned."
            )

        item.quantity = quantity

        item.subtotal = (
            Decimal(str(quantity))
            *
            Decimal(str(item.unit_cost))
        )

        purchase_return.total_amount = Decimal("0")

        for return_item in self.item_repo.get_by_return(
            purchase_return.return_id
        ):

            if return_item.return_item_id == item.return_item_id:
                continue

            purchase_return.total_amount += Decimal(
                str(return_item.subtotal)
            )

        purchase_return.total_amount += item.subtotal

        self.return_repo.update(
            purchase_return
        )

        return self.item_repo.update(
            item
        )

    # ==================================================
    # GET ITEM
    # ==================================================
    def get_item(
        self,
        return_item_id: int
    ):

        item = self.item_repo.get_by_id(
            return_item_id
        )

        if not item:
            raise ValueError(
                "Purchase return item not found"
            )

        return item

    # ==================================================
    # GET ITEMS BY RETURN
    # ==================================================
    def get_items_by_return(
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

        return self.item_repo.get_by_return(
            return_id
        )

    # ==================================================
    # GET COMPLETED ITEMS BY PURCHASE
    # ==================================================
    def get_completed_items_by_purchase(
        self,
        purchase_id: int
    ):

        purchase_return = (
            self.return_repo.get_completed_by_purchase(
                purchase_id
            )
        )

        if not purchase_return:
            return []

        return self.item_repo.get_by_completed_purchase(
            purchase_id
        )
    

        # ==================================================
    # DELETE
    # ==================================================
    def delete_item(
        self,
        item
    ):

        purchase_return = self.return_repo.get_by_id(
            item.return_id
        )

        if not purchase_return:
            raise ValueError(
                "Purchase return not found"
            )

        if purchase_return.status != "DRAFT":
            raise ValueError(
                "Cannot modify completed purchase return"
            )

        purchase_return.total_amount = (
            Decimal(str(purchase_return.total_amount))
            -
            Decimal(str(item.subtotal))
        )

        if purchase_return.total_amount < 0:
            purchase_return.total_amount = Decimal("0")

        self.return_repo.update(
            purchase_return
        )

        self.audit_repo.create({

            "user_id":
                purchase_return.user_id,

            "action":
                "DELETE_PURCHASE_RETURN_ITEM",

            "table_name":
                "purchase_return_items",

            "record_id":
                item.return_item_id,

            "details":
                f"Deleted Purchase Return Item #{item.return_item_id}"

        })

        self.item_repo.delete(
            item
        )

        return True
