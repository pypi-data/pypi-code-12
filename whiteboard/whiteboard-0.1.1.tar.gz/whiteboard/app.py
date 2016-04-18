
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, Response, request, redirect, abort, render_template, \
                  url_for, flash
from werkzeug.security import safe_join
import os
import re


app = Flask(__name__)
app.jinja_env.globals['today'] = datetime.today


@app.route('/')
def list():
    files = []
    for fname in os.listdir(app.config['NOTES_DIR']):
        path = path_for(fname)
        if path is not None and not fname.startswith('.'):
            t = os.path.getmtime(path)
            with open(path, 'rb') as f:
                files.append((fname, read_title(f), datetime.fromtimestamp(t)))
    files.sort(key=lambda x: x[2], reverse=True)
    return render_template('list.html', files=files)


@app.route('/', methods=['POST'])
def create():
    title = request.form.get('title', '')
    fname = re.sub(r'[^A-Za-z0-9\s]', '', title)
    fname = fname.lower().replace(' ', '-') + '.txt'
    path = path_for(fname, should_exist=False)
    if path is None:
        flash('That file exists')
        return redirect(url_for('.list'), code=303)
    with open(path, 'wb') as f:
        write_note(f, title, '')
    return redirect(url_for('.edit', fname=fname), code=303)


@app.route('/<fname>', methods=['GET', 'PUT'])
def edit(fname):
    path = path_for(fname)
    if path is None:
        abort(404)

    if request.method == 'GET':
        title, text = read_note(fname)
        return render_template('edit.html', title=title, text=text)

    with open(path, 'wb') as f:
        write_note(f, json_value('title'), json_value('text'))
    return Response(status=204)


def json_value(key):
    data = request.get_json()
    if data is None or not isinstance(data, dict):
        abort(400, 'Got %r for data' % data)
    elif key not in data or not isinstance(data[key], type(u'')):
        abort(400, '%s missing or bad type' % key)
    return data[key]


def path_for(fname, should_exist=True):
    path = safe_join(app.config['NOTES_DIR'], fname)
    if path is None or os.path.isfile(path) != should_exist:
        return None
    return path


def read_title(f):
    line = f.readline()
    if line.startswith(b'# ') and f.readline() == b'\n':
        return line[2:-1].decode('utf-8')
    return None


def read_note(fname):
    with open(path_for(fname), 'rb') as f:
        return read_title(f), f.read().decode('utf-8')


def write_note(f, title, text):
    if title:
        f.write(b'# ')
        f.write(title.encode('utf-8'))
        f.write(b'\n\n')
    f.write(text.encode('utf-8'))
