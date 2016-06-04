#!/usr/bin/env python
"""Provides datastore access."""
import os
import sqlite3
from OpenSSL import crypto
from . import DataStoreError


class DataStore(object):
    def __init__(self, dbpath, confpath):
        self.dbpath = dbpath
        self.confpath = confpath

    def initialize_store(self):
        """Initializes the store, throws DataStoreError if there is something wrong."""
        try:
            self._connect()
        except sqlite3.OperationalError as exc:
            raise DataStoreError("unable to connect to database '{}': {}".format(self.dbpath, exc.message))

        if not os.access(self.dbpath, os.W_OK):
            raise DataStoreError("unable to write to database '{}'".format(self.dbpath))

        if not os.access(self.confpath, os.R_OK):
            raise DataStoreError("unable to read conf file '{}'".format(self.confpath))

    def add_certificate(self, issuer_nickname, profile_nickname, cert, status, cert_type):
        """Adds a certificate to the datastore."""
        sql = """INSERT INTO certificates(cert_type, status, key_type, key_size, not_before, not_after, version,
            serial_number, issuer_nickname, profile_nickname, subject_cn, subject_ou, subject_o, subject_c, subject_st,
            subject_l, subject_e) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        #if cert.get_pubkey().type() != crypto.TYPE_RSA:
        #    raise DataStoreError("unknown key type")
        key_type = "rsa"
        serial_number = str(cert.get_serial_number())

        # insert
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, (cert_type, status, key_type, cert.get_pubkey().bits(), cert.get_notBefore(),
                    cert.get_notAfter(), cert.get_version(), serial_number, issuer_nickname, profile_nickname,
                    cert.get_subject().CN, cert.get_subject().OU, cert.get_subject().O, cert.get_subject().C,
                    cert.get_subject().ST, cert.get_subject().L, cert.get_subject().emailAddress))
        except sqlite3.IntegrityError:
            raise DataStoreError("serial number already exists in the datastore""")

    def get_certificate(self, serial_number):
        """Returns a dictionary of the certificate data in the datastore or None."""
        sql = """SELECT * FROM certificates WHERE serial_number = ?"""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, (str(serial_number),))
            row = cur.fetchone()
            if row:
                return dict(row)
            else:
                return None
    
    def get_issuer(self, nickname):
        """Returns a dictionary of the issuer data in the datastore or None."""
        sql = """SELECT * FROM certificates WHERE profile_nickname = ?"""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, (str(nickname),))
            row = cur.fetchone()
            if row:
                return dict(row)
            else:
                return None

    def revoke_certificate(self, serial_number):
        """Changes the status of the certificate to revoked."""
        sql = "UPDATE certificates SET status = 'revoked' WHERE serial_number = ?"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (str(serial_number),))

    def list_certificates(self, issuer_nickname=None, profile_nickname=None):
        """Returns a list of cert dicts for all certs, certs issued by issuer_nickname, or certs for profile_nickname."""
        results = []
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            if issuer_nickname:
                sql = """SELECT * FROM certificates WHERE issuer_nickname = ?"""
                cur.execute(sql, (issuer_nickname,))
            elif profile_nickname:
                sql = """SELECT * FROM certificates WHERE profile_nickname = ?"""
                cur.execute(sql, (profile_nickname,))
            else:
                sql = """SELECT * FROM certificates"""
                cur.execute(sql)

            rows = cur.fetchall()
            for row in rows:
                results.append(dict(row))
        return results

    def remove_certificate(self, serial_number):
        """Removes the certificate from the datastore."""
        sql = "DELETE FROM certificates WHERE serial_number = ?"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (str(serial_number),))

    def load_conf_str(self):
        """Returns the JSON string for the conf file."""
        try:
            with open(self.confpath, "r") as f:
                return f.read()
        except IOError as exc:
            raise DataStoreError("unable to read conf file '{}': {}".format(confpath, exc.strerror))

    def _connect(self):
        """Returns a database connection for the datastore."""
        if os.path.isfile(self.dbpath):
            return sqlite3.connect(self.dbpath)
        else:
            conn = sqlite3.connect(self.dbpath)
            DataStore._create_tables(conn)
            return conn

    @classmethod
    def _create_tables(cls, conn):
        """Creates the tables for the datastore."""
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE certificates(
                id INTEGER PRIMARY KEY,
                cert_type TEXT NOT NULL,
                status TEXT NOT NULL,
                key_type TEXT NOT NULL,
                key_size INT NOT NULL,
                not_before DATETIME NOT NULL,
                not_after DATETIME NOT NULL,
                version INT NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                issuer_nickname TEXT NOT NULL,
                profile_nickname TEXT NOT NULL,
                subject_cn TEXT,
                subject_ou TEXT,
                subject_o TEXT,
                subject_c TEXT,
                subject_st TEXT,
                subject_l TEXT,
                subject_e TEXT);""")
