import sys
import os
from sqlalchemy import *
from jinja2 import Template
import datetime

sys.path.insert(0, os.path.abspath(""))
from config import *


engine = create_engine(dburi)



def index(db, CURDIR):
  cur = db.execute("SELECT paper_name, count(distinct commit_id) as count FROM papers GROUP BY paper_name")
  ds = [dict(zip(cur.keys(), row)) for row in cur]
  for d in ds:
    d['paper_name'] = d['paper_name'] + '.html'
  print ds
  return render_template(os.path.join(CURDIR, "templates/index.html"), papers=ds)

def paper(db, paper_name, CURDIR):
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

  return render_template(os.path.join(CURDIR, "templates/paper.html"), commits=commits)

def render_template(template_path, **kwargs):
  template = Template(file(template_path).read())
  return template.render(**kwargs)


def export(outdir):
  CURDIR = os.path.dirname(os.path.abspath(__file__))
  tmpl_dir = os.path.join(CURDIR, 'templates')
  static_dir = os.path.join(CURDIR, 'static')

  os.system("mkdir -p %s" % outdir)
  os.system("mkdir -p %s" % os.path.join(outdir, 'html'))
  os.system("cp -r %s %s/" % (static_dir, outdir))
  db = engine.connect()
  with file(os.path.join(outdir, "html/index.html"), 'w') as f:
    f.write(index(db, CURDIR))


  cur = db.execute("select distinct paper_name from papers")
  papers = [row[0] for row in cur]
  for paper_name in papers:
    with file(os.path.join(outdir, "html/%s.html" % paper_name), 'w') as f:
      f.write(paper(db, paper_name, CURDIR))


