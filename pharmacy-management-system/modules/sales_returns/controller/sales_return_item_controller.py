from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.sales_returns.repository.sales_return_repository import (
    SalesReturnRepository
)
from modules.sales_returns.repository.sales_return_item_repository import (
    SalesReturnItemRepository
)

from modules.sales_returns.services.sales_return_item_service import (
    SalesReturnItemService
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

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


sales_return_item_controller = Blueprint(
    "sales_return_items",
    __name__,
    url_prefix="/sales-return-items"
)


def build_service(db):

    item_repo = SalesReturnItemRepository(db)
    return_repo = SalesReturnRepository(db)

    sale_item_repo = SaleItemRepository(db)
    invoice_repo = SalesInvoiceRepository(db)

    medicine_repo = MedicineRepository(db)
    batch_repo = MedicineBatchRepository(db)

    inventory_repo = InventoryRepository(db)
    movement_repo = StockMovementRepository(db)

    audit_repo = AuditLogRepository(db)

    return SalesReturnItemService(
        item_repo,
        return_repo,
        sale_item_repo,
        invoice_repo,
        medicine_repo,
        batch_repo,
        inventory_repo,
        movement_repo,
        audit_repo
    )


# ==================================================
# CREATE
# ==================================================
@sales_return_item_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_return_item():

    db = SessionLocal()

    try:

        service = build_service(db)

        item = service.create_item(
            request.get_json()
        )

        return jsonify({

            "message":
                "Return item saved successfully",

            "return_item_id":
                item.return_item_id

        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET ITEMS BY RETURN
# ==================================================
@sales_return_item_controller.route(
    "/return/<int:return_id>",
    methods=["GET"]
)
@auth_required
def get_return_items(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        items = service.get_items_by_return(
            return_id
        )

        result = []

        for item in items:

            result.append({

                "return_item_id":
                    item.return_item_id,

                "return_id":
                    item.return_id,

                "sale_item_id":
                    item.sale_item_id,

                "medicine_id":
                    item.medicine_id,

                "batch_id":
                    item.batch_id,

                "quantity":
                    item.quantity,

                "unit_price":
                    float(item.unit_price),

                "subtotal":
                    float(item.subtotal)

            })

        return jsonify(result)

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# GET COMPLETED ITEMS BY INVOICE
# ==================================================
@sales_return_item_controller.route(
    "/invoice/<int:invoice_id>",
    methods=["GET"]
)
@auth_required
def get_completed_items_by_invoice(invoice_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        items = service.get_completed_items_by_invoice(
            invoice_id
        )

        result = []

        for item in items:

            result.append({

                "return_item_id":
                    item.return_item_id,

                "return_id":
                    item.return_id,

                "sale_item_id":
                    item.sale_item_id,

                "medicine_id":
                    item.medicine_id,

                "batch_id":
                    item.batch_id,

                "quantity":
                    item.quantity,

                "unit_price":
                    float(item.unit_price),

                "subtotal":
                    float(item.subtotal)

            })

        return jsonify(result)

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()

# ==================================================
# GET BY ID
# ==================================================
@sales_return_item_controller.route(
    "/<int:return_item_id>",
    methods=["GET"]
)
@auth_required
def get_return_item(return_item_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        item = service.get_item(
            return_item_id
        )

        return jsonify({

            "return_item_id":
                item.return_item_id,

            "return_id":
                item.return_id,

            "sale_item_id":
                item.sale_item_id,

            "medicine_id":
                item.medicine_id,

            "batch_id":
                item.batch_id,

            "quantity":
                item.quantity,

            "unit_price":
                float(item.unit_price),

            "subtotal":
                float(item.subtotal)

        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# DELETE
# ==================================================
@sales_return_item_controller.route(
    "/<int:return_item_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2, 3])
def delete_return_item(return_item_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        item = service.get_item(
            return_item_id
        )

        service.delete_item(
            item
        )

        return jsonify({
            "message":
                "Return item deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()