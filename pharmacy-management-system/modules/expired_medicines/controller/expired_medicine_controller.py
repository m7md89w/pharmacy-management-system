from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.expired_medicines.repository.expired_medicine_repository import (
    ExpiredMedicineRepository
)
from modules.expired_medicines.services.expired_medicine_service import (
    ExpiredMedicineService
)

from modules.users.repository.user_repository import (
    UserRepository
)

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required


expired_medicine_controller = Blueprint(
    "expired_medicines",
    __name__,
    url_prefix="/expired-medicines"
)


@expired_medicine_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_expired():

    db = SessionLocal()

    try:

        expired_repo = ExpiredMedicineRepository(db)
        user_repo = UserRepository(db)

        service = ExpiredMedicineService(
            expired_repo,
            user_repo
        )

        data = request.get_json()

        data["user_id"] = request.user["user_id"]

        expired = service.create_expired(
            data
        )

        return jsonify({
            "message":
            "Expired record created successfully",
            "expired_id":
            expired.expired_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@expired_medicine_controller.route("/", methods=["GET"])
@auth_required
def get_expired():

    db = SessionLocal()

    try:

        expired_repo = ExpiredMedicineRepository(db)
        user_repo = UserRepository(db)

        service = ExpiredMedicineService(
            expired_repo,
            user_repo
        )

        records = service.get_all_expired()

        return jsonify([
            {
                "expired_id":
                record.expired_id,
                "user_id":
                record.user_id,
                "notes":
                record.notes
            }
            for record in records
        ])

    finally:
        db.close()


@expired_medicine_controller.route(
    "/<int:expired_id>",
    methods=["GET"]
)
@auth_required
def get_expired_by_id(expired_id):

    db = SessionLocal()

    try:

        expired_repo = ExpiredMedicineRepository(db)
        user_repo = UserRepository(db)

        service = ExpiredMedicineService(
            expired_repo,
            user_repo
        )

        record = service.get_expired(
            expired_id
        )

        return jsonify({
            "expired_id":
            record.expired_id,
            "user_id":
            record.user_id,
            "notes":
            record.notes
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()