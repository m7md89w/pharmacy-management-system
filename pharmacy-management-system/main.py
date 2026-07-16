from flask import Flask

# ==========================
# AUTH
# ==========================

from modules.auth.controller.auth_controller import auth_controller

# ==========================
# ROLES
# ==========================

from modules.roles.controller.role_controller import role_controller

# ==========================
# USERS
# ==========================

from modules.users.controller.user_controller import user_controller

# ==========================
# SUPPLIERS
# ==========================

from modules.suppliers.controllers.supplier_controller import supplier_controller

# ==========================
# CUSTOMERS
# ==========================

from modules.customers.controller.customer_controller import customer_controller

# ==========================
# MEDICINES
# ==========================

from modules.medicines.controller.medicine_controller import medicine_controller

from modules.medicines.controller.medicine_batch_controller import (
    medicine_batch_controller
)

# ==========================
# PURCHASES
# ==========================

from modules.purchases.controller.purchase_order_controller import (
    purchase_order_controller
)

from modules.purchases.controller.purchase_item_controller import (
    purchase_item_controller
)

# ==========================
# SALES
# ==========================

from modules.sales.controller.sales_invoice_controller import (
    sales_invoice_controller
)

from modules.sales.controller.sale_item_controller import (
    sale_item_controller
)

# ==========================
# STOCK MOVEMENTS
# ==========================

from modules.stock_movements.controllers.stock_movement_controller import (
    stock_movement_controller
)

from modules.inventory.controller.inventory_controller import inventory_controller

from modules.sales_returns.controller.sales_return_controller import (
    sales_return_controller
)
from modules.sales_returns.controller.sales_return_item_controller import (
    sales_return_item_controller
)

from modules.expired_medicines.controller.expired_medicine_controller import (
    expired_medicine_controller
)

from modules.expired_medicines.controller.expired_medicine_item_controller import (
    expired_medicine_item_controller
)

from modules.purchase_returns.controller.purchase_return_controller import (purchase_return_controller)

from modules.purchase_returns.controller.purchase_return_item_controller import (purchase_return_item_controller)

from modules.reports.controller.report_controller import (report_controller)

from modules.audit_logs.controller.audit_log_controller import (audit_log_controller)

from modules.categories.controller.category_controller import (
    category_controller
)

from modules.manufacturers.controller.manufacturer_controller import (
    manufacturer_controller
)

from modules.prescriptions.controller.prescription_controller import (prescription_controller)

from modules.prescriptions.controller.prescription_item_controller import (prescription_item_controller)

from modules.notifications.controller.notification_controller import (notification_controller)

from ai_modules.drug_interactions.controller.drug_interaction_controller import (drug_interaction_controller)

app = Flask(__name__)

# ==========================
# REGISTER BLUEPRINTS
# ==========================

app.register_blueprint(auth_controller)

app.register_blueprint(role_controller)

app.register_blueprint(user_controller)

app.register_blueprint(supplier_controller)

app.register_blueprint(customer_controller)

app.register_blueprint(medicine_controller)

app.register_blueprint(medicine_batch_controller)

app.register_blueprint(purchase_order_controller)

app.register_blueprint(purchase_item_controller)

app.register_blueprint(sales_invoice_controller)

app.register_blueprint(sale_item_controller)

app.register_blueprint(stock_movement_controller)

app.register_blueprint(inventory_controller)

app.register_blueprint(sales_return_controller)

app.register_blueprint(sales_return_item_controller)

app.register_blueprint(expired_medicine_controller)

app.register_blueprint(expired_medicine_item_controller)

app.register_blueprint(purchase_return_controller)

app.register_blueprint(purchase_return_item_controller)

app.register_blueprint(report_controller)

app.register_blueprint(audit_log_controller)

app.register_blueprint(category_controller)

app.register_blueprint(manufacturer_controller)

app.register_blueprint(prescription_controller)

app.register_blueprint(prescription_item_controller)

app.register_blueprint(notification_controller)

app.register_blueprint(drug_interaction_controller)

@app.route("/")
def home():

    return {
        "message": "Pharmacy Management System API Running"
    }


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )