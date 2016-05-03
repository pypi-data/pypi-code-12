import datetime
import argparse
import sys
import flask
import os
import re
import time
import json
import pdb
import random
import tempfile
import traceback
from collections import *

import click
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

sys.path.insert(0, os.path.abspath(""))
from config import *


engine = create_engine(dburi)

def index(db):
  cur = db.execute("SELECT paper_name, count(distinct commit_id) as count FROM papers GROUP BY paper_name")
  ds = [dict(zip(cur.keys(), row)) for row in cur]
  return render_template("index.html", papers=ds)



def paper(db, paper_name):
  cur = db.execute("""
    SELECT paper_name, commit_id, max(tstamp) as tstamp, pdfpath, max(imgpath) as imgpath, imgidx
    FROM papers
    WHERE paper_name = ?
    GROUP BY paper_name, commit_id, pdfpath, imgidx
    order by max(tstamp) desc, pdfpath, imgidx
    """, 

    (paper_name,))
  ds = [dict(zip(cur.keys(), row)) for row in cur]
  for d in ds:
    d['pdfurl'] = "/pdfs/%s" % (os.path.basename(d['pdfpath']))
    d['imgurl'] = "/imgs/%s" % (os.path.basename(d['imgpath']))
    dt = datetime.datetime.strptime(d['tstamp'], '%Y-%m-%d %H:%M:%S')
    d['tstamp'] = dt.strftime("%m-%d-%y %I:%M %p")


  commits = []
  for d in ds:
    if len(commits) == 0 or commits[-1]['commit_id'] != d['commit_id']:
      commits.append(dict(d))
      commits[-1]['imgs'] = []
    commits[-1]['imgs'].append(d['imgurl'])

  return render_template("paper.html", commits=commits)



def create_app(app):

  @app.before_request
  def before_request():
    try:
      g.conn = engine.connect()
    except:
      traceback.print_exc()
      g.conn = None

  @app.teardown_request
  def teardown_request(exception):
    try:
      if hasattr(g, 'conn'):
        g.conn.close()
    except Exception as e:
      print(e)
      pass


  @app.route('/', methods=["POST", "GET"])
  def app_index():
    return index(g.conn)

  @app.route('/<paper_name>/')
  def app_paper(paper_name):
    return paper(g.conn, paper_name)

def run_server(HOST='localhost', PORT=8000,  threaded=False, debug=True):
  CURDIR = os.path.dirname(os.path.abspath(__file__))
  tmpl_dir = os.path.join(CURDIR, 'templates')
  static_dir = os.path.join(CURDIR, 'static')
  print(tmpl_dir)
  app = Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir)
  create_app(app)

  print("Point your browser to: http://%s:%d" % (HOST, PORT))
  app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


