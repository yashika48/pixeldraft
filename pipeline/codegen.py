"""
codegen.py — Layout tree  ->  React + Tailwind.   (Phase 2, step 3)

Deterministic templating. Each element type has a JSX template; containers become
flex divs with classes inferred from the layout (direction, gap, padding, justify).
Pixel values are snapped to Tailwind's spacing scale so the output reads like clean,
human-written code rather than a wall of inline styles.

Entry point: generate_react(tree) -> a string of valid JSX (a single component).
"""

# Tailwind spacing scale (px -> the nearest `n` in p-n / gap-n; 1 unit = 4px)
_SPACING = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]


def _space(px):
    """Snap a pixel value to the nearest Tailwind spacing step."""
    units = px / 4
    return min(_SPACING, key=lambda s: abs(s - units))


def _layout_classes(layout):
    if not layout:
        return ""
    cls = ["flex"]
    cls.append("flex-row" if layout.get("direction") == "row" else "flex-col")
    g = _space(layout.get("gap", 0))
    if g:
        cls.append(f"gap-{g}")
    p = _space(layout.get("pad", 0))
    if p:
        cls.append(f"p-{p}")
    j = layout.get("justify")
    if j == "between":
        cls.append("justify-between")
    elif j == "center":
        cls.append("justify-center")
    # rows are vertically centered by default; avoid emitting items-center twice
    if layout.get("direction") == "row" or j == "center":
        cls.append("items-center")
    return " ".join(cls)


def _txt(node, default=""):
    t = node.get("text", "").strip()
    return t if t else default


# --- per-type leaf templates ---------------------------------------------------

def _leaf(node):
    t = node["type"]
    c = node.get("colors", {})
    bg = c.get("bg", "white")
    fg = c.get("fg", "gray-900")
    # readability guard: never emit near-invisible light text on light bg
    light = {"white", "slate-50", "slate-100", "slate-200", "gray-100"}
    if fg in light:
        fg = "gray-900"

    if t == "button":
        return f'<button className="px-4 py-2 rounded-lg bg-{bg} text-{fg} font-medium">{_txt(node,"Button")}</button>'
    if t == "icon_button":
        return f'<button className="w-10 h-10 grid place-items-center rounded-lg border border-slate-200 text-{fg}" aria-label="icon">{{/* icon */}}\u2630</button>'
    if t == "input":
        return f'<input className="px-3 py-2 rounded-lg border border-slate-200 w-full" placeholder="{_txt(node,"Enter text")}" />'
    if t == "textarea":
        return f'<textarea className="px-3 py-2 rounded-lg border border-slate-200 w-full" rows={{3}} placeholder="{_txt(node,"Message")}" />'
    if t == "checkbox":
        return f'<label className="inline-flex items-center gap-2"><input type="checkbox" />{_txt(node,"Option")}</label>'
    if t == "radio":
        return f'<label className="inline-flex items-center gap-2"><input type="radio" />{_txt(node,"Option")}</label>'
    if t == "toggle":
        return '<button role="switch" className="w-10 h-6 rounded-full bg-blue-600 relative"><span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" /></button>'
    if t == "select":
        return f'<select className="px-3 py-2 rounded-lg border border-slate-200"><option>{_txt(node,"Select")}</option></select>'
    if t == "label":
        return f'<label className="text-sm font-medium text-{fg}">{_txt(node,"Label")}</label>'
    if t == "heading":
        return f'<h2 className="text-2xl font-bold text-{fg}">{_txt(node,"Heading")}</h2>'
    if t == "paragraph":
        return f'<p className="text-sm text-{fg} leading-relaxed">{_txt(node,"Lorem ipsum dolor sit amet.")}</p>'
    if t == "link":
        return f'<a className="text-blue-600 underline" href="#">{_txt(node,"Link")}</a>'
    if t == "badge":
        return f'<span className="px-2.5 py-0.5 rounded-full bg-{bg} text-white text-xs font-semibold">{_txt(node,"New")}</span>'
    if t == "avatar":
        return f'<div className="w-10 h-10 rounded-full bg-{bg} grid place-items-center text-white font-semibold">A</div>'
    if t == "image":
        return '<div className="bg-slate-100 rounded-lg grid place-items-center text-slate-400" style={{ width: 160, height: 100 }}>image</div>'
    return f'<div>{_txt(node, t)}</div>'


_CONTAINER_TAG = {"card": "div", "navbar": "nav", "list_item": "div", "root": "div"}


def _render(node, depth=1):
    indent = "  " * depth
    kids = node["children"]

    if not kids:
        return indent + _leaf(node)

    # container
    cls = _layout_classes(node.get("layout", {}))
    if node["type"] == "card":
        cls = ("rounded-xl border border-slate-200 bg-white " + cls).strip()
    elif node["type"] == "navbar":
        cls = ("border-b border-slate-200 bg-white " + cls).strip()

    tag = _CONTAINER_TAG.get(node["type"], "div")
    inner = "\n".join(_render(k, depth + 1) for k in kids)
    return f'{indent}<{tag} className="{cls}">\n{inner}\n{indent}</{tag}>'


def generate_react(tree, component_name="GeneratedUI"):
    body = _render(tree, depth=2)
    return (f"function {component_name}() {{\n"
            f"  return (\n{body}\n  );\n}}\n")

if __name__ == "__main__":
    import json, sys
    from hierarchy import build_tree
    els = [
        {"type": "navbar", "box": [0, 0, 1000, 60], "conf": 1},
        {"type": "avatar", "box": [10, 12, 46, 48], "conf": 1},
        {"type": "heading", "box": [56, 14, 200, 46], "conf": 1},
        {"type": "button", "box": [900, 12, 990, 48], "conf": 1},
        {"type": "card", "box": [40, 100, 460, 320], "conf": 1},
        {"type": "heading", "box": [64, 120, 300, 156], "conf": 1},
        {"type": "paragraph", "box": [64, 170, 430, 240], "conf": 1},
        {"type": "button", "box": [64, 260, 180, 300], "conf": 1},
    ]
    tree = build_tree(els, 1000, 800)
    print(generate_react(tree))
