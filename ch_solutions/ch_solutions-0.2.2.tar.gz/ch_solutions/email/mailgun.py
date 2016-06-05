import requests


class MGMail:
    def __init__(self, api_base, api_endpoint, api_key):
        # Set the Auth params
        self.api_base = api_base
        self.api_endpoint = api_endpoint
        self.api_key = api_key

        # declare all the stuff we could need
        self.from_address = None
        self.subject = None
        self.to_address = []
        self.cc_address = []
        self.bcc_address = []
        self.text = None
        self.html = None
        self.files = []

    def set_header(self, from_address, to_address, subject):
        self.from_address = from_address
        self.to_address = to_address
        self.subject = subject

    def add_cc(self, cc_address):
        self.cc_address.append(cc_address)

    def add_bcc(self, bcc_address):
        self.bcc_address.append(bcc_address)

    def add_text(self, text):
        self.text = text

    def add_html(self, html):
        self.html = html

    def add_attachment(self, file):
        self.files.append(("attachment", open(file)))

    def send_msg(self):
        return requests.post(
            "{0}{1}".format(self.api_base, self.api_endpoint),
            auth=("api", self.api_key),
            files=self.files,
            data={
                "from": self.from_address,
                "to": self.to_address,
                "cc": self.cc_address,
                "bcc": self.bcc_address,
                "subject": self.subject,
                "text": self.text,
                "html": self.html,
            }
        )






