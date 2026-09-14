from database.session import SessionLocal
from flask import Blueprint, jsonify, request
from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository,
)
from modules.medicines.repository.medicine_repository import MedicineRepository
from modules.medicines.services.medicine_batch_service import MedicineBatchService
from modules.suppliers.repository.supplier_repository import SupplierRepository

medicine_batch_controller = Blueprint(
    "medicine_batches",
    __name__,
    url_prefix="/batches"
)


# ==================================================
# CREATE
# ==================================================
@medicine_batch_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_batch():
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        medicine_repo = MedicineRepository(db)
        supplier_repo = SupplierRepository(db)

        service = MedicineBatchService(
            batch_repo,
            medicine_repo,
            supplier_repo
        )

        data = request.get_json() or {}

        if "supplier_id" not in data or data["supplier_id"] is None:
            data["supplier_id"] = 1

        batch = service.create_batch(data)

        return jsonify({
            "message": "Batch created successfully",
            "batch_id": batch.batch_id,
            "medicine_id": batch.medicine_id,
            "supplier_id": batch.supplier_id
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:  # noqa: BLE001
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

    finally:
        db.close()


# ==================================================
# GET ALL
# ==================================================
@medicine_batch_controller.route("/", methods=["GET"])
@auth_required
def get_batches():
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        medicine_repo = MedicineRepository(db)
        supplier_repo = SupplierRepository(db)

        service = MedicineBatchService(
            batch_repo,
            medicine_repo,
            supplier_repo
        )

        batches = service.get_all_batches()

        return jsonify([
            {
                "batch_id": batch.batch_id,
                "medicine_id": batch.medicine_id,
                "supplier_id": batch.supplier_id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "purchase_price": float(batch.purchase_price),
                "selling_price": float(batch.selling_price),
                "manufacture_date": str(batch.manufacture_date) if batch.manufacture_date else None,
                "expiry_date": str(batch.expiry_date)
            }
            for batch in batches
        ])

    finally:
        db.close()


# ==================================================
# GET BY ID
# ==================================================
@medicine_batch_controller.route("/<int:batch_id>", methods=["GET"])
@auth_required
def get_batch(batch_id):
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        medicine_repo = MedicineRepository(db)
        supplier_repo = SupplierRepository(db)

        service = MedicineBatchService(
            batch_repo,
            medicine_repo,
            supplier_repo
        )

        batch = service.get_batch(batch_id)

        return jsonify({
            "batch_id": batch.batch_id,
            "medicine_id": batch.medicine_id,
            "supplier_id": batch.supplier_id,
            "batch_number": batch.batch_number,
            "quantity": batch.quantity,
            "purchase_price": float(batch.purchase_price),
            "selling_price": float(batch.selling_price),
            "manufacture_date": str(batch.manufacture_date) if batch.manufacture_date else None,
            "expiry_date": str(batch.expiry_date),
            "created_at": str(batch.created_at)
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    finally:
        db.close()


# ==================================================
# GET BY MEDICINE (ALL BATCHES - FOR INVENTORY DETAILS)
# ==================================================
@medicine_batch_controller.route("/medicine/<int:medicine_id>", methods=["GET"])
@auth_required
def get_batches_by_medicine(medicine_id):
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        batches = batch_repo.get_by_medicine_id(medicine_id)

        return jsonify([
            {
                "batch_id": batch.batch_id,
                "medicine_id": batch.medicine_id,
                "supplier_id": batch.supplier_id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "purchase_price": float(batch.purchase_price),
                "selling_price": float(batch.selling_price),
                "manufacture_date": str(batch.manufacture_date) if batch.manufacture_date else None,
                "expiry_date": str(batch.expiry_date)
            }
            for batch in batches
        ])

    finally:
        db.close()


# ==================================================
# UPDATE
# ==================================================
@medicine_batch_controller.route("/<int:batch_id>", methods=["PUT"])
@auth_required
@role_required([1, 2])
def update_batch(batch_id):
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        medicine_repo = MedicineRepository(db)
        supplier_repo = SupplierRepository(db)

        service = MedicineBatchService(
            batch_repo,
            medicine_repo,
            supplier_repo
        )

        batch = service.get_batch(batch_id)
        data = request.get_json()
        updated_batch = service.update_batch(batch, data)

        return jsonify({
            "message": "Batch updated successfully",
            "batch_id": updated_batch.batch_id
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    finally:
        db.close()


# ==================================================
# DELETE
# ==================================================
@medicine_batch_controller.route("/<int:batch_id>", methods=["DELETE"])
@auth_required
@role_required([1])
def delete_batch(batch_id):
    db = SessionLocal()
    try:
        batch_repo = MedicineBatchRepository(db)
        medicine_repo = MedicineRepository(db)
        supplier_repo = SupplierRepository(db)

        service = MedicineBatchService(
            batch_repo,
            medicine_repo,
            supplier_repo
        )

        batch = service.get_batch(batch_id)
        service.delete_batch(batch)

        return jsonify({"message": "Batch deleted successfully"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    finally:
        db.close()