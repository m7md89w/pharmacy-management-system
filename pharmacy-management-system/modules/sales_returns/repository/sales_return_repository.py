from sqlalchemy.orm import Session

from models.all_models import SalesReturn


class SalesReturnRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # CREATE
    # ==========================================
    def create(
        self,
        data: dict
    ):

        sales_return = SalesReturn(**data)

        self.db.add(sales_return)
        self.db.commit()
        self.db.refresh(sales_return)

        return sales_return

    # ==========================================
    # GET BY ID
    # ==========================================
    def get_by_id(
        self,
        return_id: int
    ):

        return (
            self.db.query(SalesReturn)
            .filter(
                SalesReturn.return_id == return_id
            )
            .first()
        )

    # ==========================================
    # GET ALL
    # ==========================================
    def get_all(self):

        return (
            self.db.query(SalesReturn)
            .order_by(
                SalesReturn.return_id.desc()
            )
            .all()
        )

    # ==========================================
    # GET BY INVOICE
    # ==========================================
    def get_by_invoice(
        self,
        invoice_id: int
    ):

        return (
            self.db.query(SalesReturn)
            .filter(
                SalesReturn.invoice_id == invoice_id
            )
            .order_by(
                SalesReturn.return_id.desc()
            )
            .all()
        )

    # ==========================================
    # GET DRAFT BY INVOICE
    # ==========================================
    def get_draft_by_invoice(
        self,
        invoice_id: int
    ):

        return (
            self.db.query(SalesReturn)
            .filter(
                SalesReturn.invoice_id == invoice_id,
                SalesReturn.status == "DRAFT"
            )
            .first()
        )

    # ==========================================
    # GET COMPLETED BY INVOICE
    # ==========================================
    def get_completed_by_invoice(
        self,
        invoice_id: int
    ):

        return (
            self.db.query(SalesReturn)
            .filter(
                SalesReturn.invoice_id == invoice_id,
                SalesReturn.status == "COMPLETED"
            )
            .all()
        )

    # ==========================================
    # GET BY STATUS
    # ==========================================
    def get_by_status(
        self,
        status: str
    ):

        return (
            self.db.query(SalesReturn)
            .filter(
                SalesReturn.status == status
            )
            .order_by(
                SalesReturn.return_id.desc()
            )
            .all()
        )
    
        # ==========================================
    # GET INVOICES WITH RETURNS
    # ==========================================
    def get_returned_invoices(self):

        return (

            self.db.query(
                SalesReturn.invoice_id
            )

            .distinct()

            .order_by(
                SalesReturn.invoice_id.desc()
            )

            .all()

        )

    # ==========================================
    # UPDATE
    # ==========================================
    def update(
        self,
        sales_return
    ):

        self.db.commit()
        self.db.refresh(sales_return)

        return sales_return

    # ==========================================
    # DELETE
    # ==========================================
    def delete(
        self,
        sales_return
    ):

        self.db.delete(sales_return)
        self.db.commit()

        return True