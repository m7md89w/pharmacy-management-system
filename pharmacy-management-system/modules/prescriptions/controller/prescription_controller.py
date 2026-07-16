from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.prescriptions.repository.prescription_repository import (
    PrescriptionRepository
)
from modules.prescriptions.services.prescription_service import (
    PrescriptionService
)

from modules.customers.repository.customer_repository import (
    CustomerRepository
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

prescription_controller = Blueprint(
    "prescriptions",
    __name__,
    url_prefix="/prescriptions"
)


@prescription_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_prescription():

    db = SessionLocal()

    try:

        prescription_repo = PrescriptionRepository(db)
        customer_repo = CustomerRepository(db)

        service = PrescriptionService(
            prescription_repo,
            customer_repo
        )

        prescription = service.create_prescription(
            request.get_json()
        )

        return jsonify({
            "message":
            "Prescription created successfully",
            "prescription_id":
            prescription.prescription_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@prescription_controller.route("/", methods=["GET"])
@auth_required
def get_prescriptions():

    db = SessionLocal()

    try:

        prescription_repo = PrescriptionRepository(db)
        customer_repo = CustomerRepository(db)

        service = PrescriptionService(
            prescription_repo,
            customer_repo
        )

        prescriptions = (
            service.get_all_prescriptions()
        )

        return jsonify([
            {
                "prescription_id":
                p.prescription_id,
                "customer_id":
                p.customer_id,
                "doctor_name":
                p.doctor_name,
                "prescription_image":
                p.prescription_image,
                "issue_date":
                str(p.issue_date)
                if p.issue_date else None,
                "notes":
                p.notes
            }
            for p in prescriptions
        ])

    finally:
        db.close()


@prescription_controller.route(
    "/<int:prescription_id>",
    methods=["GET"]
)
@auth_required
def get_prescription(
    prescription_id
):

    db = SessionLocal()

    try:

        prescription_repo = PrescriptionRepository(db)
        customer_repo = CustomerRepository(db)

        service = PrescriptionService(
            prescription_repo,
            customer_repo
        )

        p = service.get_prescription(
            prescription_id
        )

        return jsonify({
            "prescription_id":
            p.prescription_id,
            "customer_id":
            p.customer_id,
            "doctor_name":
            p.doctor_name,
            "prescription_image":
            p.prescription_image,
            "issue_date":
            str(p.issue_date)
            if p.issue_date else None,
            "notes":
            p.notes
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@prescription_controller.route(
    "/<int:prescription_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2, 3])
def update_prescription(
    prescription_id
):

    db = SessionLocal()

    try:

        prescription_repo = PrescriptionRepository(db)
        customer_repo = CustomerRepository(db)

        service = PrescriptionService(
            prescription_repo,
            customer_repo
        )

        prescription = (
            service.get_prescription(
                prescription_id
            )
        )

        updated = (
            service.update_prescription(
                prescription,
                request.get_json()
            )
        )

        return jsonify({
            "message":
            "Prescription updated successfully",
            "prescription_id":
            updated.prescription_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@prescription_controller.route(
    "/<int:prescription_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1, 2])
def delete_prescription(
    prescription_id
):

    db = SessionLocal()

    try:

        prescription_repo = PrescriptionRepository(db)
        customer_repo = CustomerRepository(db)

        service = PrescriptionService(
            prescription_repo,
            customer_repo
        )

        prescription = (
            service.get_prescription(
                prescription_id
            )
        )

        service.delete_prescription(
            prescription
        )

        return jsonify({
            "message":
            "Prescription deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()