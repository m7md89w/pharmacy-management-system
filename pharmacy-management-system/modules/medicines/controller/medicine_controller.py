from flask import Blueprint, request, jsonify

from database.session import SessionLocal
from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)
from modules.medicines.services.medicine_service import (
    MedicineService
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

medicine_controller = Blueprint(
    "medicines",
    __name__,
    url_prefix="/medicines"
)


# =========================================================
# CREATE MEDICINE
# =========================================================
@medicine_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_medicine():

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        data = request.get_json()

        medicine = service.create_medicine(data)

        return jsonify({
            "message": "Medicine created successfully",
            "id": medicine.medicine_id,
            "commercial_name": medicine.commercial_name,
            "barcode": medicine.barcode
        }), 201

    except ValueError as e:
        db.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        db.rollback()

        print("MEDICINE CREATE ERROR:")
        print(e)

        return jsonify({
            "error": "Internal Server Error"
        }), 500

    finally:
        db.close()


# =========================================================
# GET ALL MEDICINES
# =========================================================
@medicine_controller.route("/", methods=["GET"])
@auth_required
def get_medicines():

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        medicines = service.get_all_medicines()

        return jsonify([
            {
                "id": m.medicine_id,
                "scientific_name": m.scientific_name,
                "commercial_name": m.commercial_name,
                "barcode": m.barcode,
                "dosage_form": m.dosage_form,
                "selling_price": float(m.selling_price)
                if m.selling_price else 0.0
            }
            for m in medicines
        ])

    finally:
        db.close()


# =========================================================
# GET MEDICINE BY ID
# =========================================================
@medicine_controller.route(
    "/<int:medicine_id>",
    methods=["GET"]
)
@auth_required
def get_medicine(medicine_id):

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        medicine = service.get_medicine(
            medicine_id
        )

        return jsonify({
            "id": medicine.medicine_id,
            "scientific_name": medicine.scientific_name,
            "commercial_name": medicine.commercial_name,
            "barcode": medicine.barcode,
            "description": medicine.description,
            "dosage_form": medicine.dosage_form,
            "requires_prescription": medicine.requires_prescription,
            "category_id": medicine.category_id,
            "manufacturer_id": medicine.manufacturer_id,
            "selling_price": float(medicine.selling_price)
            if medicine.selling_price else 0.0
        })

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


# =========================================================
# UPDATE MEDICINE
# =========================================================
@medicine_controller.route(
    "/<int:medicine_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def update_medicine(medicine_id):

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        medicine = service.get_medicine(
            medicine_id
        )

        data = request.get_json()

        updated = service.update_medicine(
            medicine,
            data
        )

        return jsonify({
            "message": "Medicine updated successfully",
            "id": updated.medicine_id
        })

    except ValueError as e:
        db.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        db.rollback()

        print("MEDICINE UPDATE ERROR:")
        print(e)

        return jsonify({
            "error": "Internal Server Error"
        }), 500

    finally:
        db.close()


# =========================================================
# RESTORE MEDICINE
# =========================================================
@medicine_controller.route(
    "/restore/<string:barcode>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def restore_medicine(barcode):

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        medicine = service.restore_medicine(
            barcode
        )

        return jsonify({
            "message": "Medicine restored successfully",
            "id": medicine.medicine_id,
            "commercial_name": medicine.commercial_name
        })

    except ValueError as e:
        db.rollback()

        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        db.rollback()

        print("MEDICINE RESTORE ERROR:")
        print(e)

        return jsonify({
            "error": "Internal Server Error"
        }), 500

    finally:
        db.close()


# =========================================================
# DELETE MEDICINE
# =========================================================
@medicine_controller.route(
    "/<int:medicine_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_medicine(medicine_id):

    db = SessionLocal()

    try:
        repo = MedicineRepository(db)
        service = MedicineService(repo)

        medicine = service.get_medicine(
            medicine_id
        )

        service.deactivate_medicine(
            medicine
        )

        return jsonify({
            "message":
            "Medicine deactivated successfully"
        })

    except ValueError as e:
        db.rollback()

        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        db.rollback()

        print("MEDICINE DELETE ERROR:")
        print(e)

        return jsonify({
            "error":
            "Internal Server Error"
        }), 500

    finally:
        db.close()