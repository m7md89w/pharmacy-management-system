from flask import Blueprint
from flask import request
from flask import jsonify

from database.session import SessionLocal

from modules.users.repository.user_repository import UserRepository

from modules.auth.services.auth_service import AuthService


auth_controller = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_controller.route(
    "/login",
    methods=["POST"]
)
def login():

    db = SessionLocal()

    try:

        user_repo = UserRepository(db)

        auth_service = AuthService(
            user_repo
        )

        data = request.get_json()

        result = auth_service.login(
            username=data["username"],
            password=data["password"]
        )

        return jsonify(result)

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 401

    finally:
        db.close()