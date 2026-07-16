from functools import wraps

from flask import request
from flask import jsonify

from modules.auth.utils.jwt_handler import JWTHandler


def auth_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get(
            "Authorization"
        )

        if not auth_header:

            return jsonify({
                "error": "Token is missing"
            }), 401

        try:

            token = auth_header.split(
                " "
            )[1]

        except IndexError:

            return jsonify({
                "error": "Invalid token format"
            }), 401

        try:

            payload = JWTHandler.verify_token(
                token
            )

            request.user = payload

        except Exception:

            return jsonify({
                "error": "Invalid or expired token"
            }), 401

        return func(
            *args,
            **kwargs
        )

    return wrapper