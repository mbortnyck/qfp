# This Python file uses the following encoding: utf-8

import itertools

def root_quads(root, peaks, q, r, n, k):
    """
    finds valid quads for given root
    """
    quads = []
    filtered = _filter_peaks(root, peaks, r, k)
    if filtered is None:
        return []
    found = _find_quads(root, filtered, q, n)
    if found is not None:
        quads += found
    return quads

def _filter_peaks(root, peaks, r, k):
    """
    returns peaks inside window of Ax + k ± (r / 2)
    """
    lastPeak = peaks[-1][0]
    windowStart = root[0] + k - (r / 2)
    if windowStart > lastPeak:
        return None
    windowEnd = windowStart + r
    filtered = [x for x in peaks if x[0] >= windowStart and x[0] <= windowEnd]
    if len(filtered) is 0:
        return None
    return filtered

def _find_quads(root, filtered, q, n):
    """
    returns list of validated quads for given root (A)
    """
    validQuads = []
    offset = 0
    while len(validQuads) < q and offset + n <= len(filtered):
        take = filtered[offset : offset + n]
        combs = list(itertools.combinations(take, 3))
        for comb in combs:
            # note that B is defined as point farthest from A
            A, B, C, D = (root, comb[2], comb[0], comb[1])
            if _validate_quad(A, B, C, D, validQuads):
                validQuads += [[A, B, C, D]]
            if len(validQuads) >= q:
                break
        offset += 1
    if len(validQuads) is 0:
        return None
    else:
        return validQuads

def _validate_quad(A, B, C, D, quads):
    """
    evaluates:
          Ax < Bx
          Ay < By
      Ax < Cx,Dx <= Bx
      Ay < Cy,Dy <= By

    then checks if quad is a duplicate
    """
    # !! assumes combinations are sorted by x value
    # (default behavior of itertools.combinations)
    if A[0] is B[0] or A[0] is C[0]:
        return False
    elif A[1] >= B[1] or A[1] >= C[1] or A[1] >= D[1]:
        return False
    elif C[1] > B[1] or D[1] > B[1]:
        return False
    for quad in quads:
        if [A, B, C, D] == quad:
            return False
    return True