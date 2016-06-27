import web
import paste.httpserver

def pet_serve():
    app = web.main()
    paste.httpserver.serve(app, host='0.0.0.0')
