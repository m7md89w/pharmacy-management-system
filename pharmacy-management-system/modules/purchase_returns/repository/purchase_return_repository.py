from sqlalchemy.orm import Session

from models.all_models import PurchaseReturn


class PurchaseReturnRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # CREATE
    # ==================================================
    def create(
        self,
        data: dict
    ):

        purchase_return = PurchaseReturn(
            **data
        )

        self.db.add(
            purchase_return
        )

        self.db.commit()

        self.db.refresh(
            purchase_return
        )

        return purchase_return

    # ==================================================
    # GET BY ID
    # ==================================================
    def get_by_id(
        self,
        return_id: int
    ):

        return (

            self.db.query(
                PurchaseReturn
            )

            .filter(
                PurchaseReturn.return_id
                == return_id
            )

            .first()

        )

    # ==================================================
    # GET ALL
    # ==================================================
    def get_all(self):

        return (

            self.db.query(
                PurchaseReturn
            )

            .order_by(
                PurchaseReturn.return_id.desc()
            )

            .all()

        )

    # ==================================================
    # GET BY PURCHASE
    # ==================================================
    def get_by_purchase(
        self,
        purchase_id: int
    ):

        return (

            self.db.query(
                PurchaseReturn
            )

            .filter(
                PurchaseReturn.purchase_id
                == purchase_id
            )

            .order_by(
                PurchaseReturn.return_id.desc()
            )

            .all()

        )

    # ==================================================
    # GET DRAFT BY PURCHASE
    # ==================================================
    def get_draft_by_purchase(
        self,
        purchase_id: int
    ):

        return (

            self.db.query(
                PurchaseReturn
            )

            .filter(

                PurchaseReturn.purchase_id
                == purchase_id,

                PurchaseReturn.status
                == "DRAFT"

            )

            .first()

        )

    # ==================================================
    # GET COMPLETED BY PURCHASE
    # ==================================================
    def get_completed_by_purchase(
        self,
        purchase_id: int
    ):

        return (

            self.db.query(
                PurchaseReturn
            )

            .filter(

                PurchaseReturn.purchase_id
                == purchase_id,

                PurchaseReturn.status
                == "COMPLETED"

            )

            .all()

        )

    # ==================================================
    # GET RETURNED PURCHASES
    # ==================================================
    def get_returned_purchases(self):

        return (

            self.db.query(
                PurchaseReturn.purchase_id
            )

            .distinct()

            .order_by(
                PurchaseReturn.purchase_id.desc()
            )

            .all()

        )
    
    

    # ==================================================
    # GET BY STATUS
    # ==================================================
    def get_by_status(
        self,
        status: str
    ):

        return (

            self.db.query(
                PurchaseReturn
            )

            .filter(
                PurchaseReturn.status
                == status
            )

            .order_by(
                PurchaseReturn.return_id.desc()
            )

            .all()

        )

    # ==================================================
    # UPDATE
    # ==================================================
    def update(
        self,
        purchase_return
    ):

        self.db.commit()

        self.db.refresh(
            purchase_return
        )

        return purchase_return

    # ==================================================
    # DELETE
    # ==================================================
    def delete(
        self,
        purchase_return
    ):

        self.db.delete(
            purchase_return
        )

        self.db.commit()

        return True