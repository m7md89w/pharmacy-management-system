from datetime import datetime
from decimal import Decimal

from modules.purchases.repository.purchase_item_repository import PurchaseItemRepository
from modules.medicines.repository.medicine_repository import MedicineRepository
from modules.purchases.repository.purchase_order_repository import PurchaseOrderRepository


class PurchaseItemService:

    def __init__(
        self,
        item_repo: PurchaseItemRepository,
        medicine_repo: MedicineRepository,
        order_repo: PurchaseOrderRepository
    ):
        self.item_repo = item_repo
        self.medicine_repo = medicine_repo
        self.order_repo = order_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_item(
        self,
        data: dict
    ):

        order = self.order_repo.get_by_id(
            data["purchase_id"]
        )

        if not order:
            raise ValueError(
                "Purchase order not found"
            )

        if order.status != "PENDING":
            raise ValueError(
                "Cannot add items to this purchase order"
            )

        medicine = self.medicine_repo.get_by_id(
            data["medicine_id"]
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        quantity = int(
            data["quantity"]
        )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        unit_cost = float(
            data["unit_cost"]
        )

        if unit_cost < 0:
            raise ValueError(
                "Unit cost cannot be negative"
            )

        selling_price = float(
            data["selling_price"]
        )

        if selling_price < 0:
            raise ValueError(
                "Selling price cannot be negative"
            )

        if not data.get("batch_number"):
            raise ValueError(
                "Batch number is required"
            )

        if not data.get("expiry_date"):
            raise ValueError(
                "Expiry date is required"
            )

        data["batch_number"] = (
            data["batch_number"]
            .strip()
            .upper()
        )

        # ==========================================
        # Dates
        # ==========================================
        if (
            data.get("manufacture_date")
            and
            isinstance(
                data["manufacture_date"],
                str
            )
        ):
            data["manufacture_date"] = (
                datetime.strptime(
                    data["manufacture_date"],
                    "%Y-%m-%d"
                ).date()
            )

        if (
            data.get("expiry_date")
            and
            isinstance(
                data["expiry_date"],
                str
            )
        ):
            data["expiry_date"] = (
                datetime.strptime(
                    data["expiry_date"],
                    "%Y-%m-%d"
                ).date()
            )

        if (
            data.get("manufacture_date")
            and
            data["manufacture_date"]
            >=
            data["expiry_date"]
        ):
            raise ValueError(
                "Manufacture date must be before expiry date."
            )

        # ==========================================
        # Prevent duplicate batch inside purchase
        # ==========================================
        existing_items = self.item_repo.get_by_purchase(
            data["purchase_id"]
        )

        for existing_item in existing_items:

            if (
                existing_item.medicine_id
                == data["medicine_id"]
                and
                existing_item.batch_number.upper()
                == data["batch_number"]
            ):
                raise ValueError(
                    "This batch number already exists in this purchase order."
                )

        data["subtotal"] = Decimal(
            str(
                quantity * unit_cost
            )
        )

        data["selling_price"] = Decimal(
            str(
                selling_price
            )
        )

        item = self.item_repo.create(
            data
        )

        order.total_amount = (
            Decimal(str(order.total_amount))
            +
            Decimal(str(item.subtotal))
        )

        self.order_repo.update(
            order
        )

        return item
    
        # ==================================================
    # GET ITEM
    # ==================================================
    def get_item(
        self,
        purchase_item_id: int
    ):

        item = self.item_repo.get_by_id(
            purchase_item_id
        )

        if not item:
            raise ValueError(
                "Purchase item not found"
            )

        return item

    # ==================================================
    # GET ITEMS BY ORDER
    # ==================================================
    def get_items_by_order(
        self,
        purchase_id: int
    ):

        return self.item_repo.get_by_purchase(
            purchase_id
        )

    # ==================================================
    # UPDATE
    # ==================================================
    def update_item(
        self,
        item,
        data: dict
    ):

        order = self.order_repo.get_by_id(
            item.purchase_id
        )

        if order.status != "PENDING":
            raise ValueError(
                "Cannot modify items in this purchase order"
            )

        old_subtotal = Decimal(
            str(item.subtotal)
        )

        if "quantity" in data:

            quantity = int(
                data["quantity"]
            )

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than zero"
                )

            item.quantity = quantity

        if "unit_cost" in data:

            unit_cost = float(
                data["unit_cost"]
            )

            if unit_cost < 0:
                raise ValueError(
                    "Unit cost cannot be negative"
                )

            item.unit_cost = unit_cost

        if "selling_price" in data:

            selling_price = float(
                data["selling_price"]
            )

            if selling_price < 0:
                raise ValueError(
                    "Selling price cannot be negative"
                )

            item.selling_price = Decimal(
                str(selling_price)
            )

        if "batch_number" in data:

            item.batch_number = (
                data["batch_number"]
                .strip()
                .upper()
            )

        # ==========================================
        # Dates
        # ==========================================
        if (
            "manufacture_date" in data
            and
            data["manufacture_date"]
        ):

            if isinstance(
                data["manufacture_date"],
                str
            ):
                item.manufacture_date = (
                    datetime.strptime(
                        data["manufacture_date"],
                        "%Y-%m-%d"
                    ).date()
                )
            else:
                item.manufacture_date = (
                    data["manufacture_date"]
                )

        if (
            "expiry_date" in data
            and
            data["expiry_date"]
        ):

            if isinstance(
                data["expiry_date"],
                str
            ):
                item.expiry_date = (
                    datetime.strptime(
                        data["expiry_date"],
                        "%Y-%m-%d"
                    ).date()
                )
            else:
                item.expiry_date = (
                    data["expiry_date"]
                )

        if (
            item.manufacture_date
            and
            item.manufacture_date >= item.expiry_date
        ):
            raise ValueError(
                "Manufacture date must be before expiry date."
            )

        # ==========================================
        # Prevent duplicate batch inside purchase
        # ==========================================
        existing_items = self.item_repo.get_by_purchase(
            item.purchase_id
        )

        for existing_item in existing_items:

            if (
                existing_item.purchase_item_id
                == item.purchase_item_id
            ):
                continue

            if (
                existing_item.medicine_id
                == item.medicine_id
                and
                existing_item.batch_number.upper()
                == item.batch_number.upper()
            ):
                raise ValueError(
                    "This batch number already exists in this purchase order."
                )

        item.subtotal = Decimal(
            str(
                item.quantity
                * item.unit_cost
            )
        )

        difference = (
            item.subtotal
            - old_subtotal
        )

        order.total_amount = (
            Decimal(str(order.total_amount))
            + difference
        )

        self.order_repo.update(
            order
        )

        return self.item_repo.update(
            item
        )
    
        # ==================================================
    # DELETE
    # ==================================================
    def delete_item(
        self,
        item
    ):

        order = self.order_repo.get_by_id(
            item.purchase_id
        )

        if not order:
            raise ValueError(
                "Purchase order not found"
            )

        if order.status != "PENDING":
            raise ValueError(
                "Cannot delete items from this purchase order"
            )

        order.total_amount = (
            Decimal(str(order.total_amount))
            -
            Decimal(str(item.subtotal))
        )

        if order.total_amount < 0:
            order.total_amount = Decimal("0")

        self.order_repo.update(
            order
        )

        self.item_repo.delete(
            item
        )

        return True
    


    
