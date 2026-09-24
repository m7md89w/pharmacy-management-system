import logging

from flask import Blueprint, request, jsonify
from ai_modules.drug_interactions.services.drug_interaction_service import DrugInteractionService

drug_interaction_controller = Blueprint(
    "drug_interaction_controller",
    __name__,
    url_prefix="/drug-interactions"
)

service = DrugInteractionService()
logger = logging.getLogger(__name__)

MAX_DRUGS_PER_REQUEST = 15


@drug_interaction_controller.route("/check", methods=["POST"])
def check_interactions():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON payload."}), 400

    current_drugs = data.get("current_drugs", [])
    new_drugs = data.get("new_drugs", [])

    if not isinstance(current_drugs, list) or not isinstance(new_drugs, list):
        return jsonify({"error": "Both 'current_drugs' and 'new_drugs' must be lists."}), 400

    if not current_drugs and not new_drugs:
        return jsonify({"error": "Please provide at least one drug to check."}), 400

    all_drugs = current_drugs + new_drugs

    if not all(isinstance(d, str) for d in all_drugs):
        return jsonify({"error": "All drug names must be strings."}), 400

    if len(all_drugs) > MAX_DRUGS_PER_REQUEST:
        return jsonify({
            "error": f"Too many drugs in a single request. Maximum allowed is {MAX_DRUGS_PER_REQUEST}."
        }), 400

    try:
        result = service.process_interactions(current_drugs, new_drugs)
        return jsonify(result), 200
    except Exception:
        logger.exception("Unexpected error while checking drug interactions")
        return jsonify({"error": "An unexpected error occurred while checking interactions."}), 500