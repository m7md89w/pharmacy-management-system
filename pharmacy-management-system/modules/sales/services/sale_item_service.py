from decimal import Decimal

from modules.sales.repository.sale_item_repository import (
    SaleItemRepository
)
from modules.sales.repository.sales_invoice_repository import (
    SalesInvoiceRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)

from modules.stock_movements.repository.stock_movement_repository import (
    StockMovementRepository
)
from modules.inventory.repository.inventory_repository import (
    InventoryRepository
)
from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)


class SaleItemService:

    def __init__(
        self,
        item_repo: SaleItemRepository,
        invoice_repo: SalesInvoiceRepository,
        medicine_repo: MedicineRepository,
        batch_repo: MedicineBatchRepository,
        movement_repo: StockMovementRepository,
        inventory_repo: InventoryRepository,
        audit_repo: AuditLogRepository
    ):
        self.item_repo = item_repo
        self.invoice_repo = invoice_repo
        self.medicine_repo = medicine_repo
        self.batch_repo = batch_repo
        self.movement_repo = movement_repo
        self.inventory_repo = inventory_repo
        self.audit_repo = audit_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_item(
        self,
        data: dict
    ):

        invoice = self.invoice_repo.get_by_id(
            data["invoice_id"]
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        if invoice.status != "DRAFT":
            raise ValueError(
                "Cannot modify this invoice"
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

        inventory = self.inventory_repo.get_by_medicine(
            medicine.medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory record not found"
            )

        if inventory.quantity < quantity:
            raise ValueError(
                "Insufficient inventory stock"
            )

        batches = self.batch_repo.get_available_batches(
            medicine.medicine_id
        )

        if not batches:
            raise ValueError(
                "No available stock for this medicine"
            )

        total_available = sum(
            batch.quantity
            for batch in batches
        )

        if total_available < quantity:
            raise ValueError(
                "Insufficient stock"
            )

        remaining_quantity = quantity

        created_items = []

        total_subtotal = Decimal("0")

        for batch in batches:

            if remaining_quantity <= 0:
                break

            if batch.quantity <= 0:
                continue

            sell_quantity = min(
                remaining_quantity,
                batch.quantity
            )

            unit_price = Decimal(
                str(
                    data.get(
                        "unit_price",
                        batch.selling_price
                    )
                )
            )

            subtotal = (
                Decimal(str(sell_quantity))
                * unit_price
            )

            item = self.item_repo.create({
                "invoice_id": invoice.invoice_id,
                "medicine_id": medicine.medicine_id,
                "batch_id": batch.batch_id,
                "quantity": sell_quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })

            created_items.append(
                item
            )

            batch.quantity -= sell_quantity

            self.batch_repo.update(
                batch
            )

            self.movement_repo.create({
                "batch_id": batch.batch_id,
                "movement_type": "SALE",
                "quantity_change": -sell_quantity,
                "reference_type": "SALE",
                "reference_id": invoice.invoice_id,
                "notes": f"Sales Invoice #{invoice.invoice_number}",
                "created_by": invoice.user_id
            })

            total_subtotal += subtotal

            remaining_quantity -= sell_quantity

        # ==========================================
        # Safety Check
        # ==========================================
        if remaining_quantity > 0:
            raise ValueError(
                "Unable to allocate all requested quantity."
            )

        inventory.quantity -= quantity

        self.inventory_repo.update(
            inventory
        )

        invoice.total_amount = (
            Decimal(str(invoice.total_amount))
            + total_subtotal
        )

        self.invoice_repo.update(
            invoice
        )

        self.audit_repo.create({
            "user_id": invoice.user_id,
            "action": "CREATE_SALE",
            "table_name": "sale_items",
            "record_id": invoice.invoice_id,
            "details":
                f"Sold {quantity} units of medicine "
                f"{medicine.medicine_id}"
        })

        return created_items
    
        # ==================================================
    # GET ITEM
    # ==================================================
    def get_item(
        self,
        sale_item_id: int
    ):

        item = self.item_repo.get_by_id(
            sale_item_id
        )

        if not item:
            raise ValueError(
                "Sale item not found"
            )

        return item

    # ==================================================
    # GET ITEMS BY INVOICE
    # ==================================================
    def get_items_by_invoice(
        self,
        invoice_id: int
    ):

        invoice = self.invoice_repo.get_by_id(
            invoice_id
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        return self.item_repo.get_by_invoice(
            invoice_id
        )

    # ==================================================
    # UPDATE
    # ==================================================
    def update_item(
        self,
        item,
        data: dict
    ):

        raise ValueError(
            "Sale items cannot be edited. Delete and recreate the item."
        )
    

        # ==================================================
    # DELETE
    # ==================================================
    def delete_item(
        self,
        item
    ):

        invoice = self.invoice_repo.get_by_id(
            item.invoice_id
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        if invoice.status != "DRAFT":
            raise ValueError(
                "Cannot modify this invoice"
            )

        batch = self.batch_repo.get_by_id(
            item.batch_id
        )

        if not batch:
            raise ValueError(
                "Batch not found"
            )

        inventory = self.inventory_repo.get_by_medicine(
            item.medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory record not found"
            )

        # ==========================================
        # Restore batch quantity
        # ==========================================
        batch.quantity += item.quantity

        self.batch_repo.update(
            batch
        )

        # ==========================================
        # Restore inventory
        # ==========================================
        inventory.quantity += item.quantity

        self.inventory_repo.update(
            inventory
        )

        # ==========================================
        # Update invoice total
        # ==========================================
        invoice.total_amount = (
            Decimal(str(invoice.total_amount))
            - Decimal(str(item.subtotal))
        )

        if invoice.total_amount < 0:
            invoice.total_amount = Decimal("0")

        self.invoice_repo.update(
            invoice
        )

        # ==========================================
        # Stock Movement
        # ==========================================
        self.movement_repo.create({
            "batch_id": batch.batch_id,
            "movement_type": "RETURN",
            "quantity_change": item.quantity,
            "reference_type": "SALE",
            "reference_id": invoice.invoice_id,
            "notes": f"Delete Sale Item #{item.sale_item_id}",
            "created_by": invoice.user_id
        })

        # ==========================================
        # Audit Log
        # ==========================================
        self.audit_repo.create({
            "user_id": invoice.user_id,
            "action": "DELETE_SALE_ITEM",
            "table_name": "sale_items",
            "record_id": item.sale_item_id,
            "details": f"Deleted sale item #{item.sale_item_id}"
        })

        self.item_repo.delete(
            item
        )

        return True
    

