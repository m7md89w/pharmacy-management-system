from decimal import Decimal

from modules.sales_returns.repository.sales_return_repository import (
    SalesReturnRepository
)
from modules.sales_returns.repository.sales_return_item_repository import (
    SalesReturnItemRepository
)

from modules.sales.repository.sales_invoice_repository import (
    SalesInvoiceRepository
)
from modules.sales.repository.sale_item_repository import (
    SaleItemRepository
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


class SalesReturnService:

    VALID_STATUSES = [
        "DRAFT",
        "COMPLETED",
        "CANCELLED"
    ]

    def __init__(
        self,
        return_repo: SalesReturnRepository,
        item_repo: SalesReturnItemRepository,
        invoice_repo: SalesInvoiceRepository,
        user_repo: UserRepository,
        sale_item_repo: SaleItemRepository,
        batch_repo: MedicineBatchRepository,
        inventory_repo: InventoryRepository,
        movement_repo: StockMovementRepository,
        audit_repo: AuditLogRepository
    ):

        self.return_repo = return_repo
        self.item_repo = item_repo
        self.invoice_repo = invoice_repo
        self.user_repo = user_repo
        self.sale_item_repo = sale_item_repo
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

        invoice = self.invoice_repo.get_by_id(
            data["invoice_id"]
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        if invoice.status != "COMPLETED":
            raise ValueError(
                "Only completed invoices can be returned"
            )

        existing_draft = (
            self.return_repo.get_draft_by_invoice(
                data["invoice_id"]
            )
        )

        if existing_draft:
            return existing_draft

        # ==========================================
        # Check Remaining Quantities
        # ==========================================
        sale_items = self.sale_item_repo.get_by_invoice(
            invoice.invoice_id
        )

        can_return = False

        for sale_item in sale_items:

            returned_quantity = (
                self.item_repo.get_total_returned_quantity(
                    sale_item.sale_item_id
                )
            )

            if returned_quantity < sale_item.quantity:
                can_return = True
                break

        if not can_return:
            raise ValueError(
                "This invoice has already been fully returned."
            )

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

        sales_return = self.return_repo.create(
            data
        )

        self.audit_repo.create({

            "user_id":
                sales_return.user_id,

            "action":
                "CREATE_SALES_RETURN",

            "table_name":
                "sales_returns",

            "record_id":
                sales_return.return_id,

            "details":
                f"Sales Return #{sales_return.return_id} created"

        })

        return sales_return
    
    # ==================================================
    # GET BY ID
    # ==================================================
    def get_return(
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

        return sales_return

    # ==================================================
    # GET ALL RETURNS
    # ==================================================
    def get_all_returns(
        self
    ):

        return self.return_repo.get_all()

    # ==================================================
    # GET RETURNED INVOICES
    # ==================================================
    def get_returned_invoices(
        self
    ):

        invoice_rows = (
            self.return_repo.get_returned_invoices()
        )

        result = []

        for row in invoice_rows:

            invoice = self.invoice_repo.get_by_id(
                row.invoice_id
            )

            if not invoice:
                continue

            returns = (
                self.return_repo.get_by_invoice(
                    row.invoice_id
                )
            )

            completed_returns = [

                r

                for r in returns

                if r.status == "COMPLETED"

            ]

            total_returned = sum(
                Decimal(str(r.total_amount))
                for r in completed_returns
            )

            # ==========================================
            # CHECK IF CAN RETURN
            # ==========================================
            sale_items = self.sale_item_repo.get_by_invoice(
                invoice.invoice_id
            )

            can_return = False

            for sale_item in sale_items:

                returned_quantity = (
                    self.item_repo.get_total_returned_quantity(
                        sale_item.sale_item_id
                    )
                )

                if returned_quantity < sale_item.quantity:

                    can_return = True
                    break

            result.append({

                "invoice_id":
                    invoice.invoice_id,

                "invoice_number":
                    invoice.invoice_number,

                "returns_count":
                    len(completed_returns),

                "total_returned":
                    float(total_returned),

                "can_return":
                    can_return

            })

        return result

    # ==================================================
    # GET RETURNS BY INVOICE
    # ==================================================
    def get_returns_by_invoice(
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

        return self.return_repo.get_by_invoice(
            invoice_id
        )
    
    # ==================================================
    # COMPLETE RETURN
    # ==================================================
    def complete_return(
        self,
        sales_return
    ):

        if sales_return.status != "DRAFT":
            raise ValueError(
                "Only draft returns can be completed"
            )

        items = self.item_repo.get_by_return(
            sales_return.return_id
        )

        if not items:
            raise ValueError(
                "Sales return has no items"
            )

        invoice = self.invoice_repo.get_by_id(
            sales_return.invoice_id
        )

        if not invoice:
            raise ValueError(
                "Invoice not found"
            )

        total_return_amount = Decimal("0")

        for item in items:

            sale_item = self.sale_item_repo.get_by_id(
                item.sale_item_id
            )

            if not sale_item:
                raise ValueError(
                    "Sale item not found"
                )

            # ==========================================
            # CHECK RETURNED QUANTITY
            # ==========================================
            completed_returned = (
                self.item_repo.get_total_returned_quantity(
                    sale_item.sale_item_id
                )
            )

            if (
                completed_returned + item.quantity
                > sale_item.quantity
            ):
                raise ValueError(
                    f"Returned quantity exceeds sold quantity "
                    f"for Sale Item #{sale_item.sale_item_id}"
                )

            # ==========================================
            # UPDATE BATCH
            # ==========================================
            batch = self.batch_repo.get_by_id(item.batch_id)
            if not batch:
                raise ValueError(
                    f"Batch {item.batch_id} not found"
                    )
                
            print("================================")
            print("Return Item Batch:", item.batch_id)
            print("Batch Qty Before :", batch.quantity)
            print("Return Qty      :", item.quantity)
            batch.quantity += item.quantity
            print("Batch Qty After  :", batch.quantity)
            self.batch_repo.update(batch)
            saved_batch = self.batch_repo.get_by_id(batch.batch_id)
            print("Saved Qty        :", saved_batch.quantity)
            print("================================")
            # ==========================================
            # UPDATE INVENTORY
            # ==========================================
            inventory = (
                self.inventory_repo.get_by_medicine(
                    item.medicine_id
                )
            )

            if not inventory:
                raise ValueError(
                    "Inventory record not found"
                )

            inventory.quantity += item.quantity

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
                    item.quantity,

                "reference_type":
                    "RETURN",

                "reference_id":
                    sales_return.return_id,

                "notes":
                    f"Sales Return #{sales_return.return_id}",

                "created_by":
                    sales_return.user_id

            })

            total_return_amount += Decimal(
                str(item.subtotal)
            )

        # ==========================================
        # UPDATE INVOICE
        # ==========================================
        invoice.total_amount = (
            Decimal(str(invoice.total_amount))
            - total_return_amount
        )

        if invoice.total_amount < 0:
            invoice.total_amount = Decimal("0")

        self.invoice_repo.update(
            invoice
        )

        # ==========================================
        # COMPLETE RETURN
        # ==========================================
        sales_return.status = "COMPLETED"

        self.audit_repo.create({
            

            "user_id":
                sales_return.user_id,

            "action":
                "COMPLETE_SALES_RETURN",

            "table_name":
                "sales_returns",

            "record_id":
                sales_return.return_id,

            "details":
                f"Sales Return #{sales_return.return_id} completed"

        })

        return self.return_repo.update(
            sales_return
        )
    
    # ==================================================
    # DELETE
    # ==================================================
    def delete_return(
        self,
        sales_return
    ):

        if sales_return.status != "DRAFT":
            raise ValueError(
                "Only draft returns can be deleted"
            )

        items = self.item_repo.get_by_return(
            sales_return.return_id
        )

        if items:
            raise ValueError(
                "Cannot delete a sales return that contains items"
            )

        self.audit_repo.create({

            "user_id":
                sales_return.user_id,

            "action":
                "DELETE_SALES_RETURN",

            "table_name":
                "sales_returns",

            "record_id":
                sales_return.return_id,

            "details":
                f"Deleted Sales Return #{sales_return.return_id}"

        })

        self.return_repo.delete(
            sales_return
        )

        return True

    # ==========================================
    # CANCEL RETURN
    # ==========================================
    def cancel_return(
        self,
        sales_return_or_id
    ):
        # دعم استقبال كائن أو رقم الـ ID مباشرة لمرونة الـ Controller
        if isinstance(sales_return_or_id, int):
            sales_return = self.return_repo.get_by_id(sales_return_or_id)
            if not sales_return:
                raise ValueError("Sales return not found")
        else:
            sales_return = sales_return_or_id

        # التحقق من عدم التكرار (Idempotency) - إذا كان ملغى مسبقاً
        if sales_return.status == "CANCELLED":
            return sales_return

        if sales_return.status not in ["COMPLETED", "DRAFT"]:
            raise ValueError(
                "Only completed or draft returns can be cancelled"
            )

        # إذا كان الطلب في حالة DRAFT، يتم إلغاؤه مباشرة دون عكس المخزون
        if sales_return.status == "DRAFT":
            sales_return.status = "CANCELLED"
            self.return_repo.update(sales_return)
            
            self.audit_repo.create({
                "user_id": sales_return.user_id,
                "action": "CANCEL_SALES_RETURN_DRAFT",
                "table_name": "sales_returns",
                "record_id": sales_return.return_id,
                "details": f"Draft sales return #{sales_return.return_id} cancelled"
            })
            return sales_return

        # إذا كان الطلب COMPLETED، يجب عكس تأثير المخزون (Transaction Reversal)
        items = self.item_repo.get_by_return(
            sales_return.return_id
        )

        total_cancel_amount = Decimal("0")

        for item in items:
            batch = self.batch_repo.get_by_id(item.batch_id)
            if not batch:
                raise ValueError(f"Batch {item.batch_id} not found")

            inventory = self.inventory_repo.get_by_medicine(item.medicine_id)
            if not inventory:
                raise ValueError(f"Inventory for medicine {item.medicine_id} not found")

            # التحقق من عدم نزول الكمية للسالب قبل العكس (Non-Negative Stock)
            if batch.quantity < item.quantity:
                raise ValueError(
                    f"Insufficient batch quantity to cancel return. "
                    f"Current: {batch.quantity}, Required to reverse: {item.quantity}"
                )

            # عكس كمية الدفعة (-Q)
            batch.quantity -= item.quantity
            self.batch_repo.update(batch)

            # عكس كمية المخزون العام (-Q)
            inventory.quantity -= item.quantity
            self.inventory_repo.update(inventory)

            # تسجيل حركة المخزون المعاكسة باستخدام نوع الحركة المعتمد "RETURN" لتجنب قيود قاعدة البيانات
            self.movement_repo.create({
                "batch_id": batch.batch_id,
                "movement_type": "RETURN",
                "quantity_change": -item.quantity,
                "reference_type": "RETURN",
                "reference_id": sales_return.return_id,
                "notes": f"Cancelled Sales Return #{sales_return.return_id}",
                "created_by": sales_return.user_id
            })

            total_cancel_amount += Decimal(str(item.subtotal))

        # إعادة تعديل إجمالي الفاتورة الأساسية
        invoice = self.invoice_repo.get_by_id(sales_return.invoice_id)
        if invoice:
            invoice.total_amount = (
                Decimal(str(invoice.total_amount))
                + total_cancel_amount
            )
            self.invoice_repo.update(invoice)

        # تحديث حالة المرتجع إلى CANCELLED
        sales_return.status = "CANCELLED"
        self.return_repo.update(sales_return)

        # تسجيل الحدث في الـ Audit Log
        self.audit_repo.create({
            "user_id": sales_return.user_id,
            "action": "CANCEL_SALES_RETURN",
            "table_name": "sales_returns",
            "record_id": sales_return.return_id,
            "details": f"Sales return #{sales_return.return_id} cancelled successfully"
        })

        return sales_return