class InventoryReportService:

    def __init__(
        self,
        report_repo
    ):
        self.report_repo = report_repo

    def get_summary(self):
        return self.report_repo.get_summary()