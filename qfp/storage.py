from rtree import index

def bulk_load(hashes):
    """
    Generator function for storing hashes in rtree
    """
    hash_id = 1
    for (minx, miny, maxx, maxy) in hashes:
        yield (hash_id, (minx, miny, maxx, maxy), None)
        hash_id += 1