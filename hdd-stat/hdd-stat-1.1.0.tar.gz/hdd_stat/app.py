
from flask import Flask, json, Response
from hdd_stat.stat import get_labels, get_full_stat

app = Flask('hdd_stat')

@app.route('/')
def index():
    data = get_full_stat(get_labels())
    resp = Response(json.dumps([r._asdict() for r in data]))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# dev server
if __name__ == '__main__':
    app.run(host = '', port = 5000, debug = True)
