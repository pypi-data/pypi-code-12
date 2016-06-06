import sys
import os
import time
import difflib
from datetime import datetime

import click
import Levenshtein as lev
from sqlalchemy import create_engine
from git import Repo
from wand.image import Image, FILTER_TYPES
from wand.color import Color


sys.path.insert(0, os.path.abspath(""))
from config import *

_filedir_ = os.path.dirname(os.path.abspath(__file__))
ROOT = _filedir_
PDFROOT = os.path.join(ROOT, 'static/pdfs')
IMGROOT = os.path.join(ROOT, 'static/imgs')
os.system("mkdir -p %s" % PDFROOT)
os.system("mkdir -p %s" % IMGROOT)




def save_record(db, row, paper_name, commit, dt, commit_idx):
  q = """INSERT INTO papers VALUES(?, ?, ?, ?, ?, ?, ?)"""
  db.execute(q, (paper_name, str(commit), commit_idx, dt, row['pdfpath'], row['imgpath'], row['imgidx']))

def init_db(dburi):
  db = create_engine(dburi)
  try:
    q = """CREATE TABLE IF NOT EXISTS papers(
      paper_name text,
      commit_id text,
      commit_idx int,
      tstamp timestamp,
      pdfpath text,
      imgpath text,
      imgidx int
    )"""
    db.execute(q)
  except Exception as e:
    print e
  return db



def proc_diffidx(diffidx, latex_dir):
  dists = []
  for diff in diffidx:
    dists.append(proc_diff(diff, latex_dir))
  dists = filter(bool, dists)
  if dists:
    return sum(dists)
  return 0

def proc_diff(diff, latex_dir):
  if diff.a_blob and diff.b_blob and diff.a_blob.hexsha != diff.b_blob.hexsha:
    if not diff.a_path.endswith('.tex'): 
      return 0
    if not (latex_dir in diff.a_path or latex_dir in diff.b_path):
      return 0

    print diff.a_path

    filea = diff.a_blob.data_stream.read()
    fileb = diff.b_blob.data_stream.read()
    dist = lev.distance(filea, fileb)
    return dist


    if dist > 10:
      toprint = []
      for l in difflib.unified_diff(filea.split('\n'), fileb.split('\n')):
        if l.startswith('+') or l.startswith('-'):
          l = l[1:].strip().strip('+').strip('-')
          if l and not l.startswith('\\') and not l.startswith('%'):
            toprint.append(l)




def snapshot_latex(repo, commit, idx, paper_name, cmds_f, h=300):
  repo.git.checkout(commit, force=True)
  fout = "%s_%03d" % (paper_name, idx)
  fpath = os.path.join(PDFROOT, "%s.pdf" % fout)

  cmds = cmds_f(fpath)
  os.system(";".join(cmds))

  ds = screenshots(fpath)
  for d in ds:
    d['pdfpath'] = fpath
  return ds

def all_screenshots(pdfdir, h=200):
  ret = []
  for name in os.listdir(pdfdir):
    if name.endswith(".pdf"):
      fpath = os.path.join(pdfdir, name)
      ds = screenshots(fpath, h=h)
      for d in ds:
        d['pdfpath'] = fpath
      ret.extend(ds)
  return ret

def screenshots(pdfpath, h=200):
  #dirpath = os.path.join(os.path.dirname(os.path.dirname(pdfpath)), "imgs")
  dirpath = IMGROOT
  fprefix = os.path.splitext(os.path.basename(pdfpath))[0]
  print "screenshots for %s" % fprefix
  ret = []

  with Image(filename=pdfpath) as imgs:
    for imgidx, img in enumerate(imgs.sequence):
      w = int(h * img.width / img.height)
      tosave = Image(width=img.width, height=img.height, background=Color("white"))
      tosave.composite(img, 0, 0)
      tosave.convert('png')
      tosave.resize(w, h, filter='lagrange', blur=.35)

      imgname = "%s_%02d.png" % (fprefix, imgidx)
      imgpath = os.path.join(dirpath, imgname)
      tosave.save(filename=imgpath)

      ret.append(dict(
        imgpath=imgpath,
        imgidx=imgidx
      ))
  return ret


def proc_repo(db, repo, paper_name,  cmd_f=lambda: list(), latex_dir="", h=300):
  commits_list = list(repo.iter_commits())

  # skip to the latest commit that has not been analyzed
  cur = db.execute("""
      select commit_id from papers 
      where tstamp = (select min(tstamp) 
                      from papers where paper_name = ?) and 
            paper_name = ?""", 
      (paper_name, paper_name))
  rows = [row for row in cur]
  before = None
  idx = None
  if rows:
    commit_id = rows[0][0]
    idx = map(str, commits_list).index(commit_id)
    print idx, commit_id

  if idx is None:
    idx = 0
    before = commits_list[0]
    before_dt = datetime.fromtimestamp(time.mktime(time.gmtime(before.committed_date)))
    for o in snapshot_latex(repo, before, 0, paper_name, cmd_f, h=h):
      save_record(db, o, paper_name, before, before_dt, 0)
    print "saving record"

  before = commits_list[idx]

  dists = []
  while idx < len(commits_list) - 1:
    idx += 1
    after = commits_list[idx]

    timespan = abs(after.committed_date - before.committed_date)
    timespan = timespan / 1000. / 60 / 60
    if timespan <= min_hours_gap:
      continue

    before_dt = datetime.fromtimestamp(time.mktime(time.gmtime(before.committed_date)))
    after_dt = datetime.fromtimestamp(time.mktime(time.gmtime(after.committed_date)))
    print idx, after_dt.strftime("%m-%d-%y %H:%M")

    dist = proc_diffidx(before.diff(after), latex_dir)
    if dist > min_edit_distance:
      try:
        records = snapshot_latex(repo, after, idx, paper_name, cmd_f, h=h)
        for o in records:
          save_record(db, o, paper_name, after, after_dt, idx)
      except Exception as e:
        print e
        
      before = after


def proc_latex(h=300):
  repo = Repo(git_repo)
  assert not repo.bare
  repo.git.checkout("master", force=True)
  db = init_db(dburi)

  proc_repo(db, repo, paper_name=paper_name, cmd_f=make_cmds, latex_dir=latex_dir, h=h)

  repo.git.checkout('master', force=True)



