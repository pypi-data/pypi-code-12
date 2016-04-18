def internet_reachable():
    import socket
    import requests
    try:
        requests.get("http://google.com", timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, socket.timeout):
        return False
    return True
