import itertools

def quads(root, peaks, q, r, n, k=497):
    """
    finds valid quads for given root
    k should be same between ref/query
    r and n should be smaller for ref, larger for query
    
    Suggested values for reference/quad parameters:
        Ref   Q = 2
              R = 247
              N = 5
        Query Q = 500
              R = 985
              N = 8
    """
    quads = []
    A = root
    filtered = _filter_peaks(A, peaks, r, k)
    if filtered is None:
        return []
    found = _find_quads(A, filtered, q)
    if found is not None:
        quads += found
    return quads

def _filter_peaks(A, peaks, r, k):
    """
    returns peaks inside window of Ax + k ± (r / 2)
    """
    endOfTrack = peaks[-1][0]
    windowStart = A[0] + k - (r / 2)
    if windowStart > endOfTrack:
        return None
    windowEnd = windowStart + r
    filtered = [x for x in peaks if x[0] >= windowStart and x[0] <= windowEnd]
    if len(filtered) is 0:
        return None
    return filtered

def _find_quads(A, filtered, q):
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
            B, C, D = (comb[2], comb[0], comb[1])
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
    # !! assumes combinations were sorted by x value
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