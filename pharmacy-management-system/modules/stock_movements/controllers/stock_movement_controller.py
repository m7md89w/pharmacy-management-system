from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.stock_movements.repository.stock_movement_repository import StockMovementRepository
from modules.stock_movements.services.stock_movement_service import StockMovementService

from modules.medicines.repository.medicine_batch_repository import MedicineBatchRepository

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required

stock_movement_controller = Blueprint(
    "stock_movements",
    __name__,
    url_prefix="/stock-movements"
)


@stock_movement_controller.route("/", methods=["POST"])
@auth_required
@role_required([1])
def create_movement():

    db = SessionLocal()

    try:

        movement_repo = StockMovementRepository(db)
        batch_repo = MedicineBatchRepository(db)

        service = StockMovementService(
            movement_repo,
            batch_repo
        )

        data = request.get_json()
        data["created_by"] = request.user["user_id"]

        movement = service.create_movement(
            data
        )

        return jsonify({
            "message": "Stock movement created successfully",
            "movement_id": movement.movement_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@stock_movement_controller.route("/", methods=["GET"])
@auth_required
def get_movements():

    db = SessionLocal()

    try:

        movement_repo = StockMovementRepository(db)
        batch_repo = MedicineBatchRepository(db)

        service = StockMovementService(
            movement_repo,
            batch_repo
        )

        movements = service.get_all_movements()

        return jsonify([
            {
                "movement_id": movement.movement_id,
                "batch_id": movement.batch_id,
                "movement_type": movement.movement_type,
                "quantity_change": movement.quantity_change,
                "reference_type": movement.reference_type,
                "reference_id": movement.reference_id
            }
            for movement in movements
        ])

    finally:
        db.close()


@stock_movement_controller.route("/<int:movement_id>", methods=["GET"])
@auth_required
def get_movement(movement_id):

    db = SessionLocal()

    try:

        movement_repo = StockMovementRepository(db)
        batch_repo = MedicineBatchRepository(db)

        service = StockMovementService(
            movement_repo,
            batch_repo
        )

        movement = service.get_movement(
            movement_id
        )

        return jsonify({
            "movement_id": movement.movement_id,
            "batch_id": movement.batch_id,
            "movement_type": movement.movement_type,
            "quantity_change": movement.quantity_change,
            "reference_type": movement.reference_type,
            "reference_id": movement.reference_id,
            "notes": movement.notes
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@stock_movement_controller.route(
    "/batch/<int:batch_id>",
    methods=["GET"]
)
@auth_required
def get_batch_movements(batch_id):

    db = SessionLocal()

    try:

        movement_repo = StockMovementRepository(db)
        batch_repo = MedicineBatchRepository(db)

        service = StockMovementService(
            movement_repo,
            batch_repo
        )

        movements = service.get_batch_movements(
            batch_id
        )

        return jsonify([
            {
                "movement_id": movement.movement_id,
                "movement_type": movement.movement_type,
                "quantity_change": movement.quantity_change,
                "reference_type": movement.reference_type
            }
            for movement in movements
        ])

    finally:
        db.close()


@stock_movement_controller.route(
    "/<int:movement_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_movement(movement_id):

    db = SessionLocal()

    try:

        movement_repo = StockMovementRepository(db)
        batch_repo = MedicineBatchRepository(db)

        service = StockMovementService(
            movement_repo,
            batch_repo
        )

        movement = service.get_movement(
            movement_id
        )

        service.delete_movement(
            movement
        )

        return jsonify({
            "message": "Stock movement deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()