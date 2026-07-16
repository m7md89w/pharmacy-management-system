from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.sales.repository.sales_invoice_repository import (
    SalesInvoiceRepository
)
from modules.sales.services.sales_invoice_service import (
    SalesInvoiceService
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

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)


sales_invoice_controller = Blueprint(
    "sales_invoices",
    __name__,
    url_prefix="/sales-invoices"
)


def get_service(db):

    invoice_repo = SalesInvoiceRepository(db)
    user_repo = UserRepository(db)
    customer_repo = CustomerRepository(db)
    audit_repo = AuditLogRepository(db)

    return SalesInvoiceService(
        invoice_repo,
        user_repo,
        customer_repo,
        audit_repo
    )


# ==================================================
# CREATE
# ==================================================
@sales_invoice_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_invoice():

    db = SessionLocal()

    try:

        service = get_service(db)

        data = request.get_json()

        data["user_id"] = request.user["user_id"]

        invoice = service.create_invoice(
            data
        )

        return jsonify({
            "message": "Invoice created successfully",
            "invoice_id": invoice.invoice_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET BY ID
# ==================================================
@sales_invoice_controller.route(
    "/<int:invoice_id>",
    methods=["GET"]
)
@auth_required
def get_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoice = service.get_invoice(
            invoice_id
        )

        return jsonify({
            "invoice_id": invoice.invoice_id,
            "invoice_number": invoice.invoice_number,
            "customer_id": invoice.customer_id,
            "user_id": invoice.user_id,
            "sale_date": str(invoice.sale_date),
            "total_amount": float(invoice.total_amount),
            "discount": float(invoice.discount),
            "payment_method": invoice.payment_method,
            "status": invoice.status
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# GET ALL
# ==================================================
@sales_invoice_controller.route("/", methods=["GET"])
@auth_required
def get_all_invoices():

    db = SessionLocal()

    try:

        service = get_service(db)

        invoices = service.get_all_invoices()

        return jsonify([
            {
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "customer_id": invoice.customer_id,
                "user_id": invoice.user_id,
                "sale_date": str(invoice.sale_date),
                "total_amount": float(invoice.total_amount),
                "discount": float(invoice.discount),
                "payment_method": invoice.payment_method,
                "status": invoice.status
            }
            for invoice in invoices
        ])

    finally:
        db.close()

# ==================================================
# UPDATE
# ==================================================
@sales_invoice_controller.route(
    "/<int:invoice_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2, 3])
def update_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoice = service.get_invoice(
            invoice_id
        )

        data = request.get_json()

        updated = service.update_invoice(
            invoice,
            data
        )

        return jsonify({
            "message": "Invoice updated successfully",
            "invoice_id": updated.invoice_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# COMPLETE INVOICE
# ==================================================
@sales_invoice_controller.route(
    "/<int:invoice_id>/complete",
    methods=["POST"]
)
@auth_required
@role_required([1, 2, 3])
def complete_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoice = service.get_invoice(
            invoice_id
        )

        completed = service.complete_invoice(
            invoice
        )

        return jsonify({
            "message": "Invoice completed successfully",
            "invoice_id": completed.invoice_id,
            "status": completed.status
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()

# ==================================================
# DELETE
# ==================================================
@sales_invoice_controller.route(
    "/<int:invoice_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoice = service.get_invoice(
            invoice_id
        )

        service.delete_invoice(
            invoice
        )

        return jsonify({
            "message":
                "Invoice deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET BY CUSTOMER
# ==================================================
@sales_invoice_controller.route(
    "/customer/<int:customer_id>",
    methods=["GET"]
)
@auth_required
def get_customer_invoices(customer_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoices = service.get_invoices_by_customer(
            customer_id
        )

        return jsonify([
            {
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "total_amount": float(
                    invoice.total_amount
                ),
                "status": invoice.status
            }
            for invoice in invoices
        ])

    finally:
        db.close()


# ==================================================
# GET BY STATUS
# ==================================================
@sales_invoice_controller.route(
    "/status/<status>",
    methods=["GET"]
)
@auth_required
def get_status_invoices(status):

    db = SessionLocal()

    try:

        service = get_service(db)

        invoices = service.get_invoices_by_status(
            status
        )

        return jsonify([
            {
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "total_amount": float(
                    invoice.total_amount
                ),
                "status": invoice.status
            }
            for invoice in invoices
        ])

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()
