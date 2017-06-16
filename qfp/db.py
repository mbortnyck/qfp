from __future__ import division
from bisect import bisect_left, bisect_right
from collections import defaultdict, namedtuple
from qfp.fingerprint import fpType
import numpy as np
import sqlite3
import math
import operator

try:
    from itertools import izip
except:
    izip = zip


class QfpDB:
    """
    Provides methods for storing reference fingerprints and
    querying the database with query fingerprints
    """

    def __init__(self, db_path='qfp.db'):
        self.path = db_path
        with sqlite3.connect(self.path) as conn:
            self._create_tables(conn)
        self._create_named_tuples()
        conn.close()

    def _create_tables(self, conn):
        """
        Creates necessary tables if they do not already exist
        in database. executescript will automatically commit
        these changes.
        """
        conn.executescript("""
            CREATE VIRTUAL TABLE
            IF NOT EXISTS Hashes USING rtree(
                id,
                minW, maxW,
                minX, maxX,
                minY, maxY,
                minZ, maxZ);
            CREATE TABLE
            IF NOT EXISTS Records(
                id INTEGER PRIMARY KEY,
                title TEXT);
            CREATE TABLE
            IF NOT EXISTS Quads(
                hashid INTEGER PRIMARY KEY,
                recordid INTEGER,
                Ax INTEGER, Ay INTEGER,
                Cx INTEGER, Cy INTEGER,
                Dx INTEGER, Dy INTEGER,
                Bx INTEGER, By INTEGER,
                FOREIGN KEY(hashid) REFERENCES Hashes(id),
                FOREIGN KEY(recordid) REFERENCES Records(id));
            CREATE TABLE
            IF NOT EXISTS Peaks(
                recordid INTEGER, X INTEGER, Y INTEGER,
                PRIMARY KEY(recordid, X, Y),
                FOREIGN KEY(recordid) REFERENCES Records(id));""")

    def _create_named_tuples(self):
        self.Peak = namedtuple('Peak', ['x', 'y'])
        self.Quad = namedtuple('Quad', ['A', 'C', 'D', 'B'])
        mcNames = ['offset', 'num_matches', 'sTime', 'sFreq']
        self.MatchCandidate = namedtuple('MatchCandidate', mcNames)

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
                self._store_peaks(c, fp, recordid)
                for qHash, qQuad in izip(fp.hashes, fp.strongest):
                    self._store_hash(c, qHash)
                    self._store_quad(c, qQuad, recordid)
        conn.commit()
        conn.close()

    def _record_exists(self, c, title):
        """
        Returns True/False depending on existence of a song title
        in the QfpDB
        """
        c.execute("""SELECT id
                       FROM Records
                      WHERE title = ?""", (title,))
        recordid = c.fetchone()
        if recordid is None:
            return False
        else:
            print("record already exists...")
            return True

    def _store_record(self, c, title):
        """
        Inserts a song title into the Records table, then
        returns its primary key.
        """
        c.execute("""INSERT INTO Records
                     VALUES (null,?)""", (title,))
        return c.lastrowid

    def _store_peaks(self, c, fp, recordid):
        """
        Stores peaks from reference fingerprint
        """
        for x, y in fp.peaks:
            c.execute("""INSERT INTO Peaks
                         VALUES (?,?,?)""", (recordid, x, y))

    def _store_hash(self, c, h):
        """
        Inserts given hash into QfpDB's Hashes table
        """
        c.execute("""INSERT INTO Hashes
                     VALUES (null,?,?,?,?,?,?,?,?)""",
                  (h[0], h[0], h[1], h[1], h[2], h[2], h[3], h[3]))

    def _store_quad(self, c, q, recordid):
        """
        Inserts given quad into the Quads table
        """
        hashid = c.lastrowid
        values = (hashid, recordid, q.A.x, q.A.y, q.C.x, q.C.y,
                  q.D.x, q.D.y, q.B.x, q.B.y)
        c.execute("""INSERT INTO Quads
                     VALUES (?,?,?,?,?,?,?,?,?,?)""", values)
    """
    QUERYING DB
    """

    def query(self, fp, vThreshold=0):
        """
        Queries database for a given query fingerprint
        """
        if fp.fp_type != fpType.Query:
            raise TypeError("May only query db with query fingerprints")
        fp.match_candidates = self._match_candidates(fp)
        #self.verified = self._verify_candidates(self.match_candidates)

        """
        self.histogram = self._create_histogram(self.match_candidates)
        self.counts = {k:len(v) for k,v in self.results.items()}
        self.counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=1)
        for count in self.counts:
            recordid = count[0]
            self.hist = self._create_histogram(self.results[recordid])
            for off in self.hist:
                self.rPeaks = self._lookup_peak_range(c, recordid, off[0])
                vScore = self._verify_peaks(off[0], self.rPeaks, fp.peaks)
                if vScore >= vThreshold:
                    print "POSSIBLE MATCH: %s (%f) at %f seconds" % (self._lookup_record(conn, recordid), vScore, (off[0]*4/1000.))
        conn.close()"""

    def _match_candidates(self, fp):
        """
        glurg
        """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        filtered = defaultdict(list)
        for qHash, qQuad in izip(fp.hashes, fp.strongest):
            self._radius_nn(c, qHash)
            with np.errstate(divide='ignore', invalid='ignore'):
                self._filter_candidates(conn, c, qQuad, filtered)
        binned = {k: self._bin_times(v) for k, v in filtered.items()}
        results = {k: self._scales(v)
                   for k, v in binned.items() if len(v) >= 4}
        c.close()
        conn.close()
        return results.items()

    def _radius_nn(self, c, h, e=0.01):
        """
        Epsilon (e) neighbor search for a given hash. Matching hash ids
        can be retrieved from the cursor.
        """
        c.execute("""SELECT id FROM Hashes
                      WHERE minW >= ? AND maxW <= ?
                        AND minX >= ? AND maxX <= ?
                        AND minY >= ? AND maxY <= ?
                        AND minZ >= ? AND maxZ <= ?""",
                  (h[0] - e,       h[0] + e,
                   h[1] - e,       h[1] + e,
                   h[2] - e,       h[2] + e,
                   h[3] - e,       h[3] + e))

    def _filter_candidates(self, conn, c, qQuad, results, e=0.2, eFine=1.8):
        """
        Performs three tests on potential matching quads. Quads that pass
        these tests are added to the results dictionary.
        """
        for hashid in c:
            cQuad, recordid = self._lookup_quad(conn, hashid)
            # Rough pitch coherence:
            #   1/(1+e) <= queAy/canAy <= 1/(1-e)
            if not 1 / (1 + e) <= qQuad.A.y / cQuad.A.y <= 1 / (1 - e):
                continue
            # X transformation tolerance check:
            #   sTime = (queBx-queAx)/(canBx-canAx)
            sTime = (qQuad.B.x - qQuad.A.x) / (cQuad.B.x - cQuad.A.x)
            if not 1 / (1 + e) <= sTime <= 1 / (1 - e):
                continue
            # Y transformation tolerance check:
            #   sFreq = (queBy-queAy)/(canBy-canAy)
            sFreq = (qQuad.B.y - qQuad.A.y) / (cQuad.C.y - cQuad.a.Y)
            if not 1 / (1 + e) <= sFreq <= 1 / (1 - e):
                continue
            # Fine pitch coherence:
            #   |queAy-canAy*sFreq| <= eFine
            if not abs(qQuad.A.y - (cQuad.a.Y * sFreq)) <= eFine:
                continue
            offset = cQuad.A.x - (qQuad.A.x / sTime)
            results[recordid].append((offset, (sTime, sFreq)))

    def _lookup_quad(self, conn, hashid):
        """
        Returns quad and recordid of a given hashid
        """
        c = conn.cursor()
        c.execute("""SELECT Ax,Ay,Cx,Cy,Dx,Dy,Bx,By,recordid FROM Quads
                      WHERE hashid=?""", hashid)
        r = c.fetchone()
        c.close()
        quad = self.Quad((r[0], r[1]), (r[2], r[3]),
                         (r[4], r[5]), (r[6], r[7]))
        recordid = r[8]
        return quad, recordid

    def _bin_times(self, l, binwidth=20, ts=4):
        """
        Takes list of rough offsets and bins them in time increments of
        binwidth. These offsets are stored in a dictionary of
        {binned time : [list of scale factors]}. Binned time keys with
        less than Ts scale factor values are filtered out.
        """
        d = defaultdict(list)
        for rough_offset in l:
            div = rough_offset[0] / binwidth
            binname = int(math.floor(div) * binwidth)
            d[binname].append((rough_offset[1][0], rough_offset[1][1]))
        return {k: v for k, v in d.items() if len(v) >= ts}

    def _scales(self, d):
        """
        Receives dictionary of {binned time : [scale factors]}
        Performs variance-based outlier removal on these scales. If 4 or more
        matches remain after outliers are removed, a list with form
        [(rough offset, num matches, scale averages)]] is created. This result
        is sorted by # of matches in descending order and returned.
        """
        o_rm = {k: self._outlier_removal(v) for k, v in d.items()}
        res = [(i[0], len(i[1]), np.mean(i[1], axis=0))
               for i in o_rm.items() if len(i[1]) >= 4]
        sorted_mc = sorted(res, key=operator.itemgetter(1), reverse=True)
        return sorted_mc

    def _outlier_removal(self, d):
        """
        Calculates mean/std. dev. for sTime/sFreq values,
        then removes any outliers (defined as mean +/- 2 * stdv).
        Returns list of final means.
        """
        means = np.mean(d, axis=0)
        stds = np.std(d, axis=0)
        d = [v for v in d if
             (means[0] - 2 * stds[0] <= v[0] <= means[0] + 2 * stds[0]) and
             (means[1] - 2 * stds[1] <= v[1] <= means[1] + 2 * stds[1])]
        return d

    def _validate_match(self, fp, c, recordid, offset):
        """
        """
        rPeaks = self._lookup_peak_range(c, recordid, offset)
        vScore = self._verify_peaks(rPeaks, fp.peaks)

    def _lookup_peak_range(self, c, recordid, offset, e=3750):
        """
        Queries Peaks table for peaks of given recordid that are within
        3750 samples (15s) of the estimated offset value.
        """
        data = (offset, offset + e, recordid)
        c.execute("""SELECT X, Y
                       FROM Peaks
                      WHERE X >= ? AND X <= ?
                        AND recordid = ?""", data)
        return c.fetchall()

    def _verify_peaks(self, offset, rPeaks, qPeaks, eX=18, eY=12):
        """
        Checks for presence of a given set of reference peaks in the
        query fingerprint's list of peaks according to time and
        frequency boundaries (eX and eY). Each reference peak is adjusted
        according to estimated sFreq/sTime from candidate filtering
        stage.
        Returns: validation score (num. valid peaks / total peaks)
        """
        validated = 0
        for rPeak in rPeaks:
            rPeak = (rPeak[0] - offset, rPeak[1])
            lBound = bisect_left(qPeaks, (rPeak[0] - eX, None))
            rBound = bisect_right(qPeaks, (rPeak[0] + eX, None))
            for i in xrange(lBound, rBound):
                if not rPeak[1] - eY <= qPeaks[i][1] <= rPeak[1] + eY:
                    # print "yFail: ", rPeak[1] - eY, qPeaks[i][1], rPeak[1] + eY
                    continue
                else:
                    validated += 1
        vScore = (float(validated) / len(rPeaks))
        return vScore

    def _lookup_record(self, conn, recordid):
        """
        Returns title of given recordid
        """
        c = conn.execute("""SELECT title
                              FROM Records
                             WHERE id = ?""", (recordid,))
        title = c.fetchone()
        c.close()
        return title[0]
