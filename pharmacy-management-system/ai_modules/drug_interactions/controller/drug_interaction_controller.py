from flask import Blueprint, request, jsonify

from database.session import SessionLocal

from ai_modules.drug_interactions.repository.drug_interaction_repository import (
    DrugInteractionRepository,
)
from ai_modules.drug_interactions.services.drug_interaction_service import (
    DrugInteractionService,
)
from modules.medicines.repository.medicine_repository import MedicineRepository
from modules.auth.decorators.auth_required import auth_required


drug_interaction_controller = Blueprint(
    "drug_interactions",
    __name__,
    url_prefix="/drug-interactions",
)


@drug_interaction_controller.route("/check", methods=["POST"])
@auth_required
def check_interactions():
    """
    Checks for known drug-drug interactions among a given list of medicine IDs.

    Request body (JSON):
        { "medicine_ids": [1, 2, 3] }

    Returns:
        200: List of interaction objects (may be empty if no interactions found)
        400: { "error": "..." }  — invalid input
    """
    # --------------------------------------------------
    # 1. Parse & validate input
    # --------------------------------------------------
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    medicine_ids = data.get("medicine_ids")

    if medicine_ids is None:
        return jsonify({"error": "Field 'medicine_ids' is required."}), 400

    if not isinstance(medicine_ids, list):
        return jsonify({"error": "'medicine_ids' must be a list of integers."}), 400

    if len(medicine_ids) < 2:
        # Interactions require at least 2 medicines.
        return jsonify([]), 200

    # --------------------------------------------------
    # 2. Check interactions
    # --------------------------------------------------
    db = SessionLocal()

    try:
        service = DrugInteractionService(
            DrugInteractionRepository(db),
            MedicineRepository(db),
        )

        interactions = service.check_interactions(medicine_ids)

        result = [
            {
                "interaction_id": interaction.interaction_id,
                "medicine_1_id": interaction.medicine_1_id,
                "medicine_2_id": interaction.medicine_2_id,
                "severity": interaction.severity,
                "description": interaction.description,
                "source": interaction.source,
            }
            for interaction in interactions
        ]

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    finally:
        db.close()