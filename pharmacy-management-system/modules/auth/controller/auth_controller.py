# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify

from database.session import SessionLocal
from modules.users.repository.user_repository import UserRepository
from modules.auth.services.auth_service import AuthService


auth_controller = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


@auth_controller.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and returns a JWT access token.

    Request body (JSON):
        {
            "username": "string",
            "password": "string"
        }

    Returns:
        200: { "access_token": "...", "user_id": ..., "username": "...", "role_id": ... }
        400: { "error": "..." }  — missing or invalid input
        401: { "error": "..." }  — wrong credentials or inactive account
    """
    # --------------------------------------------------
    # 1. Parse & validate input
    # --------------------------------------------------
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username:
        return jsonify({"error": "Field 'username' is required."}), 400

    if not password:
        return jsonify({"error": "Field 'password' is required."}), 400

    # --------------------------------------------------
    # 2. Authenticate
    # --------------------------------------------------
    db = SessionLocal()

    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)

        result = auth_service.login(
            username=username,
            password=password,
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    finally:
        db.close()
