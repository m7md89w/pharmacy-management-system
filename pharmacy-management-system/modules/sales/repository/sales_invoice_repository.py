from sqlalchemy.orm import Session

from models.all_models import SalesInvoice


class SalesInvoiceRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        invoice_data: dict
    ) -> SalesInvoice:

        invoice = SalesInvoice(
            **invoice_data
        )

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def get_by_id(
        self,
        invoice_id: int
    ) -> SalesInvoice | None:

        return (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.invoice_id
                == invoice_id
            )
            .first()
        )

    def get_by_invoice_number(
        self,
        invoice_number: str
    ):

        return (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.invoice_number
                == invoice_number
            )
            .first()
        )

    def get_all(self):

        return (
            self.db.query(SalesInvoice)
            .all()
        )

    def update(
        self,
        invoice: SalesInvoice
    ):

        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def delete(
        self,
        invoice: SalesInvoice
    ):

        self.db.delete(invoice)
        self.db.commit()

    def get_by_customer(
        self,
        customer_id: int
    ):

        return (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.customer_id
                == customer_id
            )
            .all()
        )

    def get_by_status(
        self,
        status: str
    ):

        return (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.status
                == status
            )
            .all()
        )