from modules.medicines.repository.medicine_repository import (
    MedicineRepository,
)
from models.all_models import Inventory


class MedicineService:

  def __init__(self, repo: MedicineRepository):
    self.repo = repo

  # ==========================================
  # CREATE (مع إنشاء سجل المخزون ومكان التخزين تلقائياً)
  # ==========================================
  def create_medicine(self, data: dict):
    if not data.get("scientific_name"):
      raise ValueError("Scientific name is required")

    if not data.get("commercial_name"):
      raise ValueError("Commercial name is required")

    if not data.get("barcode"):
      raise ValueError("Barcode is required")

    existing = self.repo.get_by_barcode_any(data["barcode"])

    if existing:
      if not existing.is_active:
        raise ValueError("Medicine exists but is inactive.")

      raise ValueError("Barcode already exists.")

    if data.get("selling_price") is None:
      raise ValueError("Selling price is required")

    if float(data["selling_price"]) < 0:
      raise ValueError("Selling price cannot be negative")

    # استخراج حقول المخزون (مثل location و min_stock_level) إذا تم إرسالها من الواجهة
    location = data.pop("location", None)
    min_stock_level = data.pop("min_stock_level", 0)

    # 1. إنشاء الدواء في جدول medicines (مع دعم حقل strength)
    new_medicine = self.repo.create(data)

    # 2. إنشاء سجل المخزون المرتبط تلقائياً لتخزين مكان التخزين والكمية الابتدائية
    try:
      inventory_item = Inventory(
          medicine_id=new_medicine.medicine_id,
          quantity=0,
          min_stock_level=int(min_stock_level),
          location=location,
      )
      self.repo.db.add(inventory_item)
      self.repo.db.commit()
    except Exception as e:
      self.repo.db.rollback()
      raise ValueError(f"Failed to initialize inventory record: {str(e)}")

    return new_medicine

  # ==========================================
  # RESTORE
  # ==========================================
  def restore_medicine(self, barcode: str):
    medicine = self.repo.get_by_barcode_any(barcode)

    if not medicine:
      raise ValueError("Medicine not found.")

    if medicine.is_active:
      raise ValueError("Medicine is already active.")

    return self.repo.restore(medicine)

  # ==========================================
  # GET BY ID
  # ==========================================
  def get_medicine(self, medicine_id: int):
    medicine = self.repo.get_by_id(medicine_id)

    if not medicine:
      raise ValueError("Medicine not found")

    return medicine

  # ==========================================
  # GET ALL
  # ==========================================
  def get_all_medicines(self):
    return self.repo.get_all()

  # ==========================================
  # UPDATE
  # ==========================================
  def update_medicine(self, medicine, data: dict):
    if "barcode" in data and data["barcode"] != medicine.barcode:
      existing = self.repo.get_by_barcode(data["barcode"])

      if existing:
        raise ValueError("Barcode already exists.")

    # معالجة تحديث الـ location في جدول Inventory إذا تم إرساله ضمن البيانات
    if "location" in data:
      new_location = data.pop("location")
      if medicine.inventory:
        medicine.inventory.location = new_location
      else:
        # إذا لم يكن لديه سجل مخزون مسبقاً، نقوم بإنشائه
        inventory_item = Inventory(
            medicine_id=medicine.medicine_id, quantity=0, location=new_location
        )
        self.repo.db.add(inventory_item)

    if "min_stock_level" in data:
      new_min_stock = data.pop("min_stock_level")
      if medicine.inventory:
        medicine.inventory.min_stock_level = int(new_min_stock)

    fields = [
        "scientific_name",
        "commercial_name",
        "barcode",
        "strength",  # دعم حقل التركيز والجرعة للتحديث
        "description",
        "dosage_form",
        "requires_prescription",
        "category_id",
        "manufacturer_id",
        "selling_price",
    ]

    for field in fields:
      if field in data:
        if field == "selling_price" and float(data[field]) < 0:
          raise ValueError("Selling price cannot be negative")

        setattr(medicine, field, data[field])

    return self.repo.update(medicine)

  # ==========================================
  # DEACTIVATE
  # ==========================================
  def deactivate_medicine(self, medicine):
    return self.repo.deactivate(medicine)

  # ==========================================
  # DELETE (Protected & Bulletproof)
  # ==========================================
  def delete_medicine(self, medicine):
    medicine_id = getattr(medicine, "medicine_id", medicine)
    if isinstance(medicine_id, int):
      fresh_medicine = self.repo.get_by_id(medicine_id)
    else:
      fresh_medicine = self.repo.get_by_id(medicine.medicine_id)

    if not fresh_medicine:
      raise ValueError("Medicine not found")

    if fresh_medicine.batches and len(fresh_medicine.batches) > 0:
      raise ValueError(
          "Cannot delete medicine because it has associated batches."
      )

    if fresh_medicine.inventory and fresh_medicine.inventory.quantity > 0:
      raise ValueError(
          "Cannot delete medicine because there is remaining inventory stock."
      )

    if fresh_medicine.purchase_items and len(fresh_medicine.purchase_items) > 0:
      raise ValueError(
          "Cannot delete medicine because it is linked to purchase orders or"
          " items."
      )

    if fresh_medicine.sale_items and len(fresh_medicine.sale_items) > 0:
      raise ValueError(
          "Cannot delete medicine because it is linked to sales transactions."
      )

    # حذف سجل المخزون المرتبط أولاً لمنع مشاكل الـ Foreign Key إن وجدت
    if fresh_medicine.inventory:
      self.repo.db.delete(fresh_medicine.inventory)

    return self.repo.delete(fresh_medicine)

  # ==========================================
  # SEARCH
  # ==========================================
  def search_medicines(self, name: str):
    return self.repo.search_by_name(name)