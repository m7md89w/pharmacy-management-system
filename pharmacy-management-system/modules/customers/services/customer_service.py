from modules.customers.repository.customer_repository import CustomerRepository


class CustomerService:

    def __init__(
        self,
        customer_repo: CustomerRepository
    ):
        self.customer_repo = customer_repo

    def create_customer(
        self,
        data: dict
    ):

        return self.customer_repo.create(
            data
        )

    def get_customer(
        self,
        customer_id: int
    ):

        customer = self.customer_repo.get_by_id(
            customer_id
        )

        if not customer:
            raise ValueError(
                "Customer not found"
            )

        return customer

    def get_all_customers(self):

        return self.customer_repo.get_all()

    def update_customer(
        self,
        customer,
        data: dict
    ):

        fields = [
            "full_name",
            "phone",
            "email",
            "loyalty_points"
        ]

        for field in fields:

            if field in data:
                setattr(
                    customer,
                    field,
                    data[field]
                )

        return self.customer_repo.update(
            customer
        )

    def delete_customer(
        self,
        customer
    ):

        return self.customer_repo.delete(
            customer
        )