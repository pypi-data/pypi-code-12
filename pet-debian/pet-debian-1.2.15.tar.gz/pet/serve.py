import pet.web
from serve import pet_serve
import paste.httpserver

class Asdf():
    def pet_serve():
        app = pet.web.main()
        paste.httpserver.serve(app, host='0.0.0.0')

def pet_serve():
    app = pet.web.main()
    paste.httpserver.serve(app, host='0.0.0.0')
