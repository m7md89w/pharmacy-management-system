from sqlalchemy.orm import Session
from models.all_models import Manufacturer


class ManufacturerRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        data: dict
    ):

        manufacturer = Manufacturer(
            **data
        )

        self.db.add(manufacturer)
        self.db.commit()
        self.db.refresh(
            manufacturer
        )

        return manufacturer

    def get_by_id(
        self,
        manufacturer_id: int
    ):

        return (
            self.db.query(
                Manufacturer
            )
            .filter(
                Manufacturer.manufacturer_id
                == manufacturer_id
            )
            .first()
        )

    def get_by_name(
        self,
        name: str
    ):

        return (
            self.db.query(
                Manufacturer
            )
            .filter(
                Manufacturer.name == name
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(
                Manufacturer
            )
            .all()
        )

    def update(
        self,
        manufacturer
    ):

        self.db.commit()
        self.db.refresh(
            manufacturer
        )

        return manufacturer

    def delete(
        self,
        manufacturer
    ):

        self.db.delete(
            manufacturer
        )
        self.db.commit()