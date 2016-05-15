def request_id(skaro):
    """Returns the new value for the "request id" key"""
    if len(skaro.sent_requests.keys()) > 0:
        max_key = 1
        for key in skaro.sent_requests.keys():
            if key > max_key:
                max_key = key
        return max_key + 1
    else:
        return 1
