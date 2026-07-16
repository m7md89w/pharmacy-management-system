from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.roles.repository.role_repository import RoleRepository
from modules.roles.services.role_service import RoleService

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required

role_controller = Blueprint(
    "roles",
    __name__,
    url_prefix="/roles"
)


@role_controller.route("/", methods=["POST"])
@auth_required
@role_required([1])
def create_role():

    db = SessionLocal()

    try:

        repo = RoleRepository(db)
        service = RoleService(repo)

        data = request.get_json()

        role = service.create_role(data)

        return jsonify({
            "message": "Role created successfully",
            "role_id": role.role_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@role_controller.route("/", methods=["GET"])
@auth_required
@role_required([1])
def get_roles():

    db = SessionLocal()

    try:

        repo = RoleRepository(db)
        service = RoleService(repo)

        roles = service.get_all_roles()

        return jsonify([
            {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description
            }
            for role in roles
        ])

    finally:
        db.close()


@role_controller.route("/<int:role_id>", methods=["GET"])
@auth_required
@role_required([1])
def get_role(role_id):

    db = SessionLocal()

    try:

        repo = RoleRepository(db)
        service = RoleService(repo)

        role = service.get_role(role_id)

        return jsonify({
            "role_id": role.role_id,
            "role_name": role.role_name,
            "description": role.description
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@role_controller.route("/<int:role_id>", methods=["PUT"])
@auth_required
@role_required([1])
def update_role(role_id):

    db = SessionLocal()

    try:

        repo = RoleRepository(db)
        service = RoleService(repo)

        role = service.get_role(role_id)

        data = request.get_json()

        updated = service.update_role(
            role,
            data
        )

        return jsonify({
            "message": "Role updated successfully",
            "role_id": updated.role_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@role_controller.route("/<int:role_id>", methods=["DELETE"])
@auth_required
@role_required([1])
def delete_role(role_id):

    db = SessionLocal()

    try:

        repo = RoleRepository(db)
        service = RoleService(repo)

        role = service.get_role(role_id)

        service.delete_role(role)

        return jsonify({
            "message": "Role deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()