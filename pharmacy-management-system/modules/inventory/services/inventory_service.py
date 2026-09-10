from sqlalchemy import func
from models.all_models import (
    Medicine,
    MedicineBatch,
    StockMovement,
    PurchaseItem,
    SaleItem,
    SalesInvoice,
    SalesReturn,
    SalesReturnItem,
    PurchaseReturnItem,
    PurchaseReturn
)
from modules.inventory.repository.inventory_repository import InventoryRepository
from modules.medicines.repository.medicine_repository import MedicineRepository


class InventoryService:

    def __init__(
        self,
        inventory_repo: InventoryRepository,
        medicine_repo: MedicineRepository
    ):
        self.inventory_repo = inventory_repo
        self.medicine_repo = medicine_repo

    def create_inventory(
        self,
        data: dict
    ):

        medicine = self.medicine_repo.get_by_id(
            data["medicine_id"]
        )

        if not medicine:
            raise ValueError(
                "Medicine not found"
            )

        existing = self.inventory_repo.get_by_medicine(
            data["medicine_id"]
        )

        if existing:
            raise ValueError(
                "Inventory already exists for this medicine"
            )

        data.setdefault(
            "quantity",
            0
        )

        data.setdefault(
            "min_stock_level",
            0
        )

        return self.inventory_repo.create(
            data
        )

    def get_inventory(
        self,
        inventory_id: int
    ):

        inventory = self.inventory_repo.get_by_id(
            inventory_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        return inventory

    def get_inventory_by_medicine(
        self,
        medicine_id: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        return inventory

    def get_all_inventory(self):

        return self.inventory_repo.get_all()

    def get_detailed_inventory(self):
        inventories = self.inventory_repo.get_all()
        detailed_list = []
        db = self.inventory_repo.db

        for inv in inventories:
            # 1. استخراج بيانات الدواء حسب الموديل الفعلي (commercial_name & scientific_name)
            med = None
            try:
                med = self.medicine_repo.get_by_id(inv.medicine_id)
            except Exception:
                pass

            commercial_name = getattr(med, "commercial_name", None) if med else None
            scientific_name = getattr(med, "scientific_name", None) if med else None

            if commercial_name and scientific_name:
                med_name = f"{commercial_name} ({scientific_name})"
            elif commercial_name:
                med_name = commercial_name
            elif scientific_name:
                med_name = scientific_name
            else:
                med_name = f"Medicine #{inv.medicine_id}"

            barcode = getattr(med, "barcode", None) if med else None
            if str(barcode).strip().lower() in ("none", "null", ""):
                barcode = None

            # 2. استخراج بيانات الدفعات وحساب الكمية الأصلية بدقة
            batches_data = []
            try:
                batches = (
                    db.query(MedicineBatch)
                    .filter(MedicineBatch.medicine_id == inv.medicine_id)
                    .all()
                )

                for batch in batches:
                    current_qty = int(getattr(batch, "quantity", 0) or 0)
                    orig_qty = None

                    # أ) البحث في عناصر الشراء PurchaseItem عبر batch_id
                    try:
                        p_item = (
                            db.query(PurchaseItem)
                            .filter(PurchaseItem.batch_id == batch.batch_id)
                            .first()
                        )
                        if p_item and getattr(p_item, "quantity", None) is not None:
                            orig_qty = int(p_item.quantity)
                    except Exception:
                        pass

                    # ب) البحث في حركة التوريد StockMovement (العمود الحقيقي: quantity_change)
                    if orig_qty is None:
                        try:
                            sm = (
                                db.query(StockMovement)
                                .filter(
                                    StockMovement.batch_id == batch.batch_id,
                                    StockMovement.movement_type == "PURCHASE"
                                )
                                .order_by(StockMovement.movement_id.asc())
                                .first()
                            )
                            if sm and getattr(sm, "quantity_change", None) is not None:
                                orig_qty = abs(int(sm.quantity_change))
                        except Exception:
                            pass

                    # ج) الحساب المحاسبي الصافي للكمية الأصلية:
                    # Original = Current + Net Sold + Completed Purchase Returns
                    try:
                        # إجمالي المبيعات المكتملة للدفعة
                        total_sold = (
                            db.query(func.coalesce(func.sum(SaleItem.quantity), 0))
                            .join(SalesInvoice, SalesInvoice.invoice_id == SaleItem.invoice_id)
                            .filter(
                                SaleItem.batch_id == batch.batch_id,
                                SalesInvoice.status == "COMPLETED"
                            )
                            .scalar()
                        ) or 0

                        # إجمالي مرتجعات المبيعات المكتملة للدفعة
                        total_sales_returned = (
                            db.query(func.coalesce(func.sum(SalesReturnItem.quantity), 0))
                            .join(SalesReturn, SalesReturn.return_id == SalesReturnItem.return_id)
                            .filter(
                                SalesReturnItem.batch_id == batch.batch_id,
                                SalesReturn.status == "COMPLETED"
                            )
                            .scalar()
                        ) or 0

                        net_sold = max(int(total_sold) - int(total_sales_returned), 0)

                        # إجمالي مرتجعات المشتريات المكتملة للدفعة
                        total_purchase_returned = (
                            db.query(func.coalesce(func.sum(PurchaseReturnItem.quantity), 0))
                            .join(PurchaseReturn, PurchaseReturn.return_id == PurchaseReturnItem.return_id)
                            .filter(
                                PurchaseReturnItem.batch_id == batch.batch_id,
                                PurchaseReturn.status == "COMPLETED"
                            )
                            .scalar()
                        ) or 0

                        calc_orig = current_qty + net_sold + int(total_purchase_returned)
                        if orig_qty is None or orig_qty < calc_orig:
                            orig_qty = calc_orig
                    except Exception:
                        pass

                    # د) في حال عدم توفر سجلات، تكون الكمية الأصلية مساوية على الأقل للكمية الحالية
                    if orig_qty is None or orig_qty < current_qty:
                        orig_qty = current_qty

                    # أسعار الشراء والبيع حسب الموديل: purchase_price و selling_price
                    unit_cost = float(batch.purchase_price) if getattr(batch, "purchase_price", None) is not None else 0.0
                    selling_price = float(batch.selling_price) if getattr(batch, "selling_price", None) is not None else 0.0

                    batches_data.append({
                        "batch_id": batch.batch_id,
                        "batch_number": getattr(batch, "batch_number", "—"),
                        "original_quantity": int(orig_qty),
                        "remaining_quantity": int(current_qty),
                        "unit_cost": unit_cost,
                        "selling_price": selling_price,
                        "expiry_date": str(batch.expiry_date) if getattr(batch, "expiry_date", None) else None,
                        "manufacture_date": str(batch.manufacture_date) if getattr(batch, "manufacture_date", None) else None
                    })
            except Exception:
                batches_data = []

            detailed_list.append({
                "inventory_id": inv.inventory_id,
                "medicine_id": inv.medicine_id,
                "medicine_name": med_name,
                "barcode": barcode,
                "total_quantity": inv.quantity,
                "min_stock_level": inv.min_stock_level,
                "location": inv.location,
                "batches": batches_data
            })

        return detailed_list

    def update_inventory(
        self,
        inventory,
        data: dict
    ):

        if "quantity" in data:

            quantity = int(
                data["quantity"]
            )

            if quantity < 0:
                raise ValueError(
                    "Quantity cannot be negative"
                )

            inventory.quantity = quantity

        if "min_stock_level" in data:

            level = int(
                data["min_stock_level"]
            )

            if level < 0:
                raise ValueError(
                    "Minimum stock cannot be negative"
                )

            inventory.min_stock_level = level

        if "location" in data:

            inventory.location = data[
                "location"
            ]

        return self.inventory_repo.update(
            inventory
        )

    def delete_inventory(
        self,
        inventory
    ):

        return self.inventory_repo.delete(
            inventory
        )

    def increase_stock(
        self,
        medicine_id: int,
        quantity: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        inventory.quantity += quantity

        return self.inventory_repo.update(
            inventory
        )

    def decrease_stock(
        self,
        medicine_id: int,
        quantity: int
    ):

        inventory = self.inventory_repo.get_by_medicine(
            medicine_id
        )

        if not inventory:
            raise ValueError(
                "Inventory not found"
            )

        if inventory.quantity < quantity:
            raise ValueError(
                "Insufficient stock"
            )

        inventory.quantity -= quantity

        return self.inventory_repo.update(
            inventory
        )

    def get_low_stock(self):

        inventories = self.inventory_repo.get_all()

        return [
            inventory
            for inventory in inventories
            if inventory.quantity <= inventory.min_stock_level
        ]