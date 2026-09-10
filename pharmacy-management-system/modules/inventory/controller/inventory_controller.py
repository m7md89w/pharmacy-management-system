from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.inventory.repository.inventory_repository import InventoryRepository
from modules.inventory.services.inventory_service import InventoryService

from modules.medicines.repository.medicine_repository import MedicineRepository

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


inventory_controller = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)


@inventory_controller.route("/", methods=["POST"])
@auth_required
@role_required([1])
def create_inventory():

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        inventory = service.create_inventory(
            request.get_json()
        )

        return jsonify({
            "message": "Inventory created successfully",
            "inventory_id": inventory.inventory_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@inventory_controller.route("/", methods=["GET"])
@auth_required
def get_inventory():

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        detailed_inventory = service.get_detailed_inventory()

        return jsonify(detailed_inventory), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        db.close()


@inventory_controller.route("/<int:inventory_id>", methods=["GET"])
@auth_required
def get_inventory_by_id(inventory_id):

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        inventory = service.get_inventory(
            inventory_id
        )

        return jsonify({
            "inventory_id": inventory.inventory_id,
            "medicine_id": inventory.medicine_id,
            "quantity": inventory.quantity,
            "min_stock_level": inventory.min_stock_level,
            "location": inventory.location
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@inventory_controller.route("/medicine/<int:medicine_id>", methods=["GET"])
@auth_required
def get_inventory_by_medicine(medicine_id):

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        inventory = service.get_inventory_by_medicine(
            medicine_id
        )

        return jsonify({
            "inventory_id": inventory.inventory_id,
            "medicine_id": inventory.medicine_id,
            "quantity": inventory.quantity,
            "min_stock_level": inventory.min_stock_level,
            "location": inventory.location
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@inventory_controller.route("/<int:inventory_id>", methods=["PUT"])
@auth_required
@role_required([1])
def update_inventory(inventory_id):

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        inventory = service.get_inventory(
            inventory_id
        )

        updated = service.update_inventory(
            inventory,
            request.get_json()
        )

        return jsonify({
            "message": "Inventory updated successfully",
            "inventory_id": updated.inventory_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@inventory_controller.route("/<int:inventory_id>", methods=["DELETE"])
@auth_required
@role_required([1])
def delete_inventory(inventory_id):

    db = SessionLocal()

    try:

        inventory_repo = InventoryRepository(db)
        medicine_repo = MedicineRepository(db)

        service = InventoryService(
            inventory_repo,
            medicine_repo
        )

        inventory = service.get_inventory(
            inventory_id
        )

        service.delete_inventory(
            inventory
        )

        return jsonify({
            "message": "Inventory deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()