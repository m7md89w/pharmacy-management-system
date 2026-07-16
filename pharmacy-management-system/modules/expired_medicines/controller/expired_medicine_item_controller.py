from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.expired_medicines.repository.expired_medicine_item_repository import (
    ExpiredMedicineItemRepository
)
from modules.expired_medicines.repository.expired_medicine_repository import (
    ExpiredMedicineRepository
)

from modules.expired_medicines.services.expired_medicine_item_service import (
    ExpiredMedicineItemService
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

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


expired_medicine_item_controller = Blueprint(
    "expired_medicine_items",
    __name__,
    url_prefix="/expired-medicine-items"
)


@expired_medicine_item_controller.route(
    "/",
    methods=["POST"]
)
@auth_required
@role_required([1, 2])
def create_item():

    db = SessionLocal()

    try:

        item_repo = (
            ExpiredMedicineItemRepository(db)
        )

        expired_repo = (
            ExpiredMedicineRepository(db)
        )

        medicine_repo = MedicineRepository(db)

        batch_repo = (
            MedicineBatchRepository(db)
        )

        inventory_repo = (
            InventoryRepository(db)
        )

        movement_repo = (
            StockMovementRepository(db)
        )

        service = ExpiredMedicineItemService(
            item_repo,
            expired_repo,
            medicine_repo,
            batch_repo,
            inventory_repo,
            movement_repo
        )

        item = service.create_item(
            request.get_json()
        )

        return jsonify({
            "message":
            "Expired item created successfully",
            "expired_item_id":
            item.expired_item_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@expired_medicine_item_controller.route(
    "/expired/<int:expired_id>",
    methods=["GET"]
)
@auth_required
def get_items(expired_id):

    db = SessionLocal()

    try:

        item_repo = (
            ExpiredMedicineItemRepository(db)
        )

        expired_repo = (
            ExpiredMedicineRepository(db)
        )

        medicine_repo = MedicineRepository(db)

        batch_repo = (
            MedicineBatchRepository(db)
        )

        inventory_repo = (
            InventoryRepository(db)
        )

        movement_repo = (
            StockMovementRepository(db)
        )

        service = ExpiredMedicineItemService(
            item_repo,
            expired_repo,
            medicine_repo,
            batch_repo,
            inventory_repo,
            movement_repo
        )

        items = service.get_items_by_expired(
            expired_id
        )

        return jsonify([
            {
                "expired_item_id":
                item.expired_item_id,
                "medicine_id":
                item.medicine_id,
                "batch_id":
                item.batch_id,
                "quantity":
                item.quantity,
                "reason":
                item.reason
            }
            for item in items
        ])

    finally:
        db.close()