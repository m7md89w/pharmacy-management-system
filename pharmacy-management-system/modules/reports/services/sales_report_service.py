class SalesReportService:

    def __init__(
        self,
        report_repo
    ):
        self.report_repo = report_repo

    def get_summary(
        self,
        start_date=None,
        end_date=None
    ):
        return self.report_repo.get_summary(
            start_date,
            end_date
        )