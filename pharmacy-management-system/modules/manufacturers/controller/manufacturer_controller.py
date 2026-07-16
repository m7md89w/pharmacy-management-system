from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.manufacturers.repository.manufacturer_repository import (
    ManufacturerRepository
)
from modules.manufacturers.services.manufacturer_service import (
    ManufacturerService
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

manufacturer_controller = Blueprint(
    "manufacturers",
    __name__,
    url_prefix="/manufacturers"
)


@manufacturer_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_manufacturer():

    db = SessionLocal()

    try:

        repo = ManufacturerRepository(db)
        service = ManufacturerService(repo)

        manufacturer = (
            service.create_manufacturer(
                request.get_json()
            )
        )

        return jsonify({
            "message":
            "Manufacturer created successfully",
            "manufacturer_id":
            manufacturer.manufacturer_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@manufacturer_controller.route("/", methods=["GET"])
@auth_required
def get_manufacturers():

    db = SessionLocal()

    try:

        repo = ManufacturerRepository(db)
        service = ManufacturerService(repo)

        manufacturers = (
            service.get_all_manufacturers()
        )

        return jsonify([
            {
                "manufacturer_id":
                m.manufacturer_id,
                "name":
                m.name,
                "contact_email":
                m.contact_email,
                "contact_phone":
                m.contact_phone,
                "address":
                m.address
            }
            for m in manufacturers
        ])

    finally:
        db.close()


@manufacturer_controller.route(
    "/<int:manufacturer_id>",
    methods=["GET"]
)
@auth_required
def get_manufacturer(
    manufacturer_id
):

    db = SessionLocal()

    try:

        repo = ManufacturerRepository(db)
        service = ManufacturerService(repo)

        manufacturer = (
            service.get_manufacturer(
                manufacturer_id
            )
        )

        return jsonify({
            "manufacturer_id":
            manufacturer.manufacturer_id,
            "name":
            manufacturer.name,
            "contact_email":
            manufacturer.contact_email,
            "contact_phone":
            manufacturer.contact_phone,
            "address":
            manufacturer.address
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@manufacturer_controller.route(
    "/<int:manufacturer_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def update_manufacturer(
    manufacturer_id
):

    db = SessionLocal()

    try:

        repo = ManufacturerRepository(db)
        service = ManufacturerService(repo)

        manufacturer = (
            service.get_manufacturer(
                manufacturer_id
            )
        )

        updated = (
            service.update_manufacturer(
                manufacturer,
                request.get_json()
            )
        )

        return jsonify({
            "message":
            "Manufacturer updated successfully",
            "manufacturer_id":
            updated.manufacturer_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@manufacturer_controller.route(
    "/<int:manufacturer_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_manufacturer(
    manufacturer_id
):

    db = SessionLocal()

    try:

        repo = ManufacturerRepository(db)
        service = ManufacturerService(repo)

        manufacturer = (
            service.get_manufacturer(
                manufacturer_id
            )
        )

        service.delete_manufacturer(
            manufacturer
        )

        return jsonify({
            "message":
            "Manufacturer deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()