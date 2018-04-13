# This Python file uses the following encoding: utf-8
from __future__ import division

from bisect import bisect_left, bisect_right
from collections import namedtuple
from itertools import combinations


def find_quads(peaks, r, c):
    """
    Returns list of valid/strong quads for list of peaks
    """
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
    lastPeak = peaks[-1].x
    windowStart = root.x + c - (r / 2)
    if windowStart > lastPeak:
        return None
    windowEnd = windowStart + r
    idx_start = bisect_left(peaks, (windowStart, 0))
    idx_end = bisect_right(peaks, (windowEnd, 0))
    filtered = peaks[idx_start:idx_end]
    if len(filtered) < 3:
        return None
    return filtered


def _valid_quads(root, filtered):
    """
    returns list of validated quads for given root (A)
    """
    Quad = namedtuple('Quad', ['A', 'C', 'D', 'B'])
    validQuads = []
    for comb in combinations(filtered, 3):
        quad = Quad(root, comb[0], comb[1], comb[2])
        if _valid_quad(quad):
            validQuads.append(quad)
    if len(validQuads) is 0:
        return None
    else:
        return validQuads


def _valid_quad(q):
    """
    Evaluates:

          Ay < By
      Ax < Cx <= Dx <= Bx
      Ay < Cy ,  Dy <= By

    !! NOTE: assumes combinations are sorted by x value
    (default behavior of itertools.combinations)
    """
    if q.A.y < q.C.y < q.B.y and q.A.y < q.D.y <= q.B.y:
        return True
    else:
        return False
