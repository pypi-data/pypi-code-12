import sys
import os

log_path = "logs"
if not os.path.exists(log_path):
    os.mkdir(log_path)

sys.stdout = open(os.path.join(log_path, "stdout.log"), "w")
sys.stderr = open(os.path.join(log_path, "stderr.log"), "w")

print("Logs in {}".format(log_path))

print("Starting DjangoServer")
from wsgiref.simple_server import make_server
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), "{{NAME}}"))


#----------------------------------------------------------------------
def django_wsgi_application():
    """"""
    print("Creating WSGI application...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{NAME}}.settings")
    application = get_wsgi_application()
    return application


#----------------------------------------------------------------------
def main():
    """"""
    httpd = make_server("127.0.0.1" , {{PORT}}, django_wsgi_application())
    httpd.serve_forever()
    print("Now serving on {}:{}".format(*httpd.server_address))


main()