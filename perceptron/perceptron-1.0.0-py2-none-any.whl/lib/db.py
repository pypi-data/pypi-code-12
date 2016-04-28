import sqlite3 as sqlite

class Database():
    def __init__(self):
        self.con=sqlite.connect('nn.db')
        self.droptables()
        self.maketables()

    def __del__(self):
        self.con.close()

    def droptables(self):
        self.con.execute('drop table if exists hiddens')
        self.con.execute('drop table if exists inputs')
        self.con.execute('drop table if exists outputs')
        self.con.commit()

    def maketables(self):
        self.con.execute('create table hiddens(key)')
        self.con.execute('create table inputs(fromid,toid,strength)')
        self.con.execute('create table outputs(fromid,toid,strength)')
        self.con.commit()
