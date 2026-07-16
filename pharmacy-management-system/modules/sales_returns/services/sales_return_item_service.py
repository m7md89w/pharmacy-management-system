from decimal import Decimal

from modules.sales_returns.repository.sales_return_item_repository import (
    SalesReturnItemRepository
)
from modules.sales_returns.repository.sales_return_repository import (
    SalesReturnRepository
)

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

from modules.inventory.repository.inventory_repository import (
    InventoryRepository
)

from modules.stock_movements.repository.stock_movement_repository import (
    StockMovementRepository
)

from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)


class SalesReturnItemService:

    def __init__(
        self,
        item_repo: SalesReturnItemRepository,
        return_repo: SalesReturnRepository,
        sale_item_repo: SaleItemRepository,
        invoice_repo: SalesInvoiceRepository,
        medicine_repo: MedicineRepository,
        batch_repo: MedicineBatchRepository,
        inventory_repo: InventoryRepository,
        movement_repo: StockMovementRepository,
        audit_repo: AuditLogRepository
    ):

        self.item_repo = item_repo
        self.return_repo = return_repo
        self.sale_item_repo = sale_item_repo
        self.invoice_repo = invoice_repo
        self.medicine_repo = medicine_repo
        self.batch_repo = batch_repo
        self.inventory_repo = inventory_repo
        self.movement_repo = movement_repo
        self.audit_repo = audit_repo

    # ==================================================
    # CREATE
    # ==================================================
    def create_item(
        self,
        data: dict
    ):

        sales_return = self.return_repo.get_by_id(
            data["return_id"]
        )

        if not sales_return:
            raise ValueError(
                "Sales return not found"
            )

        if sales_return.status != "DRAFT":
            raise ValueError(
                "Cannot modify completed sales return"
            )

        invoice = self.invoice_repo.get_by_id(
            sales_return.invoice_id
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        if invoice.status != "COMPLETED":
            raise ValueError(
                "Only completed invoices can be returned"
            )

        sale_item = self.sale_item_repo.get_by_id(
            data["sale_item_id"]
        )

        if not sale_item:
            raise ValueError(
                "Sale item not found"
            )

        medicine = self.medicine_repo.get_by_id(
            sale_item.medicine_id
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

        completed_returned = (
            self.item_repo.get_total_returned_quantity(
                sale_item.sale_item_id
            )
        )

        draft_returned = 0

        draft_items = self.item_repo.get_by_return(
            sales_return.return_id
        )

        for existing in draft_items:

            if (
                existing.sale_item_id
                == sale_item.sale_item_id
            ):
                draft_returned += (
                    existing.quantity
                )

        total_returned = (
            completed_returned
            + draft_returned
        )

        if (
            total_returned + quantity
            > sale_item.quantity
        ):
            raise ValueError(
                "Return quantity exceeds sold quantity"
            )

        unit_price = Decimal(
            str(sale_item.unit_price)
        )

        subtotal = (
            Decimal(str(quantity))
            * unit_price
        )

        item = self.item_repo.create({

            "return_id":
                sales_return.return_id,

            "sale_item_id":
                sale_item.sale_item_id,

            "medicine_id":
                sale_item.medicine_id,

            "batch_id":
                sale_item.batch_id,

            "quantity":
                quantity,

            "unit_price":
                unit_price,

            "subtotal":
                subtotal
        })

        sales_return.total_amount = (
            Decimal(str(sales_return.total_amount))
            + subtotal
        )

        self.return_repo.update(
            sales_return
        )

        self.audit_repo.create({

            "user_id":
                sales_return.user_id,

            "action":
                "CREATE_SALES_RETURN_ITEM",

            "table_name":
                "sales_return_items",

            "record_id":
                item.return_item_id,

            "details":
                f"Added Return Item "
                f"#{item.return_item_id}"
        })

        return item

    # ==================================================
    # GET BY ID
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
                "Return item not found"
            )

        return item

    # ==================================================
    # GET ITEMS BY RETURN
    # ==================================================
    def get_items_by_return(
        self,
        return_id: int
    ):

        sales_return = self.return_repo.get_by_id(
            return_id
        )

        if not sales_return:
            raise ValueError(
                "Sales return not found"
            )

        return self.item_repo.get_by_return(
            return_id
        )
    # ==================================================
    # GET COMPLETED ITEMS BY INVOICE
    # ==================================================
    def get_completed_items_by_invoice(
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

        return self.item_repo.get_completed_by_invoice(
            invoice_id
        )
    

    # ==================================================
    # DELETE
    # ==================================================
    def delete_item(
        self,
        item
    ):

        sales_return = self.return_repo.get_by_id(
            item.return_id
        )

        if not sales_return:
            raise ValueError(
                "Sales return not found"
            )

        if sales_return.status != "DRAFT":
            raise ValueError(
                "Cannot modify completed sales return"
            )

        sales_return.total_amount = (
            Decimal(str(sales_return.total_amount))
            - Decimal(str(item.subtotal))
        )

        if sales_return.total_amount < 0:
            sales_return.total_amount = Decimal(
                "0"
            )

        self.return_repo.update(
            sales_return
        )

        self.audit_repo.create({

            "user_id":
                sales_return.user_id,

            "action":
                "DELETE_SALES_RETURN_ITEM",

            "table_name":
                "sales_return_items",

            "record_id":
                item.return_item_id,

            "details":
                f"Deleted Return Item "
                f"#{item.return_item_id}"
        })

        self.item_repo.delete(
            item
        )

        return True
    
