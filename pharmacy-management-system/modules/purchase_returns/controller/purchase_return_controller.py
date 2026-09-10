from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.purchase_returns.repository.purchase_return_repository import (
    PurchaseReturnRepository
)

from modules.purchase_returns.repository.purchase_return_item_repository import (
    PurchaseReturnItemRepository
)

from modules.purchase_returns.services.purchase_return_service import (
    PurchaseReturnService
)

from modules.purchases.repository.purchase_order_repository import (
    PurchaseOrderRepository
)

from modules.purchases.repository.purchase_item_repository import (
    PurchaseItemRepository
)

from modules.users.repository.user_repository import (
    UserRepository
)

from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
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


purchase_return_controller = Blueprint(
    "purchase_returns",
    __name__,
    url_prefix="/purchase-returns"
)


def build_service(db):

    return_repo = PurchaseReturnRepository(db)

    item_repo = PurchaseReturnItemRepository(db)

    purchase_repo = PurchaseOrderRepository(db)

    purchase_item_repo = PurchaseItemRepository(db)

    user_repo = UserRepository(db)

    batch_repo = MedicineBatchRepository(db)

    medicine_repo = MedicineRepository(db)

    inventory_repo = InventoryRepository(db)

    movement_repo = StockMovementRepository(db)

    audit_repo = AuditLogRepository(db)

    return PurchaseReturnService(

        return_repo,

        item_repo,

        purchase_repo,

        purchase_item_repo,

        user_repo,

        batch_repo,

        inventory_repo,

        movement_repo,

        audit_repo

    )

# ==================================================
# CREATE
# ==================================================
@purchase_return_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_return():

    db = SessionLocal()

    try:

        service = build_service(db)

        data = request.get_json()

        data["user_id"] = request.user["user_id"]

        existing = (
            service.return_repo.get_draft_by_purchase(
                data["purchase_id"]
            )
        )

       

        purchase_return = service.create_return(data)
        
        return jsonify({

            "message":
                "Purchase return ready",

            "return_id":
                purchase_return.return_id,

            "status":
                purchase_return.status

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
@purchase_return_controller.route("/", methods=["GET"])
@auth_required
def get_returns():

    db = SessionLocal()

    try:

        service = build_service(db)

        returns = service.get_all_returns()

        return jsonify([

            {

                "return_id":
                    r.return_id,

                "purchase_id":
                    r.purchase_id,

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

    finally:
        db.close()

# ==================================================
# GET RETURNED PURCHASES
# ==================================================
@purchase_return_controller.route(
    "/purchases",
    methods=["GET"]
)
@auth_required
def get_returned_purchases():

    db = SessionLocal()

    try:

        service = build_service(db)

        return jsonify(
            service.get_returned_purchases()
        )

    finally:
        db.close()

# ==================================================
# GET RETURNS BY PURCHASE
# ==================================================
@purchase_return_controller.route(
    "/purchase/<int:purchase_id>",
    methods=["GET"]
)
@auth_required
def get_returns_by_purchase(
    purchase_id
):

    db = SessionLocal()

    try:

        service = build_service(db)

        returns = (
            service.get_returns_by_purchase(
                purchase_id
            )
        )

        return jsonify([

            {

                "return_id":
                    r.return_id,

                "purchase_id":
                    r.purchase_id,

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
@purchase_return_controller.route(
    "/<int:return_id>",
    methods=["GET"]
)
@auth_required
def get_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        purchase_return = service.get_return(
            return_id
        )

        return jsonify({

            "return_id":
                purchase_return.return_id,

            "purchase_id":
                purchase_return.purchase_id,

            "status":
                purchase_return.status,

            "total_amount":
                float(
                    purchase_return.total_amount
                ),

            "return_date":
                str(
                    purchase_return.return_date
                )
                if purchase_return.return_date
                else None,

            "notes":
                purchase_return.notes

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
@purchase_return_controller.route(
    "/<int:return_id>/complete",
    methods=["POST"]
)
@auth_required
@role_required([1, 2, 3])
def complete_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        purchase_return = service.get_return(
            return_id
        )

        purchase_return = service.complete_return(
            purchase_return
        )

        return jsonify({

            "message":
                "Purchase return completed successfully",

            "return_id":
                purchase_return.return_id,

            "status":
                purchase_return.status

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
@purchase_return_controller.route(
    "/<int:return_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2, 3])
def delete_return(return_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        purchase_return = service.get_return(
            return_id
        )

        service.delete_return(
            purchase_return
        )

        return jsonify({

            "message":
                "Purchase return deleted successfully"

        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


# ==================================================
# GET DRAFT BY PURCHASE
# ==================================================
@purchase_return_controller.route(
    "/purchase/<int:purchase_id>/draft",
    methods=["GET"]
)
@auth_required
def get_draft_return(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        purchase_return = (
            service.return_repo.get_draft_by_purchase(
                purchase_id
            )
        )

        if not purchase_return:

            return jsonify(None), 200

        return jsonify({

            "return_id":
                purchase_return.return_id,

            "purchase_id":
                purchase_return.purchase_id,

            "status":
                purchase_return.status,

            "total_amount":
                float(purchase_return.total_amount),

            "return_date":
                str(purchase_return.return_date)
                if purchase_return.return_date
                else None,

            "notes":
                purchase_return.notes

        })

    finally:
        db.close()

# ==================================================
# GET DRAFT RETURN BY PURCHASE
# ==================================================
@purchase_return_controller.route(
    "/purchase/<int:purchase_id>/draft",
    methods=["GET"]
)
@auth_required
def get_draft_by_purchase(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        purchase_return = (
            service.return_repo.get_draft_by_purchase(
                purchase_id
            )
        )

        if not purchase_return:

            return jsonify(None), 200

        return jsonify({

            "return_id":
                purchase_return.return_id,

            "purchase_id":
                purchase_return.purchase_id,

            "status":
                purchase_return.status,

            "total_amount":
                float(purchase_return.total_amount),

            "return_date":
                (
                    str(purchase_return.return_date)
                    if purchase_return.return_date
                    else None
                ),

            "notes":
                purchase_return.notes

        })

    finally:
        db.close()