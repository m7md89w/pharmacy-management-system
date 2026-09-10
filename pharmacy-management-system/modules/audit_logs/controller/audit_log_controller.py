from flask import Blueprint, jsonify, request
from database.session import SessionLocal
from modules.auth.decorators.auth_required import auth_required
from models.all_models import AuditLog, User, PurchaseOrder, SalesInvoice, SalesReturn
import re

audit_log_controller = Blueprint(
    "audit_logs", __name__, url_prefix="/audit-logs"
)


@audit_log_controller.route("/", methods=["GET"])
@auth_required
def get_audit_logs():
  db = SessionLocal()
  try:
    results = (
        db.query(AuditLog, User)
        .outerjoin(User, AuditLog.user_id == User.user_id)
        .all()
    )

    logs_list = []
    for log, user in results:
      log_id = getattr(
          log,
          "audit_id",
          getattr(log, "id", getattr(log, "log_id", None)),
      )
      
      username = "System"
      if user:
        username = getattr(
            user,
            "username",
            getattr(user, "name", f"User #{log.user_id}"),
        )

      action = getattr(log, "action", getattr(log, "event", "N/A"))
      details = getattr(log, "details", getattr(log, "description", "N/A"))
      timestamp_val = getattr(
          log, "timestamp", getattr(log, "created_at", None)
      )
      timestamp_str = str(timestamp_val) if timestamp_val else "N/A"

      logs_list.append({
          "audit_id": log_id,
          "user_id": getattr(log, "user_id", None),
          "operator": username,
          "action": action,
          "details": details,
          "timestamp": timestamp_str,
      })

    logs_list = sorted(
        logs_list,
        key=lambda x: x["audit_id"] if x["audit_id"] is not None else 0,
        reverse=True,
    )
    return jsonify(logs_list)

  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()


@audit_log_controller.route("/<int:audit_id>", methods=["GET"])
@auth_required
def get_audit_log_detail(audit_id):
  db = SessionLocal()
  try:
    log_result = None
    for pk_col in ["audit_id", "id", "log_id"]:
      if hasattr(AuditLog, pk_col):
        log_result = (
            db.query(AuditLog, User)
            .outerjoin(User, AuditLog.user_id == User.user_id)
            .filter(getattr(AuditLog, pk_col) == audit_id)
            .first()
        )
        if log_result:
          break

    if not log_result:
      return jsonify({"error": "Audit log not found"}), 404

    log, user = log_result
    log_id = getattr(
        log,
        "audit_id",
        getattr(log, "id", getattr(log, "log_id", audit_id)),
    )

    username = "System"
    if user:
      username = getattr(
          user,
          "username",
          getattr(user, "name", f"User #{log.user_id}"),
      )

    action = getattr(log, "action", getattr(log, "event", "N/A"))
    details_text = getattr(log, "details", getattr(log, "description", ""))
    timestamp_val = getattr(log, "timestamp", getattr(log, "created_at", None))
    timestamp_str = str(timestamp_val) if timestamp_val else "N/A"

    linked_transaction = {}
    try:
      action_upper = action.upper()
      details_upper = details_text.upper()

      # البحث عن معرف رقمي تقليدي (مثل #1)
      match_id = re.search(r"#(\d+)", details_text)
      ref_id = int(match_id.group(1)) if match_id else None

      # البحث عن معرف نصي للفاتورة (مثل INV-1789058815-8369 أو ما شابه)
      invoice_str_match = re.search(r"(INV-[A-Z0-9\-]+)", details_text, re.IGNORECASE)
      invoice_code = invoice_str_match.group(1) if invoice_str_match else None

      if "PURCHASE" in action_upper or "PURCHASE" in details_upper:
        if ref_id:
          po = db.query(PurchaseOrder).filter_by(purchase_id=ref_id).first()
          if po:
            linked_transaction = {
                "type": "Purchase Order",
                "purchase_id": po.purchase_id,
                "status": getattr(po, "status", "N/A"),
                "supplier_id": getattr(po, "supplier_id", "N/A"),
            }
      elif "SALE" in action_upper or "INVOICE" in details_upper or "SELL" in details_upper or "DELETE" in action_upper:
        inv = None
        # محاولة البحث بالكود النصي للفاتورة أولاً
        if invoice_code:
          inv = db.query(SalesInvoice).filter_by(invoice_id=invoice_code).first()
          if not inv:
            inv = db.query(SalesInvoice).filter(SalesInvoice.invoice_id.like(f"%{invoice_code}%")).first()
        
        # إن لم يتم العثور، نجرب الرقم العادي إن وجد
        if not inv and ref_id:
          inv = db.query(SalesInvoice).filter_by(invoice_id=ref_id).first()

        if inv:
          linked_transaction = {
              "type": "Sales Invoice",
              "invoice_id": inv.invoice_id,
              "status": getattr(inv, "status", "N/A"),
              "customer_id": getattr(inv, "customer_id", "N/A"),
          }
        elif invoice_code:
          # حتى لو لم تُقَدّم ككائن كامل في حال اختلاف نوع الـ PK، نعرض الكود المستخرج
          linked_transaction = {
              "type": "Sales Invoice",
              "invoice_id": invoice_code,
              "status": "COMPLETED / RECORDED",
          }
      elif "RETURN" in action_upper:
        if ref_id:
          ret = db.query(SalesReturn).filter_by(return_id=ref_id).first()
          if ret:
            linked_transaction = {
                "type": "Sales Return",
                "return_id": ret.return_id,
                "status": getattr(ret, "status", "N/A"),
            }
    except Exception:
      pass

    return jsonify({
        "audit_id": log_id,
        "user_id": getattr(log, "user_id", None),
        "operator": username,
        "action": action,
        "details": details_text,
        "timestamp": timestamp_str,
        "linked_transaction": linked_transaction,
    })

  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()