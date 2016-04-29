

from bookbank.core import app, db

def runserver():
    port = int(os.environ.get('PORT', 5000))
    bookbank.core.app.run(host='0.0.0.0', port=port)

