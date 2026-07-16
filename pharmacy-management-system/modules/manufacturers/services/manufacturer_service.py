from modules.manufacturers.repository.manufacturer_repository import (
    ManufacturerRepository
)


class ManufacturerService:

    def __init__(
        self,
        manufacturer_repo: ManufacturerRepository
    ):
        self.manufacturer_repo = (
            manufacturer_repo
        )

    def create_manufacturer(
        self,
        data: dict
    ):

        existing = (
            self.manufacturer_repo.get_by_name(
                data["name"]
            )
        )

        if existing:
            raise ValueError(
                "Manufacturer already exists"
            )

        return (
            self.manufacturer_repo.create(
                data
            )
        )

    def get_manufacturer(
        self,
        manufacturer_id: int
    ):

        manufacturer = (
            self.manufacturer_repo.get_by_id(
                manufacturer_id
            )
        )

        if not manufacturer:
            raise ValueError(
                "Manufacturer not found"
            )

        return manufacturer

    def get_all_manufacturers(self):

        return (
            self.manufacturer_repo.get_all()
        )

    def update_manufacturer(
        self,
        manufacturer,
        data: dict
    ):

        if "name" in data:

            existing = (
                self.manufacturer_repo.get_by_name(
                    data["name"]
                )
            )

            if (
                existing
                and existing.manufacturer_id
                != manufacturer.manufacturer_id
            ):
                raise ValueError(
                    "Manufacturer already exists"
                )

            manufacturer.name = data[
                "name"
            ]

        if "contact_email" in data:
            manufacturer.contact_email = data[
                "contact_email"
            ]

        if "contact_phone" in data:
            manufacturer.contact_phone = data[
                "contact_phone"
            ]

        if "address" in data:
            manufacturer.address = data[
                "address"
            ]

        return (
            self.manufacturer_repo.update(
                manufacturer
            )
        )

    def delete_manufacturer(
        self,
        manufacturer
    ):

        return (
            self.manufacturer_repo.delete(
                manufacturer
            )
        )