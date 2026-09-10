from flask import Blueprint, request, jsonify

from database.session import SessionLocal
from modules.suppliers.repository.supplier_repository import SupplierRepository
from modules.suppliers.services.supplier_service import SupplierService

from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required

supplier_controller = Blueprint(
    'suppliers',
    __name__,
    url_prefix='/suppliers'
)


@supplier_controller.route('/', methods=['POST'])
@auth_required
@role_required([1, 2])
def create_supplier():
    db = SessionLocal()

    try:
        repo = SupplierRepository(db)
        service = SupplierService(repo)

        data = request.get_json()

        supplier = service.create_supplier(data)

        return jsonify({
            "message": "Supplier created successfully",
            "id": supplier.supplier_id,
            "name": supplier.name
        }), 201

    finally:
        db.close()




@supplier_controller.route('/', methods=['GET'])
@auth_required
def get_suppliers():
    db = SessionLocal()

    try:
        repo = SupplierRepository(db)
        service = SupplierService(repo)

        suppliers = service.get_all_suppliers()

        return jsonify([
            {
                "id": s.supplier_id,
                "name": s.name,
                "phone": s.phone,
                "email": s.email
            }
            for s in suppliers
        ])

    finally:
        db.close()


@supplier_controller.route('/<int:supplier_id>', methods=['GET'])
@auth_required
def get_supplier(supplier_id):
    db = SessionLocal()

    try:
        repo = SupplierRepository(db)
        service = SupplierService(repo)

        supplier = service.get_supplier(supplier_id)

        return jsonify({
            "id": supplier.supplier_id,
            "name": supplier.name,
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address
        })

    finally:
        db.close()


@supplier_controller.route('/<int:supplier_id>', methods=['PUT'])
@auth_required
@role_required([1, 2])
def update_supplier(supplier_id):
    db = SessionLocal()

    try:
        repo = SupplierRepository(db)
        service = SupplierService(repo)

        supplier = service.get_supplier(supplier_id)
        data = request.get_json()

        updated = service.update_supplier(supplier, data)

        return jsonify({
            "message": "Supplier updated successfully",
            "id": updated.supplier_id
        })

    finally:
        db.close()


@supplier_controller.route('/<int:supplier_id>', methods=['DELETE'])
@auth_required
@role_required([1, 2])
def delete_supplier(supplier_id):
    db = SessionLocal()

    try:
        repo = SupplierRepository(db)
        service = SupplierService(repo)

        supplier = service.get_supplier(supplier_id)
        service.deactivate_supplier(supplier)

        return jsonify({
            "message": "Supplier deactivated successfully"
        })

    finally:
        db.close()


