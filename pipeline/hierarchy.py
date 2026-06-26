"""
hierarchy.py — Detected boxes  ->  layout tree.   (Phase 2, step 1)

The detector gives a FLAT list of {type, box, conf}. Real UIs are nested, so we
reconstruct the containment hierarchy geometrically — no second model, fully
inspectable (which is exactly why deterministic beats a black box here).

Pipeline:
  1. Build a containment tree: each element's parent is the smallest box that
     (mostly) contains it. Everything else hangs off a synthetic root.
  2. For every container, infer layout: flex direction (row/col), gap, padding.
  3. Order siblings top-to-bottom, then left-to-right.

A "node" is: {type, box:[x1,y1,x2,y2], conf, children:[...], layout:{...}}
"""

from statistics import median


def _area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def _contains(outer, inner, tol=6.0):
    return (inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol and
            inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


def build_tree(elements, page_w, page_h):
    """elements: list of {type, box, conf}. Returns the root node."""
    root = {"type": "root", "box": [0, 0, page_w, page_h], "conf": 1.0,
            "children": [], "layout": {}}

    nodes = [dict(e, children=[], layout={}) for e in elements]
    nodes.sort(key=lambda n: _area(n["box"]), reverse=True)

    for node in nodes:
        best_parent, best_area = root, _area(root["box"])
        for cand in nodes:
            if cand is node or _area(cand["box"]) <= _area(node["box"]):
                continue
            if _contains(cand["box"], node["box"]) and _area(cand["box"]) < best_area:
                best_parent, best_area = cand, _area(cand["box"])
        best_parent["children"].append(node)

    _infer_layout(root)
    return root


def _infer_layout(node):
    kids = node["children"]
    if not kids:
        return
    kids.sort(key=lambda k: (round(k["box"][1] / 8), k["box"][0]))
    direction = _infer_direction(kids)

    gaps = []
    for a, b in zip(kids, kids[1:]):
        if direction == "row":
            gaps.append(max(0, b["box"][0] - a["box"][2]))
        else:
            gaps.append(max(0, b["box"][1] - a["box"][3]))
    gap = int(median(gaps)) if gaps else 0

    cx1, cy1, cx2, cy2 = node["box"]
    kx1 = min(k["box"][0] for k in kids); ky1 = min(k["box"][1] for k in kids)
    kx2 = max(k["box"][2] for k in kids); ky2 = max(k["box"][3] for k in kids)
    pad = int(median([max(0, kx1 - cx1), max(0, ky1 - cy1),
                      max(0, cx2 - kx2), max(0, cy2 - ky2)]))

    node["layout"] = {"direction": direction, "gap": gap, "pad": pad,
                      "justify": _infer_justify(node, kids, direction)}
    for k in kids:
        _infer_layout(k)


def _infer_direction(kids):
    if len(kids) < 2:
        return "col"
    row_votes = 0
    for a, b in zip(kids, kids[1:]):
        ay1, ay2 = a["box"][1], a["box"][3]
        by1, by2 = b["box"][1], b["box"][3]
        overlap = max(0, min(ay2, by2) - max(ay1, by1))
        smaller_h = min(ay2 - ay1, by2 - by1) or 1
        if overlap / smaller_h > 0.5:
            row_votes += 1
    return "row" if row_votes > 0 and row_votes >= len(kids) // 2 else "col"


def _infer_justify(node, kids, direction):
    cx1, _, cx2, _ = node["box"]
    if direction != "row" or len(kids) < 2:
        return "start"
    left_gap = min(k["box"][0] for k in kids) - cx1
    right_gap = cx2 - max(k["box"][2] for k in kids)
    inner = [kids[i + 1]["box"][0] - kids[i]["box"][2] for i in range(len(kids) - 1)]
    avg_inner = sum(inner) / len(inner) if inner else 0
    if avg_inner > 2 * max(left_gap, right_gap, 1):
        return "between"
    if abs(left_gap - right_gap) < 16 and left_gap > 16:
        return "center"
    return "start"


if __name__ == "__main__":
    els = [
        {"type": "navbar", "box": [0, 0, 1000, 60], "conf": 1},
        {"type": "avatar", "box": [10, 12, 46, 48], "conf": 1},
        {"type": "heading", "box": [56, 14, 200, 46], "conf": 1},
        {"type": "button", "box": [900, 12, 990, 48], "conf": 1},
        {"type": "card", "box": [40, 100, 460, 320], "conf": 1},
        {"type": "heading", "box": [64, 120, 300, 156], "conf": 1},
        {"type": "paragraph", "box": [64, 170, 430, 240], "conf": 1},
    ]
    import json
    print(json.dumps(build_tree(els, 1000, 800), indent=1))
