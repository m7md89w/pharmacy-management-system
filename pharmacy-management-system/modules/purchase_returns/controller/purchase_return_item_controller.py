from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.purchase_returns.repository.purchase_return_item_repository import (
    PurchaseReturnItemRepository
)

from modules.purchase_returns.repository.purchase_return_repository import (
    PurchaseReturnRepository
)

from modules.purchase_returns.services.purchase_return_item_service import (
    PurchaseReturnItemService
)

from modules.purchases.repository.purchase_item_repository import (
    PurchaseItemRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)

from modules.audit_logs.repository.audit_log_repository import (
    AuditLogRepository
)

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository
)
purchase_return_item_controller = Blueprint(
    "purchase_return_items",
    __name__,
    url_prefix="/purchase-return-items"
)


def build_service(db):

    item_repo = PurchaseReturnItemRepository(db)

    return_repo = PurchaseReturnRepository(db)

    purchase_item_repo = PurchaseItemRepository(db)

    medicine_repo = MedicineRepository(db)
    batch_repo = MedicineBatchRepository(db)

    audit_repo = AuditLogRepository(db)

    return PurchaseReturnItemService(

        item_repo,

        return_repo,

        purchase_item_repo,

        medicine_repo,

        batch_repo,

        audit_repo,


    )


# ==================================================
# CREATE
# ==================================================
@purchase_return_item_controller.route(
    "/",
    methods=["POST"]
)
@auth_required
@role_required([1, 2, 3])
def create_item():

    db = SessionLocal()

    try:

        service = build_service(db)

        data = request.get_json()

        item = service.create_item(
            data
        )

        return jsonify({

            "message":
                "Purchase return item created successfully",

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
@purchase_return_item_controller.route(
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

        return jsonify([

            {

                "return_item_id":
                    item.return_item_id,

                "purchase_item_id":
                    item.purchase_item_id,

                "medicine_id":
                    item.medicine_id,

                "medicine_name":
                    item.medicine.commercial_name,

                "batch_id":
                    item.batch_id,

                "quantity":
                    item.quantity,

                "unit_cost":
                    float(item.unit_cost),

                "subtotal":
                    float(item.subtotal),

                "reason":
                    item.reason

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
# GET BY ID
# ==================================================
@purchase_return_item_controller.route(
    "/<int:return_item_id>",
    methods=["GET"]
)
@auth_required
def get_item(return_item_id):

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

            "purchase_item_id":
                item.purchase_item_id,

            "medicine_id":
                item.medicine_id,

            "medicine_name":
                item.medicine.commercial_name,

            "batch_id":
                item.batch_id,

            "quantity":
                item.quantity,

            "unit_cost":
                float(item.unit_cost),

            "subtotal":
                float(item.subtotal),

            "reason":
                item.reason

        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# ==================================================
# GET COMPLETED ITEMS BY PURCHASE
# ==================================================
@purchase_return_item_controller.route(
    "/purchase/<int:purchase_id>",
    methods=["GET"]
)
@auth_required
def get_completed_items_by_purchase(purchase_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        items = service.get_completed_items_by_purchase(
            purchase_id
        )

        return jsonify([

            {

                "return_item_id":
                    item.return_item_id,

                "return_id":
                    item.return_id,

                "purchase_item_id":
                    item.purchase_item_id,

                "medicine_id":
                    item.medicine_id,

                "medicine_name":
                    item.medicine.commercial_name,

                "batch_id":
                    item.batch_id,

                "quantity":
                    item.quantity,

                "unit_cost":
                    float(item.unit_cost),

                "subtotal":
                    float(item.subtotal),

                "reason":
                    item.reason

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
@purchase_return_item_controller.route(
    "/<int:return_item_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2, 3])
def update_item(return_item_id):

    db = SessionLocal()

    try:

        service = build_service(db)

        item = service.get_item(
            return_item_id
        )

        data = request.get_json()

        item = service.update_item(
            item,
            data["quantity"]
        )

        return jsonify({

            "message":
                "Purchase return item updated successfully",

            "return_item_id":
                item.return_item_id,

            "quantity":
                item.quantity,

            "subtotal":
                float(item.subtotal)

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
@purchase_return_item_controller.route(
    "/<int:return_item_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2, 3])
def delete_item(return_item_id):

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
                "Purchase return item deleted successfully"

        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()

