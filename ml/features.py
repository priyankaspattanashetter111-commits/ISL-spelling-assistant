import numpy as np

def normalize(hands):
    """126 coordinates + 2 presence bits; shared wrist origin/scale retains two-hand geometry.
    Sort by image wrist x to avoid unstable handedness labels. Do not mirror the input.
    """
    hands = sorted(hands, key=lambda h: h[0][0])[:2]
    if not hands:
        return None
    arrays = [np.asarray(h, dtype=float).reshape(21, 3) for h in hands]
    origin = arrays[0][0].copy()
    scale = max(float(np.linalg.norm(a[9, :2]-a[0, :2])) for a in arrays)
    if scale < 1e-5:
        return None
    result = []
    for a in arrays:
        result.extend(((a-origin)/scale).flatten().tolist())
    result.extend([0.] * (126-len(result)))
    result.extend([1., float(len(arrays)==2)])
    return result
