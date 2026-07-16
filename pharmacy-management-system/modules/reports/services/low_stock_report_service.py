class LowStockReportService:

    def __init__(
        self,
        report_repo
    ):
        self.report_repo = report_repo

    def get_low_stock(self):
        return self.report_repo.get_low_stock()