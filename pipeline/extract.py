"""
extract.py — Fill the layout tree with real content.   (Phase 2, step 2)

The tree from hierarchy.py knows *where* and *what type* each element is, but not
its text or colors. This samples the original screenshot to add:
  - text:  OCR inside each text-bearing element's box
  - color: dominant background + a contrasting foreground, snapped to Tailwind tokens

OCR backend is pytesseract (needs the tesseract binary). If it's missing we
degrade to empty text so the pipeline still runs.
"""

from PIL import Image

try:
    import pytesseract
    import shutil, os
    # if tesseract isn't on PATH, point at the default Windows install location
    if shutil.which("tesseract") is None:
        _default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(_default):
            pytesseract.pytesseract.tesseract_cmd = _default
    _HAS_OCR = True
except Exception:
    _HAS_OCR = False

TEXT_TYPES = {"button", "heading", "paragraph", "label", "link", "badge",
              "list_item", "input", "textarea", "select"}

TAILWIND_COLORS = {
    "white": (255, 255, 255), "black": (0, 0, 0),
    "slate-50": (248, 250, 252), "slate-100": (241, 245, 249),
    "slate-200": (226, 232, 240), "slate-500": (100, 116, 139),
    "slate-800": (30, 41, 59), "slate-900": (15, 23, 42),
    "gray-100": (243, 244, 246), "gray-500": (107, 114, 128), "gray-900": (17, 24, 39),
    "blue-600": (37, 99, 235), "blue-500": (59, 130, 246),
    "green-600": (5, 150, 105), "green-500": (34, 197, 94),
    "red-600": (220, 38, 38), "purple-600": (124, 58, 237),
    "violet-400": (167, 139, 250), "amber-500": (245, 158, 11),
    "pink-600": (219, 39, 119), "zinc-800": (39, 39, 42), "zinc-900": (24, 24, 27),
}


def _snap_color(rgb):
    best, bestd = "gray-500", 1e18
    for token, c in TAILWIND_COLORS.items():
        d = sum((a - b) ** 2 for a, b in zip(rgb, c))
        if d < bestd:
            best, bestd = token, d
    return best


def _dominant_color(img, box):
    x1, y1, x2, y2 = (int(v) for v in box)
    x1, y1 = max(0, x1), max(0, y1)
    crop = img.crop((x1, y1, max(x1 + 1, x2), max(y1 + 1, y2))).convert("RGB")
    crop.thumbnail((24, 24))
    colors = crop.getcolors(24 * 24) or [(1, (128, 128, 128))]
    return max(colors, key=lambda c: c[0])[1]


def _border_vs_center(img, box):
    x1, y1, x2, y2 = (int(v) for v in box)
    bg = _dominant_color(img, [x1, y1, x2, y1 + max(2, (y2 - y1) // 6)])
    fg = _dominant_color(img, [x1 + (x2 - x1) // 3, y1 + (y2 - y1) // 3,
                               x2 - (x2 - x1) // 3, y2 - (y2 - y1) // 3])
    return bg, fg


def _ocr(img, box):
    if not _HAS_OCR:
        return ""
    x1, y1, x2, y2 = (int(v) for v in box)
    if x2 - x1 < 6 or y2 - y1 < 6:
        return ""
    crop = img.crop((max(0, x1), max(0, y1), x2, y2))
    try:
        text = pytesseract.image_to_string(crop, config="--psm 7").strip()
    except Exception:
        return ""
    return " ".join(text.split())[:80]


def enrich(node, img):
    if node["type"] != "root":
        bg, fg = _border_vs_center(img, node["box"])
        node["colors"] = {"bg": _snap_color(bg), "fg": _snap_color(fg)}
        if node["type"] in TEXT_TYPES:
            node["text"] = _ocr(img, node["box"])
    for child in node["children"]:
        enrich(child, img)
    return node


def enrich_from_path(node, image_path):
    return enrich(node, Image.open(image_path).convert("RGB"))


if __name__ == "__main__":
    print("OCR available:", _HAS_OCR)
    print("snap (37,99,235) ->", _snap_color((37, 99, 235)))
    print("snap (250,250,250) ->", _snap_color((250, 250, 250)))
