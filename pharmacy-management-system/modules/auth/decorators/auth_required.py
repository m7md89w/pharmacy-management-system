from functools import wraps

# pyrefly: ignore [missing-import]
import jwt

# pyrefly: ignore [missing-import]
from flask import request, jsonify

from modules.auth.utils.jwt_handler import JWTHandler


def auth_required(func):
    """
    Route decorator that enforces JWT authentication.

    Reads the Bearer token from the Authorization header, verifies it,
    and attaches the decoded payload to `request.user` so downstream
    handlers can access user_id, username, and role_id.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # --------------------------------------------------
        # 1. Check header presence
        # --------------------------------------------------
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header is missing."}), 401

        # --------------------------------------------------
        # 2. Extract Bearer token
        # --------------------------------------------------
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Invalid Authorization header format. Expected: Bearer <token>"
            }), 401

        token = parts[1]

        # --------------------------------------------------
        # 3. Verify token — catch only JWT-specific failures
        # --------------------------------------------------
        try:
            payload = JWTHandler.verify_token(token)
            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please log in again."}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token."}), 401

        return func(*args, **kwargs)

    return wrapper
