class ExpiryReportService:

  def __init__(self, report_repo):
    self.report_repo = report_repo

  def get_expired_batches(self):
    return self.report_repo.get_expired_batches()