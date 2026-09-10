from itertools import combinations

from ai_modules.drug_interactions.repository.drug_interaction_repository import (
    DrugInteractionRepository
)

from modules.medicines.repository.medicine_repository import (
    MedicineRepository
)


class DrugInteractionService:

    def __init__(
        self,
        interaction_repo: DrugInteractionRepository,
        medicine_repo: MedicineRepository
    ):
        self.interaction_repo = interaction_repo
        self.medicine_repo = medicine_repo

    def check_interactions(
        self,
        medicine_ids: list[int]
    ):
        if not medicine_ids or len(medicine_ids) < 2:
            return []

        med_ids_set = set(medicine_ids)
        all_interactions = self.interaction_repo.get_by_medicine_ids(list(med_ids_set))

        seen_ids = set()
        interactions = []
        for i in all_interactions:
            if i.interaction_id not in seen_ids:
                if (i.medicine_1_id in med_ids_set and 
                        i.medicine_2_id in med_ids_set and 
                        i.medicine_1_id != i.medicine_2_id):
                    seen_ids.add(i.interaction_id)
                    interactions.append(i)

        return interactions

    def get_medicine_interactions(
        self,
        medicine_id: int
    ):
        return (
            self.interaction_repo.get_by_medicine(
                medicine_id
            )
        )