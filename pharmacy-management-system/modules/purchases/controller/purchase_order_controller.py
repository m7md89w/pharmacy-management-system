from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.purchases.repository.purchase_order_repository import (
    PurchaseOrderRepository
)
from modules.purchases.repository.purchase_item_repository import (
    PurchaseItemRepository
)
from modules.purchases.services.purchase_order_service import (
    PurchaseOrderService
)

from modules.suppliers.repository.supplier_repository import (
    SupplierRepository
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

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


purchase_order_controller = Blueprint(
    "purchase_orders",
    __name__,
    url_prefix="/purchase-orders"
)


def build_service(db):

    order_repo = PurchaseOrderRepository(db)
    supplier_repo = SupplierRepository(db)
    item_repo = PurchaseItemRepository(db)
    batch_repo = MedicineBatchRepository(db)
    movement_repo = StockMovementRepository(db)
    inventory_repo = InventoryRepository(db)
    audit_repo = AuditLogRepository(db)

    return PurchaseOrderService(
        order_repo,
        supplier_repo,
        item_repo,
        batch_repo,
        movement_repo,
        inventory_repo,
        audit_repo
    )


# ==================================================
# CREATE
# ==================================================
@purchase_order_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_order():

    db = SessionLocal()

    try:

        service = build_service(db)

        data = request.get_json()

        data["user_id"] = request.user["user_id"]

        order = service.create_order(data)

        return jsonify({
            "message": "Purchase order created successfully",
            "purchase_id": order.purchase_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET ALL
# ==================================================
@purchase_order_controller.route("/", methods=["GET"])
@auth_required
def get_orders():

    db = SessionLocal()

    try:

        service = build_service(db)

        orders = service.get_all_orders()

        return jsonify([
            {
                "purchase_id": order.purchase_id,
                "supplier_id": order.supplier_id,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "order_date": str(order.order_date),
                "received_date": (
                    str(order.received_date)
                    if order.received_date
                    else None
                )
            }
            for order in orders
        ])

    finally:
        db.close()


# ==================================================
# GET BY ID
# ==================================================
@purchase_order_controller.route(
    "/<int:purchase_id>",
    methods=["GET"]
)
@auth_required
def get_order(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        order = service.get_order(
            purchase_id
        )

        return jsonify({
            "purchase_id": order.purchase_id,
            "supplier_id": order.supplier_id,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "order_date": str(order.order_date),
            "received_date": (
                str(order.received_date)
                if order.received_date
                else None
            )
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# UPDATE
# ==================================================
@purchase_order_controller.route(
    "/<int:purchase_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def update_order(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        order = service.get_order(
            purchase_id
        )

        data = request.get_json()

        updated = service.update_order(
            order,
            data
        )

        return jsonify({
            "message": "Purchase order updated successfully",
            "purchase_id": updated.purchase_id,
            "status": updated.status,
            "received_date": (
                str(updated.received_date)
                if updated.received_date
                else None
            )
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
@purchase_order_controller.route(
    "/<int:purchase_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2])
def delete_order(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        order = service.get_order(
            purchase_id
        )

        service.delete_order(
            order
        )

        return jsonify({
            "message":
                "Purchase order deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()

# ==================================================
# GET BY STATUS
# ==================================================
@purchase_order_controller.route(
    "/status/<status>",
    methods=["GET"]
)
@auth_required
def get_orders_by_status(status):

    db = SessionLocal()

    try:

        service = build_service(db)

        orders = service.get_orders_by_status(
            status.upper()
        )

        return jsonify([

            {

                "purchase_id":
                    order.purchase_id,

                "supplier_id":
                    order.supplier_id,

                "status":
                    order.status,

                "total_amount":
                    float(order.total_amount),

                "order_date":
                    str(order.order_date),

                "received_date":
                    (
                        str(order.received_date)
                        if order.received_date
                        else None
                    )

            }

            for order in orders

        ])

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()