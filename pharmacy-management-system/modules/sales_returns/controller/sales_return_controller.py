from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.sales_returns.repository.sales_return_repository import (
    SalesReturnRepository
)
from modules.sales_returns.repository.sales_return_item_repository import (
    SalesReturnItemRepository
)

from modules.sales_returns.services.sales_return_service import (
    SalesReturnService
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

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


sales_return_controller = Blueprint(
    "sales_returns",
    __name__,
    url_prefix="/sales-returns"
)


def build_service(db):

    return_repo = SalesReturnRepository(db)
    item_repo = SalesReturnItemRepository(db)

    invoice_repo = SalesInvoiceRepository(db)
    user_repo = UserRepository(db)

    sale_item_repo = SaleItemRepository(db)

    batch_repo = MedicineBatchRepository(db)
    inventory_repo = InventoryRepository(db)
    movement_repo = StockMovementRepository(db)

    audit_repo = AuditLogRepository(db)

    return SalesReturnService(
        return_repo,
        item_repo,
        invoice_repo,
        user_repo,
        sale_item_repo,
        batch_repo,
        inventory_repo,
        movement_repo,
        audit_repo
    )


# ==================================================
# CREATE
# ==================================================
@sales_return_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_return():

    db = SessionLocal()

    try:

        service = build_service(db)

        data = request.get_json()

        data["user_id"] = request.user["user_id"]

        existing = (
            service.return_repo.get_draft_by_invoice(
                data["invoice_id"]
            )
        )

        sales_return = service.create_return(
            data
        )

        return jsonify({
            "message": "Sales return ready",
            "return_id": sales_return.return_id,
            "status": sales_return.status
        }), 200 if existing else 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET ALL
# ==================================================
@sales_return_controller.route("/", methods=["GET"])
@auth_required
def get_returns():

    db = SessionLocal()

    try:

        service = build_service(db)

        returns = service.get_all_returns()

        return jsonify([
            {
                "return_id": r.return_id,
                "invoice_id": r.invoice_id,
                "status": r.status,
                "total_amount": float(r.total_amount),
                "return_date": str(r.return_date)
                if r.return_date else None
            }
            for r in returns
        ])

    finally:
        db.close()


# ==================================================
# GET RETURNED INVOICES
# ==================================================
@sales_return_controller.route(
    "/invoices",
    methods=["GET"]
)
@auth_required
def get_returned_invoices():

    db = SessionLocal()

    try:

        service = build_service(db)

        return jsonify(
            service.get_returned_invoices()
        )

    finally:
        db.close()

# ==================================================
# GET DRAFT BY INVOICE
# ==================================================
@sales_return_controller.route(
    "/invoice/<int:invoice_id>/draft",
    methods=["GET"]
)
@auth_required
def get_draft_return(invoice_id):

    db = SessionLocal()

    try:

        repo = SalesReturnRepository(db)

        sales_return = repo.get_draft_by_invoice(
            invoice_id
        )

        if not sales_return:

            return jsonify({}), 404

        return jsonify({

            "return_id":
                sales_return.return_id,

            "invoice_id":
                sales_return.invoice_id,

            "status":
                sales_return.status

        })

    finally:
        db.close()
        

# ==================================================
# GET RETURNS BY INVOICE
# ==================================================
@sales_return_controller.route(
    "/invoice/<int:invoice_id>",
    methods=["GET"]
)
@auth_required
def get_returns_by_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        returns = service.get_returns_by_invoice(
            invoice_id
        )

        return jsonify([

            {

                "return_id":
                    r.return_id,

                "invoice_id":
                    r.invoice_id,

                "status":
                    r.status,

                "total_amount":
                    float(r.total_amount),

                "return_date":
                    str(r.return_date)
                    if r.return_date
                    else None

            }

            for r in returns

        ])

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()
        
# ==================================================
# GET BY ID
# ==================================================
@sales_return_controller.route(
    "/<int:return_id>",
    methods=["GET"]
)
@auth_required
def get_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        sales_return = service.get_return(
            return_id
        )

        return jsonify({

            "return_id": sales_return.return_id,

            "invoice_id": sales_return.invoice_id,

            "status": sales_return.status,

            "total_amount": float(
                sales_return.total_amount
            ),

            "return_date": str(
                sales_return.return_date
            ) if sales_return.return_date else None,

            "notes": sales_return.notes
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# COMPLETE
# ==================================================
@sales_return_controller.route(
    "/<int:return_id>/complete",
    methods=["POST"]
)
@auth_required
@role_required([1, 2, 3])
def complete_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        sales_return = service.get_return(
            return_id
        )

        sales_return = service.complete_return(
            sales_return
        )

        return jsonify({

            "message":
                "Sales return completed successfully",

            "return_id":
                sales_return.return_id,

            "status":
                sales_return.status
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
@sales_return_controller.route(
    "/<int:return_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2, 3])
def delete_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        sales_return = service.get_return(
            return_id
        )

        service.delete_return(
            sales_return
        )

        return jsonify({
            "message":
                "Sales return deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# CANCEL RETURN (تم التعديل لدعم PUT و POST معاً)
# ==================================================
@sales_return_controller.route(
    "/<int:return_id>/cancel",
    methods=["PUT", "POST"]
)
@auth_required
@role_required([1, 2, 3])
def cancel_return(return_id):

    db = SessionLocal()

    try:
        service = build_service(db)

        sales_return = service.get_return(
            return_id
        )

        sales_return = service.cancel_return(
            sales_return
        )

        return jsonify({
            "message": "Sales return cancelled successfully",
            "return_id": sales_return.return_id,
            "status": sales_return.status
        })

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()