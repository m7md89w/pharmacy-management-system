from functools import wraps

from flask import request
from flask import jsonify


def role_required(
    allowed_roles: list[int]
):

    def decorator(func):

        @wraps(func)
        def wrapper(
            *args,
            **kwargs
        ):

            user = getattr(
                request,
                "user",
                None
            )

            if not user:

                return jsonify({
                    "error": "Authentication required"
                }), 401

            role_id = user.get(
                "role_id"
            )

            if role_id not in allowed_roles:

                return jsonify({
                    "error": "Access denied"
                }), 403

            return func(
                *args,
                **kwargs
            )

        return wrapper

    return decorator