import sqlite3

from qfp.fingerprint import fpType

class QfpDB:
    """
    The QfpDB stores reference fingerprints'
    hashes, quads, and record information.
    """
    def __init__(self, db_path='qfp.db'):
        self.conn = sqlite3.connect(db_path)
        c = self.conn.cursor()
        self.create_db(c)
    def create_db(self, c):
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
            raise TypeError("May only store reference fingerprints in QfpDB")
        c = self.conn.cursor()
        c.execute('''INSERT INTO Records
                      VALUES (null,?)''', (title,))
        recordid = c.lastrowid
        for i in xrange(len(fp.strongest)):
            self.store_hash(c, fp.hashes[i])
            hashid = c.lastrowid
            self.store_quad(c, fp.strongest[i], hashid, recordid)
        self.conn.commit()
    def store_hash(self, c, h):
        """
        Inserts given hash into QfpDB's Hashes table
        """
        c.execute('''INSERT INTO Hashes
                     VALUES (null,?,?,?,?,?,?,?,?)''',
                     (h[0], h[0], h[1], h[1], h[2], h[2], h[3], h[3]))
    def store_quad(self, c, quad, hashid, recordid):
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
        if fp.fp_type != fpType.Query:
            raise TypeError("May only query db with query fingerprints")
        for h in fp.hashes:
            lookup_hash(h)
    def lookup_hash(self, h):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM Hashes
                           WHERE minW >= ? AND maxW <= ?
                             AND minX >= ? AND maxX <= ?
                             AND minY >= ? AND maxY <= ?
                             AND minZ >= ? AND maxZ <= ?''',
                                (h[0]-0.01,    h[0]+0.01,
                                 h[1]-0.01,    h[1]+0.01,
                                 h[2]-0.01,    h[2]+0.01,
                                 h[3]-0.01,    h[3]+0.01))
        return c