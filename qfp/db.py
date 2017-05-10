from __future__ import division
from qfp.fingerprint import fpType
import numpy as np
import sqlite3
import math

class QfpDB:
    """
    The QfpDB stores reference fingerprints'
    hashes, quads, and record information.
    """
    def __init__(self, db_path='qfp.db'):
        self.conn = sqlite3.connect(db_path)
        c = self.conn.cursor()
        self._create_tables(c)
    def _create_tables(self, c):
        c.executescript('''
            CREATE VIRTUAL TABLE 
            IF NOT EXISTS Hashes USING rtree(
                id,
                minW, maxW,
                minX, maxX,
                minY, maxY,
                minZ, maxZ);
            CREATE TABLE 
            IF NOT EXISTS Quads(
                quadid INTEGER PRIMARY KEY ASC,
                hashid INTEGER, recordid INTEGER,
                Ax INTEGER, Ay INTEGER,
                Cx INTEGER, Cy INTEGER,
                Dx INTEGER, Dy INTEGER,
                Bx INTEGER, By INTEGER,
                FOREIGN KEY(hashid) REFERENCES Hashes(id));
            CREATE TABLE
            IF NOT EXISTS Records(
                id INTEGER PRIMARY KEY ASC,
                title);''')
    """
    STORING FINGERPRINTS
    
    Usage example:
    db = QfpDB()
    db.store(fp, "Prince - Kiss")
    """
    def store(self, fp, title):
        """
        Stores a reference fingerprint in the db
        """
        if fp.fp_type != fpType.Reference:
            raise TypeError("May only store reference fingerprints in db")
        c = self.conn.cursor()
        c.execute('''INSERT INTO Records
                     VALUES (null,?)''', (title,))
        recordid = c.lastrowid
        for i in xrange(len(fp.strongest)):
            self._store_hash(c, fp.hashes[i])
            hashid = c.lastrowid
            self._store_quad(c, fp.strongest[i], hashid, recordid)
        self.conn.commit()
    def _store_hash(self, c, h):
        """
        Inserts given hash into QfpDB's Hashes table
        """
        c.execute('''INSERT INTO Hashes
                     VALUES (null,?,?,?,?,?,?,?,?)''',
                    (h[0], h[0], h[1], h[1], h[2], h[2], h[3], h[3]))
    def _store_quad(self, c, quad, hashid, recordid):
        """
        Inserts given quad into QfpDB's Quads table
        """
        c.execute('''INSERT INTO Quads
                     VALUES (null,?,?,?,?,?,?,?,?,?,?)''', (hashid, recordid,
                     quad[0][0], quad[0][1], quad[1][0], quad[1][1],
                     quad[2][0], quad[2][1], quad[3][0], quad[3][1]))
    """
    QUERYING DB

    Usage example:
    db = QfpDB()
    result = db.query(fp)
    """
    def query(self, fp):
        results = []
        c = self.conn.cursor()
        if fp.fp_type != fpType.Query:
            raise TypeError("May only query db with query fingerprints")
        for i in xrange(len(fp.hashes)):
            queQ = fp.strongest[i]
            c = self._find_candidates(fp.hashes[i])
            res= self._filter_candidates(c, queQ)
            print res
            results += res
        for r in results:
            print r
    def _find_candidates(self, h, e=0.01):
        c = self.conn.cursor()
        c.execute('''SELECT id FROM Hashes
                      WHERE minW >= ? AND maxW <= ?
                        AND minX >= ? AND maxX <= ?
                        AND minY >= ? AND maxY <= ?
                        AND minZ >= ? AND maxZ <= ?''',
                           (h[0]-e,       h[0]+e,
                            h[1]-e,       h[1]+e,
                            h[2]-e,       h[2]+e,
                            h[3]-e,       h[3]+e))
        return c
    def _filter_candidates(self, c, queQ, e=0.2, eFine=1.8):
        results = []
        for hashid in c.fetchall():
            canQ, recordid = self._lookup_quad(hashid)
            # Rough pitch coherence:
            #   1/(1+e) <= queAy/canAy <= 1/(1-e)
            if not 1/(1+e) <= queQ[0][1]/canQ[0][1] <= 1/(1-e):
                continue
            # X transformation tolerance check:
            #   sTime = (queBx-queAx)/(canBx-canAx)
            sTime = (queQ[3][0]-queQ[0][0])/(canQ[3][0]-canQ[0][0])
            if not 1/(1+e) <= sTime <= 1/(1-e):
                continue
            # Y transformation tolerance check:
            #   sFreq = (queBy-queAy)/(canBy-canAy)
            sFreq = (queQ[3][1]-queQ[0][1])/(canQ[3][1]-canQ[0][1])
            if not 1/(1+e) <= sFreq <= 1/(1-e):
                continue
            # Fine pitch coherence:
            #   |queAy-canAy*sFreq| <= eFine
            if not abs(queQ[0][1]-(canQ[0][1]*sFreq)) <= eFine:
                continue
            results += [(hashid, sTime, sFreq)]
        return results
    def _lookup_quad(self, hashid):
        c = self.conn.cursor()
        c.execute('''SELECT Ax,Ay,Cx,Cy,Dx,Dy,Bx,By,recordid FROM Quads
                      WHERE hashid=?''', hashid)
        r = c.fetchone()
        quad = [(r[0],r[1]),(r[2],r[3]),(r[4],r[5]),(r[6],r[7])]
        recordid = r[8]
        return quad, recordid