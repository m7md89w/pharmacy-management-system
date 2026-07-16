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

        interactions = []

        for med1, med2 in combinations(
            medicine_ids,
            2
        ):

            interaction = (
                self.interaction_repo.get_by_pair(
                    med1,
                    med2
                )
            )

            if interaction:
                interactions.append(
                    interaction
                )

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