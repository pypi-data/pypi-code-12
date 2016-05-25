import uuid, requests
from django.db import models
from django.utils import timezone
from django.conf import settings
from signals import request_done, request_failed

class Request(models.Model):
  NEW, RUNNING, RETRYING, FAILED, READY = range(5)
  STATUS = [
    (NEW, "New"),
    (RUNNING, "Running"),
    (RETRYING, "Retrying"),
    (FAILED, "Failed"),
    (READY, "Ready"),
  ]

  MOCK_REQUESTS_SETTING = "RESCUESTS_MOCK_REQUESTS"
  MOCK_STATUS_SETTING = "RESCUESTS_MOCK_STATUS"
  MOCK_FUNC_SETTING = "RESCUESTS_MOCK_FUNC"
  MOCK_CONTENT_SETTING = "RESCUESTS_MOCK_CONTENT"


  uuid = models.CharField(verbose_name='UUID', max_length = 127, default = uuid.uuid4)
  url = models.URLField(verbose_name='URL')
  max_retries = models.PositiveIntegerField(default = 3)
  retries = models.PositiveIntegerField(default = 0)
  last_try = models.DateTimeField(null = True, blank = True)
  status = models.PositiveIntegerField(choices = STATUS, default = NEW)

  comment = models.TextField(blank = True)

  class mock():
    def __init__(self, func, status = 200, content = None):
      self.func = func
      self.status = status
      self.content = content
      self.saved_requests_setting = False
      self.saved_func_setting = None
      self.saved_content_setting = None
      self.saved_status_setting = 200

    def __enter__(self):
      self.saved_requests_setting = getattr(settings, Request.MOCK_REQUESTS_SETTING, False)
      self.saved_func_setting = getattr(settings, Request.MOCK_FUNC_SETTING, None)
      self.saved_content_setting = getattr(settings, Request.MOCK_CONTENT_SETTING, None)
      self.saved_status_setting = getattr(settings, Request.MOCK_STATUS_SETTING, 200)

      setattr(settings, Request.MOCK_REQUESTS_SETTING, True)
      setattr(settings, Request.MOCK_FUNC_SETTING, self.func)
      setattr(settings, Request.MOCK_CONTENT_SETTING, self.content)
      setattr(settings, Request.MOCK_STATUS_SETTING, self.status)

    def __exit__(self, *args):
      setattr(settings, Request.MOCK_REQUESTS_SETTING, self.saved_requests_setting)
      setattr(settings, Request.MOCK_FUNC_SETTING, self.saved_func_setting)
      setattr(settings, Request.MOCK_CONTENT_SETTING, self.saved_content_setting)
      setattr(settings, Request.MOCK_STATUS_SETTING, self.saved_status_setting)


  def __failed(self, response, error):
    self.comment += str(error) + "\n"
    self.retries += 1
    self.status = Request.FAILED if self.retries > self.max_retries else Request.RETRYING
    self.save()
    request_failed.send(sender = Request, instance = self, response = response, error = error)

  def __succeded(self, response):
    self.status = Request.READY
    self.save()
    request_done.send(sender = Request, instance = self, response = response)

  def run(self):
    if self.status in [Request.READY, Request.FAILED]: return
    self.status = Request.RUNNING
    self.last_try = timezone.now()
    self.save()

    if getattr(settings, Request.MOCK_REQUESTS_SETTING, False):
      return self.mock_request()

    try:
      response = requests.get(self.url)
      response.raise_for_status()
    except Exception, e:
      self.__failed(response, e)
    else:
      self.__succeded(response)
    finally:
      self.save()

  def mock_request(self):
    status = getattr(settings, Request.MOCK_STATUS_SETTING, 200)
    return_func = getattr(settings, Request.MOCK_FUNC_SETTING, None)
    return_content = getattr(settings, Request.MOCK_CONTENT_SETTING, None)

    if status not in [200, 403, 404, 500]:
      raise ValueError("currently only 200, 403, 404, 500 status "
        "codes are supported")

    if return_func is None:
      raise ValueError("if you trying to mock requests, "
        "please provide a \"RESCUESTS_MOCK_FUNC\" in your settings, "
        "which will be called instead of the HTTP requests")
    elif isinstance(return_func, str):
      module, _, func = return_func.rpartition(".")
      return_func = getattr(__import__(module, fromlist = [""]), func)

    return_func(status, self.url)

    if status == 200:
      self.__succeded(self.mock_response(status, return_content))
    else:
      self.__failed(self.mock_response(status, return_content), Exception("mocked exception"))

    self.save()

  def mock_response(self, status, content):
    resp = requests.Response()
    resp.status_code = status
    resp._content = content(self) if callable(content) else content
    return resp
