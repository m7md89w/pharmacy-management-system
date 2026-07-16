import time

from modules.sales.repository.sales_invoice_repository import (
    SalesInvoiceRepository
)

from modules.users.repository.user_repository import (
    UserRepository
)
from modules.customers.repository.customer_repository import (
    CustomerRepository
)
from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)


class SalesInvoiceService:

    VALID_PAYMENT_METHODS = [
        "CASH",
        "CARD",
        "INSURANCE",
        "OTHER"
    ]

    VALID_STATUSES = [
        "DRAFT",
        "COMPLETED",
        "CANCELLED",
        "REFUNDED"
    ]

    def __init__(
        self,
        invoice_repo: SalesInvoiceRepository,
        user_repo: UserRepository,
        customer_repo: CustomerRepository,
        audit_repo: AuditLogRepository
    ):
        self.invoice_repo = invoice_repo
        self.user_repo = user_repo
        self.customer_repo = customer_repo
        self.audit_repo = audit_repo

    def create_invoice(
        self,
        data: dict
    ):

        user = self.user_repo.get_by_id(
            data["user_id"]
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        if data.get("customer_id"):

            customer = self.customer_repo.get_by_id(
                data["customer_id"]
            )

            if not customer:
                raise ValueError(
                    "Customer not found"
                )

        if not data.get(
            "invoice_number"
        ):

            data["invoice_number"] = (
                f"INV-{int(time.time())}"
            )

        existing = (
            self.invoice_repo.get_by_invoice_number(
                data["invoice_number"]
            )
        )

        if existing:
            raise ValueError(
                "Invoice number already exists"
            )

        payment_method = data.get(
            "payment_method",
            "CASH"
        )

        if (
            payment_method
            not in self.VALID_PAYMENT_METHODS
        ):
            raise ValueError(
                "Invalid payment method"
            )

        data.setdefault(
            "status",
            "DRAFT"
        )

        data.setdefault(
            "discount",
            0
        )

        data.setdefault(
            "total_amount",
            0
        )

        invoice = self.invoice_repo.create(
            data
        )

        self.audit_repo.create({
            "user_id": invoice.user_id,
            "action": "CREATE_SALE_INVOICE",
            "table_name": "sales_invoices",
            "record_id": invoice.invoice_id,
            "details":
                f"Invoice #{invoice.invoice_number} created"
        })

        return invoice

    def get_invoice(
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

        return invoice

    def get_all_invoices(self):

        return self.invoice_repo.get_all()
    
    def update_invoice(
        self,
        invoice,
        data: dict
    ):

        if invoice.status == "COMPLETED":
            raise ValueError(
                "Completed invoices cannot be modified"
            )

        if "status" in data:

            if (
                data["status"]
                not in self.VALID_STATUSES
            ):
                raise ValueError(
                    "Invalid status"
                )

            if invoice.status != data["status"]:

                old_status = invoice.status

                invoice.status = data["status"]

                self.audit_repo.create({
                    "user_id": invoice.user_id,
                    "action": "UPDATE_SALE_INVOICE_STATUS",
                    "table_name": "sales_invoices",
                    "record_id": invoice.invoice_id,
                    "details":
                        f"Status changed from "
                        f"{old_status} to "
                        f"{invoice.status}"
                })

        if "discount" in data:

            discount = float(
                data["discount"]
            )

            if discount < 0:
                raise ValueError(
                    "Discount cannot be negative"
                )

            old_discount = invoice.discount

            invoice.discount = discount

            self.audit_repo.create({
                "user_id": invoice.user_id,
                "action": "UPDATE_SALE_DISCOUNT",
                "table_name": "sales_invoices",
                "record_id": invoice.invoice_id,
                "details":
                    f"Discount changed from "
                    f"{old_discount} to "
                    f"{invoice.discount}"
            })

        if "payment_method" in data:

            if (
                data["payment_method"]
                not in self.VALID_PAYMENT_METHODS
            ):
                raise ValueError(
                    "Invalid payment method"
                )

            old_payment = (
                invoice.payment_method
            )

            invoice.payment_method = (
                data["payment_method"]
            )

            self.audit_repo.create({
                "user_id": invoice.user_id,
                "action": "UPDATE_PAYMENT_METHOD",
                "table_name": "sales_invoices",
                "record_id": invoice.invoice_id,
                "details":
                    f"Payment changed from "
                    f"{old_payment} to "
                    f"{invoice.payment_method}"
            })

        return self.invoice_repo.update(
            invoice
        )
    
    # ==========================================
    # COMPLETE INVOICE
    # ==========================================
    def complete_invoice(
        self,
        invoice
    ):

        if invoice.status != "DRAFT":
            raise ValueError(
                "Only draft invoices can be completed"
            )

        if not invoice.sale_items:
            raise ValueError(
                "Invoice has no items"
            )

        if invoice.total_amount <= 0:
            raise ValueError(
                "Invoice total must be greater than zero"
            )

        invoice.status = "COMPLETED"

        self.audit_repo.create({
            "user_id": invoice.user_id,
            "action": "COMPLETE_SALE",
            "table_name": "sales_invoices",
            "record_id": invoice.invoice_id,
            "details":
                f"Invoice #{invoice.invoice_number} completed"
        })

        return self.invoice_repo.update(
            invoice
        )

    # ==========================================
    # DELETE
    # ==========================================
    def delete_invoice(
        self,
        invoice
    ):

        if invoice.status != "DRAFT":
            raise ValueError(
                "Only draft invoices can be deleted"
            )

        self.audit_repo.create({
            "user_id": invoice.user_id,
            "action": "DELETE_SALE_INVOICE",
            "table_name": "sales_invoices",
            "record_id": invoice.invoice_id,
            "details":
                f"Invoice #{invoice.invoice_number} deleted"
        })

        return self.invoice_repo.delete(
            invoice
        )

    # ==========================================
    # GET BY CUSTOMER
    # ==========================================
    def get_invoices_by_customer(
        self,
        customer_id: int
    ):

        return self.invoice_repo.get_by_customer(
            customer_id
        )

    # ==========================================
    # GET BY STATUS
    # ==========================================
    def get_invoices_by_status(
        self,
        status: str
    ):

        if status not in self.VALID_STATUSES:
            raise ValueError(
                "Invalid status"
            )

        return self.invoice_repo.get_by_status(
            status
        )