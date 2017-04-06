# This Python file uses the following encoding: utf-8

import itertools

def root_quads(root, peaks, q, r, c):
    """
    finds valid quads for given root
    """
    quads = []
    filtered = _filter_peaks(root, peaks, r, c)
    if filtered is None:
        return []
    found = _find_quads(root, filtered, q)
    if found is not None:
        quads += found
    return quads

def _filter_peaks(root, peaks, r, c):
    """
    returns peaks inside window of Ax + c ± (r / 2)
    """
    lastPeak = peaks[-1][0]
    windowStart = root[0] + c - (r / 2)
    if windowStart > lastPeak:
        return None 
    windowEnd = windowStart + r
    filtered = [x for x in peaks if x[0] >= windowStart and x[0] <= windowEnd]
    if len(filtered) is 0:
        return None
    return filtered

def _find_quads(root, filtered, q):
    """
    returns list of validated quads for given root (A)
    """
    validQuads = []
    while len(validQuads) < q:
        # combs = list(itertools.combinations(take, 3))
        for comb in itertools.combinations(take, 3):
            A, C, D, B = (root, comb[0], comb[1], comb[2])
            if _validate_quad(A, C, D, B, validQuads):
                validQuads += [[A, C, D, B]]
            if len(validQuads) >= q:
                break
        offset += 1
    if len(validQuads) is 0:
        return None
    else:
        return validQuads

def _validate_quad(A, C, D, B, quads):
    """
    Checks if quad is a duplicate

    Then evaluates:
          Ax < Bx
          Ay < By
      Ax < Cx,Dx <= Bx
      Ay < Cy,Dy <= By
    """
    # !! assumes combinations are sorted by x value
    # (default behavior of itertools.combinations)
    for quad in quads:
        if [A, C, D, B] == quad:
            return False
    if A[0] == B[0]:
        return False
    elif A[1] >= C[1] or A[1] >= D[1] or A[1] >= B[1]:
        return False
    elif B[1] >= C[1] or B[1] >= D[1] or C[1] >= D[1]:
        return False
    # what was this for?
    """elif (C[0] - B[0]) <= 8 or (C[1] - B[1]) <= 4:
        return False"""
    return True

def generate_hashes(quads):
    """
    Compute translation- and scale-invariant hash from a given quad
    Yields: tuple of four float64 values
    """
    for quad in quads:
        hashed = ()
        A = quad[0]
        D = quad[3]
        for point in quad[1:3]:
            xDash = (point[0] - A[0]) * (1.0 / (D[0] - A[0]))
            yDash = (point[1] - A[1]) * (1.0 / (D[1] - A[1]))
            hashed += (xDash, yDash)
        yield [hashed]