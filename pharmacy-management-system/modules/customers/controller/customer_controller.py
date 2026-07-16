from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from modules.customers.repository.customer_repository import CustomerRepository
from modules.customers.services.customer_service import CustomerService

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required

customer_controller = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)


@customer_controller.route("/", methods=["POST"])
@auth_required
@role_required([1, 2, 3])
def create_customer():

    db = SessionLocal()

    try:

        customer_repo = CustomerRepository(db)

        service = CustomerService(
            customer_repo
        )

        data = request.get_json()

        customer = service.create_customer(
            data
        )

        return jsonify({
            "message": "Customer created successfully",
            "customer_id": customer.customer_id
        }), 201

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@customer_controller.route("/", methods=["GET"])
@auth_required
def get_customers():

    db = SessionLocal()

    try:

        customer_repo = CustomerRepository(db)

        service = CustomerService(
            customer_repo
        )

        customers = service.get_all_customers()

        return jsonify([
            {
                "customer_id": customer.customer_id,
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
                "loyalty_points": customer.loyalty_points
            }
            for customer in customers
        ])

    finally:
        db.close()


@customer_controller.route("/<int:customer_id>", methods=["GET"])
@auth_required
def get_customer(customer_id):

    db = SessionLocal()

    try:

        customer_repo = CustomerRepository(db)

        service = CustomerService(
            customer_repo
        )

        customer = service.get_customer(
            customer_id
        )

        return jsonify({
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "email": customer.email,
            "loyalty_points": customer.loyalty_points
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()


@customer_controller.route("/<int:customer_id>", methods=["PUT"])
@auth_required
@role_required([1, 2, 3])
def update_customer(customer_id):

    db = SessionLocal()

    try:

        customer_repo = CustomerRepository(db)

        service = CustomerService(
            customer_repo
        )

        customer = service.get_customer(
            customer_id
        )

        data = request.get_json()

        updated = service.update_customer(
            customer,
            data
        )

        return jsonify({
            "message": "Customer updated successfully",
            "customer_id": updated.customer_id
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        db.close()


@customer_controller.route("/<int:customer_id>", methods=["DELETE"])
@auth_required
@role_required([1])
def delete_customer(customer_id):

    db = SessionLocal()

    try:

        customer_repo = CustomerRepository(db)

        service = CustomerService(
            customer_repo
        )

        customer = service.get_customer(
            customer_id
        )

        service.delete_customer(
            customer
        )

        return jsonify({
            "message": "Customer deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404

    finally:
        db.close()