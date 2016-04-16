from django_cron import CronJobBase, Schedule
from rescuests.models import Request

class SendRequests(CronJobBase):
  RUN_EVERY_MINS = 1 # every minute

  schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
  code = 'rescuests.send_requests'    # a unique code

  def do(self):
    for request in Request.objects.filter(
      status__in = [Request.NEW, Request.RETRYING]):
      request.run()
