class FinalResult:
    def __init__(self, responses, complete=True, whois_server_available=True, server_list=None):
        self.responses = responses
        self.complete = complete
        self.whois_server_available = whois_server_available
        self.server_list = server_list
