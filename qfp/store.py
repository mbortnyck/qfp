from rtree import index

def bulk_load(hashes):
    """
    Generator function for storing hashes in rtree
    """
    i = 1
    for (minx, miny, maxx, maxy) in hashes:
        yield (i, (minx, miny, maxx, maxy), None)
        i += 1