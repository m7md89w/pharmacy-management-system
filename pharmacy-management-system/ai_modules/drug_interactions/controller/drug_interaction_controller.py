from flask import (
    Blueprint,
    request,
    jsonify
)

from database.session import SessionLocal

from ai_modules.drug_interactions.repository.drug_interaction_repository import (
    DrugInteractionRepository
)

from ai_modules.drug_interactions.services.drug_interaction_service import (
    DrugInteractionService
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)

from modules.auth.decorators.auth_required import (
    auth_required
)

drug_interaction_controller = Blueprint(
    "drug_interactions",
    __name__,
    url_prefix="/drug-interactions"
)

@drug_interaction_controller.route(
    "/check",
    methods=["POST"]
)
@auth_required
def check_interactions():

    db = SessionLocal()

    try:
        data = request.get_json()

        medicine_ids = data.get(
            "medicine_ids",
            []
        )

        service = DrugInteractionService(
            DrugInteractionRepository(db),
            MedicineRepository(db)
        )

        interactions = (
            service.check_interactions(
                medicine_ids
            )
        )

        result = []

        for interaction in interactions:

            result.append({
                "interaction_id":
                interaction.interaction_id,

                "medicine_1_id":
                interaction.medicine_1_id,

                "medicine_2_id":
                interaction.medicine_2_id,

                "severity":
                interaction.severity,

                "description":
                interaction.description
            })

        return jsonify(result), 200

    finally:
        db.close()

        