from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.users.repository.user_repository import UserRepository
from modules.users.services.user_service import UserService

from modules.roles.repository.role_repository import RoleRepository
from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required

user_controller = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@user_controller.route("/", methods=["POST"])
@auth_required
@role_required([1])
def create_user():

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        service = UserService(
            user_repo,
            role_repo
        )

        data = request.get_json()

        user = service.create_user(data)

        return jsonify({
            "message": "User created successfully",
            "user_id": user.user_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@user_controller.route("/", methods=["GET"])
@auth_required
@role_required([1])
def get_users():

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        service = UserService(
            user_repo,
            role_repo
        )

        users = service.get_all_users()

        return jsonify([
            {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "role_id": user.role_id,
                "is_active": user.is_active
            }
            for user in users
        ])

    finally:
        db.close()


@user_controller.route("/<int:user_id>", methods=["GET"])
@auth_required
@role_required([1])
def get_user(user_id):

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        service = UserService(
            user_repo,
            role_repo
        )

        user = service.get_user(user_id)

        return jsonify({
            "user_id": user.user_id,
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "is_active": user.is_active
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()



@user_controller.route("/<int:user_id>", methods=["PUT"])
@auth_required
@role_required([1])
def update_user(user_id):

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        service = UserService(
            user_repo,
            role_repo
        )

        user = service.get_user(user_id)

        data = request.get_json()

        updated = service.update_user(
            user,
            data
        )

        return jsonify({
            "message": "User updated successfully",
            "user_id": updated.user_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@user_controller.route(
    "/<int:user_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def deactivate_user(user_id):

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        service = UserService(
            user_repo,
            role_repo
        )

        user = service.get_user(
            user_id
        )

        service.deactivate_user(
            user
        )

        return jsonify({
            "message": "User deactivated successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()