from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.purchases.repository.purchase_item_repository import PurchaseItemRepository
from modules.purchases.repository.purchase_order_repository import PurchaseOrderRepository
from modules.purchases.services.purchase_item_service import PurchaseItemService

from modules.medicines.repository.medicine_repository import MedicineRepository

from modules.sales.repository.sale_item_repository import SaleItemRepository

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


purchase_item_controller = Blueprint(
    "purchase_items",
    __name__,
    url_prefix="/purchase-items"
)


# ==================================================
# CREATE
# ==================================================
@purchase_item_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_item():

    db = SessionLocal()

    try:

        item_repo = PurchaseItemRepository(db)
        medicine_repo = MedicineRepository(db)
        order_repo = PurchaseOrderRepository(db)

        service = PurchaseItemService(
            item_repo,
            medicine_repo,
            order_repo
        )

        data = request.get_json()

        item = service.create_item(data)

        return jsonify({
            "message": "Purchase item created successfully",
            "purchase_item_id": item.purchase_item_id
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
@purchase_item_controller.route(
    "/<int:purchase_item_id>",
    methods=["GET"]
)
@auth_required
def get_item(purchase_item_id):

    db = SessionLocal()

    try:

        item_repo = PurchaseItemRepository(db)
        medicine_repo = MedicineRepository(db)
        order_repo = PurchaseOrderRepository(db)

        service = PurchaseItemService(
            item_repo,
            medicine_repo,
            order_repo
        )

        item = service.get_item(
            purchase_item_id
        )

        return jsonify({

            "purchase_item_id":
                item.purchase_item_id,

            "purchase_id":
                item.purchase_id,

            "medicine_id":
                item.medicine_id,

            "medicine_name":
                item.medicine.commercial_name,

            "batch_id":
                item.batch_id,

            "batch_number":
                item.batch_number,

            "manufacture_date":
                str(item.manufacture_date)
                if item.manufacture_date
                else None,

            "expiry_date":
                str(item.expiry_date)
                if item.expiry_date
                else None,

            "quantity":
                item.quantity,

            "unit_cost":
                float(item.unit_cost),

            "selling_price":
                float(item.selling_price),

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
# GET BY PURCHASE
# ==================================================
@purchase_item_controller.route(
    "/purchase/<int:purchase_id>",
    methods=["GET"]
)
@auth_required
def get_items_by_purchase(purchase_id):

    db = SessionLocal()

    try:

        item_repo = PurchaseItemRepository(db)
        medicine_repo = MedicineRepository(db)
        order_repo = PurchaseOrderRepository(db)

        # يبقى هنا فقط لأننا نستخدمه لحساب sold
        sale_item_repo = SaleItemRepository(db)

        service = PurchaseItemService(
            item_repo,
            medicine_repo,
            order_repo
        )

        items = service.get_items_by_order(
            purchase_id
        )

        return jsonify([

            {

                "purchase_item_id":
                    item.purchase_item_id,

                "purchase_id":
                    item.purchase_id,

                "medicine_id":
                    item.medicine_id,

                "medicine_name":
                    item.medicine.commercial_name,

                "batch_id":
                    item.batch_id,

                "batch_number":
                    item.batch_number,

                "manufacture_date":
                    str(item.manufacture_date)
                    if item.manufacture_date
                    else None,

                "expiry_date":
                    str(item.expiry_date)
                    if item.expiry_date
                    else None,

                "quantity":
                    item.quantity,

                "sold":
                    sale_item_repo.get_total_sold_by_batch(
                        item.batch_id
                    )
                    if item.batch_id
                    else 0,

                "unit_cost":
                    float(item.unit_cost),

                "selling_price":
                    float(item.selling_price),

                "subtotal":
                    float(item.subtotal)

            }

            for item in items

        ])

    finally:
        db.close()


# ==================================================
# UPDATE
# ==================================================
@purchase_item_controller.route(
    "/<int:purchase_item_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def update_item(purchase_item_id):

    db = SessionLocal()

    try:

        item_repo = PurchaseItemRepository(db)
        medicine_repo = MedicineRepository(db)
        order_repo = PurchaseOrderRepository(db)

        service = PurchaseItemService(
            item_repo,
            medicine_repo,
            order_repo
        )

        item = service.get_item(
            purchase_item_id
        )

        data = request.get_json()

        updated = service.update_item(
            item,
            data
        )

        return jsonify({

            "message":
                "Purchase item updated successfully",

            "purchase_item_id":
                updated.purchase_item_id

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
@purchase_item_controller.route(
    "/<int:purchase_item_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2])
def delete_item(purchase_item_id):

    db = SessionLocal()

    try:

        item_repo = PurchaseItemRepository(db)
        medicine_repo = MedicineRepository(db)
        order_repo = PurchaseOrderRepository(db)

        service = PurchaseItemService(
            item_repo,
            medicine_repo,
            order_repo
        )

        item = service.get_item(
            purchase_item_id
        )

        service.delete_item(
            item
        )

        return jsonify({
            "message":
                "Purchase item deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()

    


    