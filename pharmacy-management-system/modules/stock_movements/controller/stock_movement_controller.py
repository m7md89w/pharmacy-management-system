from flask import Blueprint, jsonify, request
from database.session import SessionLocal
from modules.auth.decorators.auth_required import auth_required
from modules.auth.decorators.role_required import role_required
from modules.medicines.repository.medicine_batch_repository import (
    MedicineBatchRepository,
)
from modules.stock_movements.repository.stock_movement_repository import (
    StockMovementRepository,
)
from modules.stock_movements.services.stock_movement_service import (
    StockMovementService,
)

# استيراد النماذج بأمان
from models.all_models import MedicineBatch, PurchaseOrder, SalesInvoice

stock_movement_controller = Blueprint(
    "stock_movements", __name__, url_prefix="/stock-movements"
)


@stock_movement_controller.route("/", methods=["POST"])
@auth_required
@role_required([1])
def create_movement():
  db = SessionLocal()
  try:
    movement_repo = StockMovementRepository(db)
    batch_repo = MedicineBatchRepository(db)
    service = StockMovementService(movement_repo, batch_repo)

    data = request.get_json()
    data["created_by"] = request.user["user_id"]

    movement = service.create_movement(data)

    return (
        jsonify({
            "message": "Stock movement created successfully",
            "movement_id": movement.movement_id,
        }),
        201,
    )
  except ValueError as e:
    return jsonify({"error": str(e)}), 400
  finally:
    db.close()


@stock_movement_controller.route("/", methods=["GET"])
@auth_required
def get_movements():
  db = SessionLocal()
  try:
    movement_repo = StockMovementRepository(db)
    batch_repo = MedicineBatchRepository(db)
    service = StockMovementService(movement_repo, batch_repo)

    movements = service.get_all_movements()

    result = []
    for movement in movements:
      # جلب رقم الباتش الفعلي (batch_number) إن وجد
      batch_number = None
      if getattr(movement, "batch_id", None):
        batch = db.query(MedicineBatch).filter_by(batch_id=movement.batch_id).first()
        if batch:
          batch_number = getattr(batch, "batch_number", str(batch.batch_id))

      result.append({
          "movement_id": getattr(movement, "movement_id", None),
          "batch_id": getattr(movement, "batch_id", None),
          "batch_number": batch_number,
          "movement_type": getattr(movement, "movement_type", "N/A"),
          "quantity_change": getattr(movement, "quantity_change", 0),
          "reference_type": getattr(movement, "reference_type", "N/A"),
          "reference_id": getattr(movement, "reference_id", None),
          "created_by": getattr(movement, "created_by", None),
          "created_at": (
              str(movement.created_at)
              if getattr(movement, "created_at", None)
              else None
          ),
      })
    return jsonify(result)
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()


@stock_movement_controller.route("/<int:movement_id>", methods=["GET"])
@auth_required
def get_movement(movement_id):
  db = SessionLocal()
  try:
    movement_repo = StockMovementRepository(db)
    batch_repo = MedicineBatchRepository(db)
    service = StockMovementService(movement_repo, batch_repo)

    movement = service.get_movement(movement_id)

    # جلب رقم الباتش الفعلي (batch_number)
    batch_number = None
    if getattr(movement, "batch_id", None):
      batch = db.query(MedicineBatch).filter_by(batch_id=movement.batch_id).first()
      if batch:
        batch_number = getattr(batch, "batch_number", str(batch.batch_id))

    reference_details = {}
    ref_type = getattr(movement, "reference_type", None)
    ref_id = getattr(movement, "reference_id", None)

    try:
      if ref_id and ref_type:
        if ref_type in ["SALE", "SALES_RETURN"]:
          invoice = (
              db.query(SalesInvoice).filter_by(invoice_id=ref_id).first()
          )
          if invoice:
            reference_details = {
                "type": "Sales Invoice",
                "invoice_id": getattr(invoice, "invoice_id", ref_id),
                "status": getattr(invoice, "status", "N/A"),
                "customer_id": getattr(invoice, "customer_id", "N/A"),
            }
        elif ref_type in ["PURCHASE", "PURCHASE_RETURN"]:
          purchase = (
              db.query(PurchaseOrder).filter_by(purchase_id=ref_id).first()
          )
          if purchase:
            reference_details = {
                "type": "Purchase Order",
                "purchase_id": getattr(purchase, "purchase_id", ref_id),
                "status": getattr(purchase, "status", "N/A"),
                "supplier_id": getattr(purchase, "supplier_id", "N/A"),
            }
    except Exception:
      pass

    return jsonify({
        "movement_id": getattr(movement, "movement_id", movement_id),
        "batch_id": getattr(movement, "batch_id", None),
        "batch_number": batch_number,
        "movement_type": getattr(movement, "movement_type", "N/A"),
        "quantity_change": getattr(movement, "quantity_change", 0),
        "reference_type": ref_type,
        "reference_id": ref_id,
        "notes": getattr(movement, "notes", None),
        "created_by": getattr(movement, "created_by", None),
        "created_at": (
            str(movement.created_at)
            if getattr(movement, "created_at", None)
            else None
        ),
        "reference_details": reference_details,
    })

  except ValueError as e:
    return jsonify({"error": str(e)}), 404
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()


@stock_movement_controller.route("/batch/<int:batch_id>", methods=["GET"])
@auth_required
def get_batch_movements(batch_id):
  db = SessionLocal()
  try:
    movement_repo = StockMovementRepository(db)
    batch_repo = MedicineBatchRepository(db)
    service = StockMovementService(movement_repo, batch_repo)

    movements = service.get_batch_movements(batch_id)

    return jsonify([
        {
            "movement_id": getattr(m, "movement_id", None),
            "movement_type": getattr(m, "movement_type", "N/A"),
            "quantity_change": getattr(m, "quantity_change", 0),
            "reference_type": getattr(m, "reference_type", "N/A"),
            "created_by": getattr(m, "created_by", None),
            "created_at": (
                str(m.created_at) if getattr(m, "created_at", None) else None
            ),
        }
        for m in movements
    ])
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()


@stock_movement_controller.route("/<int:movement_id>", methods=["DELETE"])
@auth_required
@role_required([1])
def delete_movement(movement_id):
  db = SessionLocal()
  try:
    movement_repo = StockMovementRepository(db)
    batch_repo = MedicineBatchRepository(db)
    service = StockMovementService(movement_repo, batch_repo)

    movement = service.get_movement(movement_id)
    service.delete_movement(movement)

    return jsonify({"message": "Stock movement deleted successfully"})
  except ValueError as e:
    return jsonify({"error": str(e)}), 404
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()