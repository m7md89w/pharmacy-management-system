from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.categories.repository.category_repository import (
    CategoryRepository
)
from modules.categories.services.category_service import (
    CategoryService
)

from modules.auth.decorators.auth_required import (
    auth_required
)
from modules.auth.decorators.role_required import (
    role_required
)

category_controller = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories"
)


@category_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2])
def create_category():

    db = SessionLocal()

    try:

        repo = CategoryRepository(db)
        service = CategoryService(repo)

        category = service.create_category(
            request.get_json()
        )

        return jsonify({
            "message": "Category created successfully",
            "category_id": category.category_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@category_controller.route("/", methods=["GET"])
@auth_required
def get_categories():

    db = SessionLocal()

    try:

        repo = CategoryRepository(db)
        service = CategoryService(repo)

        categories = (
            service.get_all_categories()
        )

        return jsonify([
            {
                "category_id":
                category.category_id,
                "category_name":
                category.category_name,
                "description":
                category.description
            }
            for category in categories
        ])

    finally:
        db.close()


@category_controller.route(
    "/<int:category_id>",
    methods=["GET"]
)
@auth_required
def get_category(category_id):

    db = SessionLocal()

    try:

        repo = CategoryRepository(db)
        service = CategoryService(repo)

        category = service.get_category(
            category_id
        )

        return jsonify({
            "category_id":
            category.category_id,
            "category_name":
            category.category_name,
            "description":
            category.description
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@category_controller.route(
    "/<int:category_id>",
    methods=["PUT"]
)
@auth_required
@role_required([1, 2])
def update_category(category_id):

    db = SessionLocal()

    try:

        repo = CategoryRepository(db)
        service = CategoryService(repo)

        category = service.get_category(
            category_id
        )

        updated = (
            service.update_category(
                category,
                request.get_json()
            )
        )

        return jsonify({
            "message":
            "Category updated successfully",
            "category_id":
            updated.category_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@category_controller.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
@auth_required
@role_required([1])
def delete_category(category_id):

    db = SessionLocal()

    try:

        repo = CategoryRepository(db)
        service = CategoryService(repo)

        category = service.get_category(
            category_id
        )

        service.delete_category(
            category
        )

        return jsonify({
            "message":
            "Category deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()