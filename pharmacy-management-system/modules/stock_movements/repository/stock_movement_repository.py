from sqlalchemy.orm import Session

from models.all_models import StockMovement


class StockMovementRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        movement_data: dict
    ) -> StockMovement:

        movement = StockMovement(
            **movement_data
        )

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def get_by_id(
        self,
        movement_id: int
    ) -> StockMovement | None:

        return (
            self.db.query(StockMovement)
            .filter(
                StockMovement.movement_id
                == movement_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(StockMovement)
            .all()
        )

    def get_by_batch(
        self,
        batch_id: int
    ):

        return (
            self.db.query(StockMovement)
            .filter(
                StockMovement.batch_id
                == batch_id
            )
            .all()
        )

    def update(
        self,
        movement: StockMovement
    ):

        self.db.commit()
        self.db.refresh(movement)

        return movement

    def delete(
        self,
        movement: StockMovement
    ):

        self.db.delete(movement)
        self.db.commit()