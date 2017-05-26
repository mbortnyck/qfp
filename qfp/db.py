from __future__ import division
from collections import defaultdict
from qfp.fingerprint import fpType
import numpy as np
import sqlite3
import math
import operator

class QfpDB:
    """
    The QfpDB stores reference fingerprints'
    hashes, quads, and record information.
    """
    def __init__(self, db_path='qfp.db'):
        self.path = db_path
        with sqlite3.connect(self.path) as conn:
            self._create_tables(conn)
        conn.close()
    def _create_tables(self, conn):
        """
        Creates necessary tables if they do not already exist
        in database. executescript will automatically commit
        these changes.
        """
        conn.executescript('''
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
                title,
                UNIQUE(title));''')
    """
    STORING FINGERPRINTS
    """
    def store(self, fp, title):
        """
        Stores a reference fingerprint in the db
        """
        if fp.fp_type != fpType.Reference:
            raise TypeError("May only store reference fingerprints in db")
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            if not self._record_exists(c, title):
                recordid = self._store_record(c, title)
                for i in xrange(len(fp.strongest)):
                    self._store_hash(c, fp.hashes[i])
                    self._store_quad(c, fp.strongest[i], recordid)
        conn.commit()
        conn.close()
    def _record_exists(self, c, title):
        """
        Returns True/False depending on existence of a song title
        in the QfpDB
        """
        c.execute('''SELECT id 
                       FROM Records
                      WHERE title = ?''', (title,))
        recordid = c.fetchone()
        if recordid is None:
            return False
        else:
            return True
    def _store_record(self, c, title):
        """
        Inserts a song title into the Records table, then
        returns its primary key.
        """
        c.execute('''INSERT INTO Records
                     VALUES (null,?)''', (title,))
        return c.lastrowid
    def _store_hash(self, c, h):
        """
        Inserts given hash into QfpDB's Hashes table
        """
        c.execute('''INSERT INTO Hashes
                     VALUES (null,?,?,?,?,?,?,?,?)''',
                    (h[0], h[0], h[1], h[1], h[2], h[2], h[3], h[3]))
    def _store_quad(self, c, quad, recordid):
        """
        Inserts given quad into the Quads table
        """
        hashid = c.lastrowid
        c.execute('''INSERT INTO Quads
                     VALUES (null,?,?,?,?,?,?,?,?,?,?)''', (hashid, recordid,
                     quad[0][0], quad[0][1], quad[1][0], quad[1][1],
                     quad[2][0], quad[2][1], quad[3][0], quad[3][1]))
    """
    QUERYING DB
    """
    def query(self, fp):
        """
        Queries database for a given query quad
        """
        if fp.fp_type != fpType.Query:
            raise TypeError("May only query db with query fingerprints")
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            self.results = defaultdict(list)
            self.counts = defaultdict(int)
            for i in xrange(len(fp.hashes)):
                qHash = fp.hashes[i]
                qQuad = fp.strongest[i]
                self._find_candidates(c, qHash)
                self._filter_candidates(conn, c, qQuad)
        self.counts = sorted(self.counts.items(), key=operator.itemgetter(1), reverse=True)
        for count in self.counts:
            hist = self._create_histogram(self.results[count[0]])
            print hist
        #self.histogram = self._create_histogram(self.results)
        #self.match_candidates = (x for x in self.histogram if x[1] >= 4)
        conn.close()
    def _find_candidates(self, c, h, e=0.01):
        """
        Epsilon (e) neighbor search for a given hash. Matching hash ids
        can be retrieved from the cursor.
        """
        c.execute('''SELECT id FROM Hashes
                      WHERE minW >= ? AND maxW <= ?
                        AND minX >= ? AND maxX <= ?
                        AND minY >= ? AND maxY <= ?
                        AND minZ >= ? AND maxZ <= ?''',
                           (h[0]-e,       h[0]+e,
                            h[1]-e,       h[1]+e,
                            h[2]-e,       h[2]+e,
                            h[3]-e,       h[3]+e))
    def _filter_candidates(self, conn, c, queQ, e=0.2, eFine=1.8):
        """
        Performs three tests on potential matching quads. Quads that pass
        these tests are added to the results dictionary.
        Counts is used to determine order of candidate recordid validation
        (we want to start the next step, validation, with the record with
        the greatest number of possible matches).
        """
        for hashid in c:
            canQ, recordid = self._lookup_quad(conn, hashid)
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
            normal = (queQ[0][0]/sTime)
            self.results[recordid].append(canQ[0][0]-normal)
            self.counts[recordid] += 1
    def _lookup_quad(self, conn, hashid):
        c = conn.cursor()
        c.execute('''SELECT Ax,Ay,Cx,Cy,Dx,Dy,Bx,By,recordid FROM Quads
                      WHERE hashid=?''', hashid)
        r = c.fetchone()
        quad = [(r[0],r[1]),(r[2],r[3]),(r[4],r[5]),(r[6],r[7])]
        recordid = r[8]
        return quad, recordid
    def _create_histogram(self, results, binwidth=20, ts=4):
        counts = defaultdict(int)
        for val in results:
           binname = int(math.floor(val/binwidth)*binwidth)
           counts[binname] += 1
        sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
        gt_ts = [x for x in sorted_counts if x[1] >= ts]
        return gt_ts