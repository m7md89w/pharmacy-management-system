import os
import csv
from database.session import SessionLocal
from models.all_models import Medicine, DrugInteraction

db = SessionLocal()

try:
    print("Loading CSV...")

    # Calculate absolute path relative to this script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "datasets", "db_drug_interactions.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    # ==========================
    # Load medicines once
    # ==========================
    medicines = db.query(Medicine).all()
    medicine_map = {m.scientific_name.lower(): m for m in medicines}
    print(f"Medicines in database: {len(medicine_map)}")

    # ==========================
    # Existing interactions
    # ==========================
    existing_pairs = set()
    for interaction in db.query(DrugInteraction).all():
        pair = tuple(sorted([interaction.medicine_1_id, interaction.medicine_2_id]))
        existing_pairs.add(pair)
    print(f"Existing interactions: {len(existing_pairs)}")

    created = 0
    skipped = 0

    # ==========================
    # Import using standard csv module (zero dependencies)
    # ==========================
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            drug1 = str(row.get("Drug 1", "")).strip().lower()
            drug2 = str(row.get("Drug 2", "")).strip().lower()
            description = str(row.get("Interaction Description", "")).strip()

            medicine1 = medicine_map.get(drug1)
            medicine2 = medicine_map.get(drug2)

            if not medicine1 or not medicine2:
                skipped += 1
                continue

            pair = tuple(sorted([medicine1.medicine_id, medicine2.medicine_id]))

            if pair in existing_pairs:
                continue

            # ==========================
            # Guess severity
            # ==========================
            severity = "MODERATE"
            desc = description.lower()

            if "contraindicated" in desc:
                severity = "CONTRAINDICATED"
            elif "major" in desc:
                severity = "MAJOR"
            elif "minor" in desc:
                severity = "MINOR"

            interaction = DrugInteraction(
                medicine_1_id=medicine1.medicine_id,
                medicine_2_id=medicine2.medicine_id,
                severity=severity,
                description=description,
                source="DATASET"
            )

            db.add(interaction)
            existing_pairs.add(pair)
            created += 1

            if created % 100 == 0:
                print(f"Loaded: {created}")

    db.commit()
    print("==============================")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print("==============================")

except Exception as e:
    db.rollback()
    print(f"Error: {e}")

finally:
    db.close()