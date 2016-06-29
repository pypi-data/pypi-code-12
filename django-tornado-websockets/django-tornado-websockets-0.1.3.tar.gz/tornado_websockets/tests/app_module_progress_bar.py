from tornado_websockets.modules.progress_bar import ProgressBar
from tornado_websockets.websocket import WebSocket

ws_pb = WebSocket('my_progress_bar', False)
app_progress_bar_test = ProgressBar(ws_pb)

ws_ipb = WebSocket('my_indeterminate_progress_bar', False)
app_progress_bar_indeterminate_test = ProgressBar(ws_ipb, min=0, max=0)
