import pandas as pd

from database.session import SessionLocal
from models.all_models import (
    Medicine,
    DrugInteraction
)

db = SessionLocal()

try:
    print("Loading CSV...")

    df = pd.read_csv(
        r"pharmacy-management-system\datasets\db_drug_interactions.csv"
    )

    print(f"Rows: {len(df)}")

    # ==========================
    # Load medicines once
    # ==========================
    medicines = db.query(
        Medicine
    ).all()

    medicine_map = {
        m.scientific_name.lower(): m
        for m in medicines
    }

    print(
        f"Medicines in database: {len(medicine_map)}"
    )

    # ==========================
    # Existing interactions
    # ==========================
    existing_pairs = set()

    for interaction in (
        db.query(DrugInteraction)
        .all()
    ):

        pair = tuple(
            sorted(
                [
                    interaction.medicine_1_id,
                    interaction.medicine_2_id
                ]
            )
        )

        existing_pairs.add(pair)

    print(
        f"Existing interactions: {len(existing_pairs)}"
    )

    created = 0
    skipped = 0

    # ==========================
    # Import
    # ==========================
    for _, row in df.iterrows():

        drug1 = str(
            row["Drug 1"]
        ).strip().lower()

        drug2 = str(
            row["Drug 2"]
        ).strip().lower()

        description = str(
            row["Interaction Description"]
        ).strip()

        medicine1 = medicine_map.get(
            drug1
        )

        medicine2 = medicine_map.get(
            drug2
        )

        if not medicine1 or not medicine2:
            skipped += 1
            continue

        pair = tuple(
            sorted(
                [
                    medicine1.medicine_id,
                    medicine2.medicine_id
                ]
            )
        )

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
            print(
                f"Created: {created}"
            )

    db.commit()

    print()
    print("==============================")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print("==============================")

except Exception as e:
    db.rollback()
    print(
        f"Error: {e}"
    )

finally:
    db.close()