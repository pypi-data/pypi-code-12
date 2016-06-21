import os
from cf_predict import create_app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(host=app.config['HOST'], port=app.config['PORT'])
