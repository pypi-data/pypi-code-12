from dragline.http.requests import Request, RequestError, RequestProcessor
from dragline import runtime
runtime.request_processor = RequestProcessor()
