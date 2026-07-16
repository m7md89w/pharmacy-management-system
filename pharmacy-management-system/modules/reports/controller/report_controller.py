from flask import Blueprint, jsonify
from database.session import SessionLocal

from modules.reports.repository.sales_report_repository import (
    SalesReportRepository
)
from modules.reports.repository.purchase_report_repository import (
    PurchaseReportRepository
)
from modules.reports.repository.profit_report_repository import (
    ProfitReportRepository
)
from modules.reports.repository.inventory_report_repository import (
    InventoryReportRepository
)
from modules.reports.repository.low_stock_report_repository import (
    LowStockReportRepository
)
from modules.reports.repository.expiry_report_repository import (
    ExpiryReportRepository
)
from modules.reports.repository.dashboard_repository import (
    DashboardRepository
)

from modules.reports.services.sales_report_service import (
    SalesReportService
)
from modules.reports.services.purchase_report_service import (
    PurchaseReportService
)
from modules.reports.services.profit_report_service import (
    ProfitReportService
)
from modules.reports.services.inventory_report_service import (
    InventoryReportService
)
from modules.reports.services.low_stock_report_service import (
    LowStockReportService
)
from modules.reports.services.expiry_report_service import (
    ExpiryReportService
)
from modules.reports.services.dashboard_service import (
    DashboardService
)

from modules.auth.decorators.auth_required import auth_required


report_controller = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


# =====================================================
# SALES REPORT
# =====================================================

@report_controller.route(
    "/sales",
    methods=["GET"]
)
@auth_required
def sales_report():

    db = SessionLocal()

    try:
        repo = SalesReportRepository(db)
        service = SalesReportService(repo)

        return jsonify(
            service.get_summary()
        )

    finally:
        db.close()


# =====================================================
# PURCHASES REPORT
# =====================================================

@report_controller.route(
    "/purchases",
    methods=["GET"]
)
@auth_required
def purchases_report():

    db = SessionLocal()

    try:
        repo = PurchaseReportRepository(db)
        service = PurchaseReportService(repo)

        return jsonify(
            service.get_summary()
        )

    finally:
        db.close()


# =====================================================
# PROFIT REPORT
# =====================================================

@report_controller.route(
    "/profit",
    methods=["GET"]
)
@auth_required
def profit_report():

    db = SessionLocal()

    try:
        repo = ProfitReportRepository(db)
        service = ProfitReportService(repo)

        return jsonify(
            service.get_summary()
        )

    finally:
        db.close()


# =====================================================
# INVENTORY REPORT
# =====================================================

@report_controller.route(
    "/inventory",
    methods=["GET"]
)
@auth_required
def inventory_report():

    db = SessionLocal()

    try:
        repo = InventoryReportRepository(db)
        service = InventoryReportService(repo)

        return jsonify(
            service.get_summary()
        )

    finally:
        db.close()


# =====================================================
# LOW STOCK REPORT
# =====================================================

@report_controller.route(
    "/low-stock",
    methods=["GET"]
)
@auth_required
def low_stock_report():

    db = SessionLocal()

    try:
        repo = LowStockReportRepository(db)
        service = LowStockReportService(repo)

        inventories = service.get_low_stock()

        return jsonify([
            {
                "inventory_id": i.inventory_id,
                "medicine_id": i.medicine_id,
                "quantity": i.quantity,
                "min_stock_level": i.min_stock_level,
                "location": i.location
            }
            for i in inventories
        ])

    finally:
        db.close()


# =====================================================
# EXPIRY REPORT
# =====================================================

@report_controller.route(
    "/expiry",
    methods=["GET"]
)
@auth_required
def expiry_report():

    db = SessionLocal()

    try:
        repo = ExpiryReportRepository(db)
        service = ExpiryReportService(repo)

        batches = service.get_expired_batches()

        return jsonify([
            {
                "batch_id": batch.batch_id,
                "medicine_id": batch.medicine_id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiry_date": str(
                    batch.expiry_date
                )
            }
            for batch in batches
        ])

    finally:
        db.close()


# =====================================================
# DASHBOARD REPORT
# =====================================================

@report_controller.route(
    "/dashboard",
    methods=["GET"]
)
@auth_required
def dashboard_report():

    db = SessionLocal()

    try:
        repo = DashboardRepository(db)
        service = DashboardService(repo)

        return jsonify(
            service.get_summary()
        )

    finally:
        db.close()