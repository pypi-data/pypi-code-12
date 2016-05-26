import sys

from flask import Flask

app = Flask(__name__)


@app.route('/<int:code>')
def hello_world(code):
    return str(code), code


def run():
    if len(sys.argv) < 2:
        print("Use port to specify server port: %s port" % sys.argv[0])
        port = 8333
    else:
        port = int(sys.argv[1])
    app.run(port=port)

if __name__ == '__main__':
    run()
