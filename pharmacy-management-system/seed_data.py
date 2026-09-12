from datetime import date, timedelta
import os
import sys

import bcrypt
from dotenv import load_dotenv

from database.session import SessionLocal
from models.all_models import (
    Category,
    Customer,
    Inventory,
    Manufacturer,
    Medicine,
    MedicineBatch,
    Role,
    Supplier,
    User,
)

load_dotenv()


# ==================================================
# GUARD: require a strong password via environment variable
# ==================================================

ADMIN_SEED_PASSWORD = os.environ.get("ADMIN_SEED_PASSWORD", "")

if not ADMIN_SEED_PASSWORD:
  print(
      "❌ Error: ADMIN_SEED_PASSWORD environment variable is not set.\n"
      "   Set it in your .env file before running seed_data.py.\n"
      "   Example:  ADMIN_SEED_PASSWORD=MyStr0ngP@ssword"
  )
  sys.exit(1)


# ==================================================
# SEED
# ==================================================

db = SessionLocal()

try:
  # --------------------------
  # ROLES
  # --------------------------
  admin_role = Role(role_name="Admin", description="System Administrator")
  pharmacist_role = Role(role_name="Pharmacist", description="Pharmacist")
  cashier_role = Role(role_name="Cashier", description="Cashier")

  db.add_all([admin_role, pharmacist_role, cashier_role])
  db.commit()

  # --------------------------
  # ADMIN USER
  # --------------------------
  hashed_password = bcrypt.hashpw(
      ADMIN_SEED_PASSWORD.encode("utf-8"),
      bcrypt.gensalt(),
  ).decode("utf-8")

  admin = User(
      username="admin",
      full_name="System Administrator",
      password_hash=hashed_password,
      role_id=admin_role.role_id,
      is_active=True,
  )

  db.add(admin)
  db.commit()

  # --------------------------
  # CATEGORY
  # --------------------------
  category = Category(
      category_name="General Medicines",
      description="General medicines category",
  )

  db.add(category)
  db.commit()
  db.refresh(category)

  # --------------------------
  # MANUFACTURER
  # --------------------------
  manufacturer = Manufacturer(
      name="Pfizer",
      contact_email="info@pfizer.com",
      contact_phone="123456789",
      address="USA",
  )

  db.add(manufacturer)
  db.commit()
  db.refresh(manufacturer)

  # --------------------------
  # SUPPLIERS
  # --------------------------
  suppliers = [
      Supplier(
          name="Jordan Pharma",
          contact_person="Ahmad Ali",
          phone="0791111111",
          email="info@jordanpharma.com",
          address="Amman, Jordan",
          is_active=True,
      ),
      Supplier(
          name="Middle East Medical",
          contact_person="Mohammad Hassan",
          phone="0792222222",
          email="sales@memedical.com",
          address="Zarqa, Jordan",
          is_active=True,
      ),
      Supplier(
          name="International Drug Store",
          contact_person="Khaled Omar",
          phone="0793333333",
          email="contact@ids.com",
          address="Irbid, Jordan",
          is_active=True,
      ),
  ]

  db.add_all(suppliers)
  db.commit()

  for supplier in suppliers:
    db.refresh(supplier)

  # --------------------------
  # MEDICINES (مع دعم حقل strength للتركيز والجرعة)
  # --------------------------
  medicines_data = [
      {
          "scientific_name": "Paracetamol",
          "commercial_name": "Panadol",
          "strength": "500mg",
          "barcode": "MED-001",
          "description": "Pain reliever",
          "dosage_form": "TABLET",
          "requires_prescription": False,
          "selling_price": 5.0,
      },
      {
          "scientific_name": "Aspirin",
          "commercial_name": "Aspirin",
          "strength": "100mg",
          "barcode": "MED-002",
          "description": "Blood thinner",
          "dosage_form": "TABLET",
          "requires_prescription": False,
          "selling_price": 3.0,
      },
      {
          "scientific_name": "Warfarin",
          "commercial_name": "Warfarin",
          "strength": "5mg",
          "barcode": "MED-003",
          "description": "Anticoagulant",
          "dosage_form": "TABLET",
          "requires_prescription": True,
          "selling_price": 8.0,
      },
      {
          "scientific_name": "Ibuprofen",
          "commercial_name": "Brufen",
          "strength": "400mg",
          "barcode": "MED-004",
          "description": "NSAID",
          "dosage_form": "TABLET",
          "requires_prescription": False,
          "selling_price": 4.0,
      },
      {
          "scientific_name": "Amoxicillin",
          "commercial_name": "Amoxil",
          "strength": "500mg",
          "barcode": "MED-005",
          "description": "Antibiotic",
          "dosage_form": "CAPSULE",
          "requires_prescription": True,
          "selling_price": 6.0,
      },
      {
          "scientific_name": "Metformin",
          "commercial_name": "Glucophage",
          "strength": "850mg",
          "barcode": "MED-006",
          "description": "Diabetes medicine",
          "dosage_form": "TABLET",
          "requires_prescription": True,
          "selling_price": 7.0,
      },
      {
          "scientific_name": "Atorvastatin",
          "commercial_name": "Lipitor",
          "strength": "20mg",
          "barcode": "MED-007",
          "description": "Cholesterol medicine",
          "dosage_form": "TABLET",
          "requires_prescription": True,
          "selling_price": 9.0,
      },
      {
          "scientific_name": "Omeprazole",
          "commercial_name": "Losec",
          "strength": "20mg",
          "barcode": "MED-008",
          "description": "Acid reflux medicine",
          "dosage_form": "CAPSULE",
          "requires_prescription": False,
          "selling_price": 5.0,
      },
  ]

  medicines = []
  for med_info in medicines_data:
    med = Medicine(
        scientific_name=med_info["scientific_name"],
        commercial_name=med_info["commercial_name"],
        strength=med_info["strength"],
        barcode=med_info["barcode"],
        description=med_info["description"],
        dosage_form=med_info["dosage_form"],
        requires_prescription=med_info["requires_prescription"],
        category_id=category.category_id,
        manufacturer_id=manufacturer.manufacturer_id,
        selling_price=med_info["selling_price"],
        is_active=True,
    )
    medicines.append(med)

  db.add_all(medicines)
  db.commit()

  for medicine in medicines:
    db.refresh(medicine)

  # --------------------------
  # INVENTORY & BATCHES (توليد المخزون والدفعات لضمان جاهزية البيع)
  # --------------------------
  inventories = []
  batches = []
  future_expiry = date.today() + timedelta(days=365)  # دفعة صالحة لمدة سنة

  for medicine in medicines:
    # إنشاء سجل المخزون
    inv = Inventory(
        medicine_id=medicine.medicine_id,
        quantity=100,
        min_stock_level=10,
        location="A1",
    )
    inventories.append(inv)

    # إنشاء دفعة مخزونية أولية (Batch) مرتبطة بالمورد والدواء لكي تظهر في فواتير المبيعات
    batch = MedicineBatch(
        medicine_id=medicine.medicine_id,
        supplier_id=suppliers[0].supplier_id,
        batch_number=f"BATCH-{medicine.barcode}",
        quantity=100,
        purchase_price=float(medicine.selling_price) * 0.7,
        selling_price=float(medicine.selling_price),
        manufacture_date=date.today(),
        expiry_date=future_expiry,
    )
    batches.append(batch)

  db.add_all(inventories)
  db.add_all(batches)
  db.commit()

  # --------------------------
  # CUSTOMER
  # --------------------------
  customer = Customer(
      full_name="Test Customer",
      phone="0799999999",
      email="customer@test.com",
  )

  db.add(customer)
  db.commit()

  print("✅ Seed Data Created Successfully")
  print()
  print("Admin Credentials:")
  print("  Username: admin")
  print("  Password: (value of ADMIN_SEED_PASSWORD env variable)")
  print()
  print(f"  Medicines Created : {len(medicines)}")خ
  print(f"  Batches Created   : {len(batches)}")
  print(f"  Suppliers Created : {len(suppliers)}")

except Exception as e:
  db.rollback()
  print(f"❌ Error: {e}")

finally:
  db.close()