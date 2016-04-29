from flask import Flask

app = Flask(__name__)
app.config.from_object('bookbank.settings.DevelopmentConfig')
app.url_map.strict_slashes = False

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response