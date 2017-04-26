# This Python file uses the following encoding: utf-8
from __future__ import division

import itertools
from bisect import bisect_left, bisect_right

def find_quads(peaks, r, c):
    """
    Returns list of valid/strong quads for list of peaks
    """
    #quads = reduce(iadd, (_root_quads(root, peaks, r, c) for root in peaks))
    quads = []
    for root in peaks:
        quads += _root_quads(root, peaks, r, c)
    return quads

def _root_quads(root, peaks, r, c):
    """
    finds valid quads for given root
    """
    quads = []
    filtered = _filter_peaks(root, peaks, r, c)
    if filtered is None:
        return []
    found = _valid_quads(root, filtered)
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
    idx_start = bisect_left(peaks, (windowStart, None))
    idx_end = bisect_right(peaks, (windowEnd, None))
    filtered = peaks[idx_start:idx_end]
    if len(filtered) is 0:
        return None
    return filtered

def _valid_quads(root, filtered):
    """
    returns list of validated quads for given root (A)
    """
    validQuads = []
    for comb in itertools.combinations(filtered, 3):
        A, C, D, B = (root, comb[0], comb[1], comb[2])
        if _validate_quad(A, C, D, B, validQuads):
            validQuads += [[A, C, D, B]]
    if len(validQuads) is 0:
        return None
    else:
        return validQuads

def _validate_quad(A, C, D, B, quads):
    """
    Checks if quad is a duplicate

    Then evaluates:
          Ay < By
      Ax < Cx <= Dx <= Bx
      Ay < Cy ,  Dy <= By
    """
    # !! assumes combinations are sorted by x value
    # (default behavior of itertools.combinations)
    for quad in quads:
        if [A, C, D, B] == quad:
            return False
    if A[1] >= B[1] or A[1] >= D[1]:
        return False
    elif A[1] >= C[1] or C[1] >= B[1] or D[1] >= B[1]:
        return False
    return True