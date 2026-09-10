from models.all_models import DrugInteraction


class DrugInteractionRepository:

    def __init__(self, db):
        self.db = db

    def create(self, data: dict):
        interaction = DrugInteraction(**data)

        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)

        return interaction

    def get_by_id(
        self,
        interaction_id: int
    ):
        return (
            self.db.query(DrugInteraction)
            .filter(
                DrugInteraction.interaction_id
                == interaction_id
            )
            .first()
        )

    def get_by_pair(
        self,
        medicine_1_id: int,
        medicine_2_id: int
    ):
        return (
            self.db.query(DrugInteraction)
            .filter(
                (
                    (DrugInteraction.medicine_1_id == medicine_1_id)
                    &
                    (DrugInteraction.medicine_2_id == medicine_2_id)
                )
                |
                (
                    (DrugInteraction.medicine_1_id == medicine_2_id)
                    &
                    (DrugInteraction.medicine_2_id == medicine_1_id)
                )
            )
            .first()
        )

    def get_by_medicine(
        self,
        medicine_id: int
    ):
        return (
            self.db.query(DrugInteraction)
            .filter(
                (
                    DrugInteraction.medicine_1_id
                    == medicine_id
                )
                |
                (
                    DrugInteraction.medicine_2_id
                    == medicine_id
                )
            )
            .all()
        )

    def get_all(self):
        return (
            self.db.query(
                DrugInteraction
            )
            .all()
        )

    def get_by_medicine_ids(self, medicine_ids: list[int]) -> list[DrugInteraction]:
        return (
            self.db.query(DrugInteraction)
            .filter(
                DrugInteraction.medicine_1_id.in_(medicine_ids),
                DrugInteraction.medicine_2_id.in_(medicine_ids)
            )
            .all()
        )

    def delete(
        self,
        interaction
    ):
        self.db.delete(
            interaction
        )
        self.db.commit()