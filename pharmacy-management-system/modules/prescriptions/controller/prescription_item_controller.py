from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.prescriptions.repository.prescription_item_repository import (
    PrescriptionItemRepository
)
from modules.prescriptions.repository.prescription_repository import (
    PrescriptionRepository
)
from modules.prescriptions.services.prescription_item_service import (
    PrescriptionItemService
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

prescription_item_controller = Blueprint(
    "prescription_items",
    __name__,
    url_prefix="/prescription-items"
)


@prescription_item_controller.route(
    "/",
    methods=["POST"]
)
@auth_required
@role_required([1, 2, 3])
def create_item():

    db = SessionLocal()

    try:

        item_repo = (
            PrescriptionItemRepository(db)
        )
        prescription_repo = (
            PrescriptionRepository(db)
        )
        medicine_repo = (
            MedicineRepository(db)
        )

        service = PrescriptionItemService(
            item_repo,
            prescription_repo,
            medicine_repo
        )

        item = service.create_item(
            request.get_json()
        )

        return jsonify({
            "message":
            "Prescription item created successfully",
            "prescription_item_id":
            item.prescription_item_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@prescription_item_controller.route(
    "/prescription/<int:prescription_id>",
    methods=["GET"]
)
@auth_required
def get_items(
    prescription_id
):

    db = SessionLocal()

    try:

        item_repo = (
            PrescriptionItemRepository(db)
        )
        prescription_repo = (
            PrescriptionRepository(db)
        )
        medicine_repo = (
            MedicineRepository(db)
        )

        service = PrescriptionItemService(
            item_repo,
            prescription_repo,
            medicine_repo
        )

        items = (
            service.get_items_by_prescription(
                prescription_id
            )
        )

        return jsonify([
            {
                "prescription_item_id":
                item.prescription_item_id,
                "medicine_id":
                item.medicine_id,
                "dosage":
                item.dosage,
                "duration":
                item.duration,
                "frequency":
                item.frequency,
                "notes":
                item.notes
            }
            for item in items
        ])

    finally:
        db.close()