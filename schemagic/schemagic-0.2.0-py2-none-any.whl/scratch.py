from functools import partial

from flask import Flask

from schemagic.web import service_route, service_registry

app = Flask(__name__)

register_services = service_registry(app)

def home(*messages):
    return "Hello World"

def my_sum(*items):
    return sum(items)

register_services(
    dict(rule="/",
         input_schema=[str],
         fn=home),
    dict(rule="/sum",
         input_schema=[int],
         output_schema=[int],
         fn=my_sum)
)


if __name__ == '__main__':
    app.run(port=5000)