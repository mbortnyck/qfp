from rtree import index
from bitstring import pack

def bulk_load(hashes):
    """
    Generator function for storing hashes in rtree
    """
    hash_id = 1
    for (minx, miny, maxx, maxy) in hashes:
        yield (hash_id, (minx, miny, maxx, maxy), None)
        hash_id += 1

def pack_quad(quad):
    """
    Creates bitstring of length 90 for storage of quad
    Ax is stored as 20-bit uint, rest are stored as 10-bit uints
    Note: other x values are stored as offset from Ax to conserve space
    
    Format:
    00-20: Ax
    20-30: Ay
    30-40: Bx (offset from Ax)
    40-50: By
    50-60: Cx (offset from Ax)
    60-70: Cy
    70-80: Dx (offset from Ax)
    80-90: Dy
    """
    Format = 'uint:20' + (', uint:10' * 7)
    Ax, Ay = quad[0][0], quad[0][1]
    Bx, By = quad[1][0] - Ax, quad[1][1]
    Cx, Cy = quad[2][0] - Ax, quad[2][1]
    Dx, Dy = quad[3][0] - Ax, quad[3][1]
    bString = pack(Format, Ax, Ay, Bx, By, Cx, Cy, Dx, Dy)
    return bString

def unpack_quad(bString):
    """
    Unpacks quad from 90-bit bitstring
    """
    Format = 'uint:20' + (', uint:10' * 7)
    Ax, Ay, Bx, By, Cx, Cy, Dx, Dy = bString.unpack(Format)
    return [(Ax, Ay), (Bx + Ax, By), (Cx + Ax, Cy), (Dx + Ax, Dy)]