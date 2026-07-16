from sqlalchemy.orm import Session

from models.all_models import Customer


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, customer_data: dict) -> Customer:

        customer = Customer(**customer_data)

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def get_by_id(
        self,
        customer_id: int
    ) -> Customer | None:

        return (
            self.db.query(Customer)
            .filter(
                Customer.customer_id == customer_id
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(Customer)
            .all()
        )

    def update(
        self,
        customer: Customer
    ):

        self.db.commit()
        self.db.refresh(customer)

        return customer

    def delete(
        self,
        customer: Customer
    ):

        self.db.delete(customer)
        self.db.commit()