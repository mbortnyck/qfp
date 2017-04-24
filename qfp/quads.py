# This Python file uses the following encoding: utf-8
from __future__ import division

import itertools
from bisect import bisect_left
from heapq import nlargest

def find_quads(peaks, r, c):
    """
    """
    quads = []
    for root in peaks:
        quads += _root_quads(root, peaks, r, c)
    strong_quads = _n_strongest(quads)
    return strong_quads

def _root_quads(root, peaks, r, c):
    """
    finds valid quads for given root
    """
    quads = []
    filtered = _filter_peaks(root, peaks, r, c)
    if filtered is None:
        return []
    found = _find_quads(root, filtered)
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

def _find_quads(root, filtered):
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

def _find_partitions(quads, length=250):
    """
    Returns list of indices where partitions of 250 (1 second) are
    """
    partitions = []
    last_x = quads[-1][0][0]
    num_partitions = last_x // length
    for i in xrange(num_partitions):
        partitions.append(bisect_left(quads, [(i * length, None)]))
    partitions.append(len(quads))
    return partitions

def _n_strongest(quads, n=9):
    """
    Returns list of 9 strongest quads in each 1 second partition
    Strongest is calculated by magnitudes of C and D in quad
    """
    strongest = []
    partitions = _find_partitions(quads)
    key = lambda x: (x[1][0] + x[1][1] + x[2][0] + x[2][1])
    for i in xrange(1, len(partitions)):
        start = partitions[i - 1]
        end = partitions[i]
        strongest += nlargest(n, quads[start:end], key)
    return strongest

def generate_hash(quad):
    """
    Compute translation- and scale-invariant hash from a given quad
    """
    A, C, D, B = quad
    B = (B[0] - A[0], B[1] - A[1])
    C = (C[0] - A[0], C[1] - A[1])
    D = (D[0] - A[0], D[1] - A[1])
    cDash = (C[0] / B[0], C[1] / B[1])
    dDash = (D[0] / B[0], D[1] / B[1])
    return [[cDash, dDash]]