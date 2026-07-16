from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.sales.repository.sale_item_repository import SaleItemRepository
from modules.sales.repository.sales_invoice_repository import SalesInvoiceRepository
from modules.sales.services.sale_item_service import SaleItemService

from modules.medicines.repository.medicine_repository import MedicineRepository
from modules.medicines.repository.medicine_batch_repository import MedicineBatchRepository

from modules.stock_movements.repository.stock_movement_repository import StockMovementRepository
from modules.inventory.repository.inventory_repository import InventoryRepository
from modules.audit_logs.repository.audit_log_repository import AuditLogRepository

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


sale_item_controller = Blueprint(
    "sale_items",
    __name__,
    url_prefix="/sale-items"
)


def get_service(db):

    item_repo = SaleItemRepository(db)
    invoice_repo = SalesInvoiceRepository(db)

    medicine_repo = MedicineRepository(db)
    batch_repo = MedicineBatchRepository(db)

    movement_repo = StockMovementRepository(db)
    inventory_repo = InventoryRepository(db)
    audit_repo = AuditLogRepository(db)

    return SaleItemService(
        item_repo,
        invoice_repo,
        medicine_repo,
        batch_repo,
        movement_repo,
        inventory_repo,
        audit_repo
    )


# ==================================================
# CREATE
# ==================================================
@sale_item_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_sale_item():

    db = SessionLocal()

    try:

        service = get_service(db)

        items = service.create_item(
            request.get_json()
        )

        return jsonify({
            "message": "Sale items created successfully",
            "sale_item_ids": [
                item.sale_item_id
                for item in items
            ]
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
@sale_item_controller.route(
    "/<int:sale_item_id>",
    methods=["GET"]
)
@auth_required
def get_sale_item(sale_item_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        item = service.get_item(
            sale_item_id
        )

        return jsonify({
            "sale_item_id": item.sale_item_id,
            "invoice_id": item.invoice_id,
            "medicine_id": item.medicine_id,
            "batch_id": item.batch_id,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "subtotal": float(item.subtotal)
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# GET BY INVOICE
# ==================================================
@sale_item_controller.route(
    "/invoice/<int:invoice_id>",
    methods=["GET"]
)
@auth_required
def get_invoice_items(invoice_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        items = service.get_items_by_invoice(
            invoice_id
        )

        return jsonify([
            {
                "sale_item_id": item.sale_item_id,
                "invoice_id": item.invoice_id,
                "medicine_id": item.medicine_id,
                "batch_id": item.batch_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal)
            }
            for item in items
        ])

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()
# ==================================================
# UPDATE
# ==================================================
@sale_item_controller.route(
    "/<int:sale_item_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2, 3])
def update_sale_item(sale_item_id):

    return jsonify({
        "error":
            "Sale items cannot be edited. Delete and recreate the item."
    }), 400


# ==================================================
# DELETE
# ==================================================
@sale_item_controller.route(
    "/<int:sale_item_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2, 3])
def delete_sale_item(sale_item_id):

    db = SessionLocal()

    try:

        service = get_service(db)

        item = service.get_item(
            sale_item_id
        )

        service.delete_item(
            item
        )

        return jsonify({
            "message": "Sale item deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()