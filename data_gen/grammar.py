"""
grammar.py — Synthetic UI generator.

Produces random-but-valid UI layouts as a single HTML string. Every element we
want the detector to learn is tagged with a `data-ui="<type>"` attribute, which
the renderer reads to produce ground-truth labels. No manual annotation, ever.
"""

import random

CLASSES = [
    "button", "input", "textarea", "checkbox", "radio", "toggle", "select",
    "label", "heading", "paragraph", "link", "badge", "avatar", "icon_button",
    "image", "card", "navbar", "list_item",
]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASSES)}

FONTS = [
    "system-ui, sans-serif", "'Segoe UI', sans-serif", "Arial, sans-serif",
    "Georgia, serif", "'Courier New', monospace", "Verdana, sans-serif",
]

LIGHT_PALETTES = [
    {"bg": "#ffffff", "surface": "#f8fafc", "text": "#0f172a", "muted": "#64748b",
     "primary": "#2563eb", "border": "#e2e8f0", "accent": "#7c3aed"},
    {"bg": "#fafaf9", "surface": "#f5f5f4", "text": "#1c1917", "muted": "#78716c",
     "primary": "#059669", "border": "#e7e5e4", "accent": "#d97706"},
    {"bg": "#ffffff", "surface": "#fef2f2", "text": "#111827", "muted": "#6b7280",
     "primary": "#dc2626", "border": "#f3f4f6", "accent": "#db2777"},
]
DARK_PALETTES = [
    {"bg": "#0f172a", "surface": "#1e293b", "text": "#f1f5f9", "muted": "#94a3b8",
     "primary": "#3b82f6", "border": "#334155", "accent": "#a78bfa"},
    {"bg": "#18181b", "surface": "#27272a", "text": "#fafafa", "muted": "#a1a1aa",
     "primary": "#22c55e", "border": "#3f3f46", "accent": "#f59e0b"},
]

WORDS = ("Dashboard Settings Profile Account Overview Reports Analytics Billing "
         "Save Cancel Submit Continue Delete Edit Create Update Search Filter "
         "Welcome back Manage your Configure the Recent activity Total revenue "
         "Active users New customers Email Password Username Full name Message "
         "Notifications Privacy Security General Advanced Home About Contact").split()


def _words(n):
    return " ".join(random.choice(WORDS) for _ in range(n))


def _rint(a, b):
    return random.randint(a, b)


class UIBuilder:
    """Builds one random UI and returns its HTML. Each call is a fresh sample."""

    def __init__(self):
        self.dark = random.random() < 0.35
        self.pal = random.choice(DARK_PALETTES if self.dark else LIGHT_PALETTES)
        self.font = random.choice(FONTS)
        self.radius = random.choice([0, 4, 6, 8, 12, 16])
        self.gap = _rint(8, 24)
        self.pad = _rint(12, 32)

    def button(self, primary=True):
        bg = self.pal["primary"] if primary else self.pal["surface"]
        fg = "#ffffff" if primary else self.pal["text"]
        return (f'<button data-ui="button" style="padding:{_rint(8,12)}px {_rint(14,24)}px;'
                f'background:{bg};color:{fg};border:none;border-radius:{self.radius}px;'
                f'font:500 14px {self.font};cursor:pointer">{_words(_rint(1,2))}</button>')

    def icon_button(self):
        s = _rint(32, 44)
        return (f'<button data-ui="icon_button" style="width:{s}px;height:{s}px;'
                f'background:{self.pal["surface"]};border:1px solid {self.pal["border"]};'
                f'border-radius:{self.radius}px;color:{self.pal["muted"]};font-size:18px">'
                f'{random.choice("\u2630\u2699\u2192\u2026\u2715\u002b\u2764")}</button>')

    def input(self):
        return (f'<input data-ui="input" placeholder="{_words(_rint(1,3))}" '
                f'style="padding:{_rint(8,12)}px 12px;background:{self.pal["bg"]};'
                f'color:{self.pal["text"]};border:1px solid {self.pal["border"]};'
                f'border-radius:{self.radius}px;font:14px {self.font};width:100%;'
                f'box-sizing:border-box"/>')

    def textarea(self):
        return (f'<textarea data-ui="textarea" placeholder="{_words(3)}" rows="{_rint(2,4)}" '
                f'style="padding:10px 12px;background:{self.pal["bg"]};color:{self.pal["text"]};'
                f'border:1px solid {self.pal["border"]};border-radius:{self.radius}px;'
                f'font:14px {self.font};width:100%;box-sizing:border-box;resize:none"></textarea>')

    def checkbox(self):
        return (f'<span data-ui="checkbox" style="display:inline-flex;align-items:center;'
                f'gap:8px;color:{self.pal["text"]};font:14px {self.font}">'
                f'<span style="width:18px;height:18px;border:1px solid {self.pal["border"]};'
                f'border-radius:4px;background:{self.pal["bg"]};display:inline-block"></span>'
                f'{_words(_rint(1,2))}</span>')

    def radio(self):
        return (f'<span data-ui="radio" style="display:inline-flex;align-items:center;'
                f'gap:8px;color:{self.pal["text"]};font:14px {self.font}">'
                f'<span style="width:18px;height:18px;border:1px solid {self.pal["border"]};'
                f'border-radius:50%;background:{self.pal["bg"]};display:inline-block"></span>'
                f'{_words(_rint(1,2))}</span>')

    def toggle(self):
        return (f'<span data-ui="toggle" style="display:inline-block;width:40px;height:22px;'
                f'background:{self.pal["primary"]};border-radius:11px;position:relative">'
                f'<span style="position:absolute;right:2px;top:2px;width:18px;height:18px;'
                f'background:#fff;border-radius:50%"></span></span>')

    def select(self):
        return (f'<div data-ui="select" style="padding:{_rint(8,12)}px 12px;'
                f'background:{self.pal["bg"]};color:{self.pal["text"]};'
                f'border:1px solid {self.pal["border"]};border-radius:{self.radius}px;'
                f'font:14px {self.font};display:flex;justify-content:space-between;'
                f'min-width:120px">{_words(1)} <span>\u25be</span></div>')

    def label(self):
        return (f'<label data-ui="label" style="color:{self.pal["muted"]};'
                f'font:500 13px {self.font}">{_words(_rint(1,2))}</label>')

    def heading(self):
        sz = random.choice([20, 24, 28, 32])
        return (f'<div data-ui="heading" style="color:{self.pal["text"]};'
                f'font:700 {sz}px {self.font}">{_words(_rint(2,4))}</div>')

    def paragraph(self):
        return (f'<div data-ui="paragraph" style="color:{self.pal["muted"]};'
                f'font:14px/1.5 {self.font};max-width:520px">{_words(_rint(8,18))}</div>')

    def link(self):
        return (f'<span data-ui="link" style="color:{self.pal["primary"]};'
                f'font:14px {self.font};text-decoration:underline">{_words(_rint(1,2))}</span>')

    def badge(self):
        return (f'<span data-ui="badge" style="padding:3px 10px;background:{self.pal["accent"]};'
                f'color:#fff;border-radius:999px;font:600 12px {self.font}">{_words(1)}</span>')

    def avatar(self):
        s = _rint(32, 48)
        return (f'<span data-ui="avatar" style="width:{s}px;height:{s}px;border-radius:50%;'
                f'background:{self.pal["accent"]};display:inline-flex;align-items:center;'
                f'justify-content:center;color:#fff;font:600 14px {self.font}">'
                f'{random.choice("ABCDEFGHJKMNPRST")}</span>')

    def image(self):
        w, h = _rint(80, 240), _rint(60, 160)
        return (f'<div data-ui="image" style="width:{w}px;height:{h}px;'
                f'background:linear-gradient(135deg,{self.pal["surface"]},{self.pal["border"]});'
                f'border-radius:{self.radius}px;display:flex;align-items:center;'
                f'justify-content:center;color:{self.pal["muted"]};font:24px {self.font}">'
                f'\u25a6</div>')

    def _row(self, inner, justify="flex-start"):
        return (f'<div style="display:flex;flex-direction:row;gap:{self.gap}px;'
                f'align-items:center;justify-content:{justify}">{inner}</div>')

    def _col(self, inner):
        return (f'<div style="display:flex;flex-direction:column;gap:{self.gap}px">{inner}</div>')

    def navbar(self):
        left = self.avatar() + self.heading()
        links = "".join(self.link() for _ in range(_rint(2, 4)))
        right = self.icon_button() + (self.button() if random.random() < 0.6 else "")
        return (f'<div data-ui="navbar" style="display:flex;align-items:center;'
                f'justify-content:space-between;padding:{self.pad//2}px {self.pad}px;'
                f'background:{self.pal["surface"]};border-bottom:1px solid {self.pal["border"]};'
                f'border-radius:{self.radius}px">'
                f'<div style="display:flex;align-items:center;gap:{self.gap}px">{left}</div>'
                f'<div style="display:flex;align-items:center;gap:{self.gap}px">{links}</div>'
                f'<div style="display:flex;align-items:center;gap:{self.gap}px">{right}</div></div>')

    def card(self):
        parts = [self.heading()]
        if random.random() < 0.7:
            parts.append(self.paragraph())
        if random.random() < 0.5:
            parts.append(self.image())
        if random.random() < 0.6:
            parts.append(self._row(self.button() + self.button(primary=False), "flex-end"))
        inner = "".join(parts)
        return (f'<div data-ui="card" style="padding:{self.pad}px;background:{self.pal["surface"]};'
                f'border:1px solid {self.pal["border"]};border-radius:{self.radius+4}px;'
                f'display:flex;flex-direction:column;gap:{self.gap}px;max-width:420px">{inner}</div>')

    def form(self):
        fields = []
        for _ in range(_rint(2, 4)):
            field = self.label() + random.choice([self.input(), self.input(), self.select(), self.textarea()])
            fields.append(f'<div style="display:flex;flex-direction:column;gap:6px">{field}</div>')
        if random.random() < 0.6:
            fields.append(self.checkbox())
        fields.append(self._row(self.button() + self.button(primary=False), "flex-start"))
        inner = "".join(fields)
        return (f'<div data-ui="card" style="padding:{self.pad}px;background:{self.pal["surface"]};'
                f'border:1px solid {self.pal["border"]};border-radius:{self.radius+4}px;'
                f'display:flex;flex-direction:column;gap:{self.gap}px;max-width:440px">{inner}</div>')

    def list_block(self):
        rows = []
        for _ in range(_rint(3, 6)):
            row = (self.avatar() if random.random() < 0.7 else "") + \
                  f'<div style="flex:1"><div style="color:{self.pal["text"]};font:600 14px {self.font}">{_words(_rint(1,3))}</div>' \
                  f'<div style="color:{self.pal["muted"]};font:13px {self.font}">{_words(_rint(2,5))}</div></div>' + \
                  (self.badge() if random.random() < 0.5 else self.icon_button())
            rows.append(f'<div data-ui="list_item" style="display:flex;align-items:center;'
                        f'gap:{self.gap}px;padding:{_rint(8,14)}px {self.pad//2}px;'
                        f'border-bottom:1px solid {self.pal["border"]}">{row}</div>')
        inner = "".join(rows)
        return (f'<div data-ui="card" style="background:{self.pal["surface"]};'
                f'border:1px solid {self.pal["border"]};border-radius:{self.radius+4}px;'
                f'overflow:hidden;max-width:520px">{inner}</div>')

    def stat_cards(self):
        cards = []
        for _ in range(_rint(2, 4)):
            cards.append(f'<div data-ui="card" style="flex:1;padding:{self.pad}px;'
                         f'background:{self.pal["surface"]};border:1px solid {self.pal["border"]};'
                         f'border-radius:{self.radius+4}px;min-width:140px">'
                         f'<div data-ui="label" style="color:{self.pal["muted"]};font:13px {self.font}">{_words(2)}</div>'
                         f'<div data-ui="heading" style="color:{self.pal["text"]};font:700 26px {self.font};margin-top:6px">{_rint(10,99)}{random.choice(["K","%","",".5K"])}</div></div>')
        return self._row("".join(cards))

    def sidebar(self):
        """A left navigation column: logo + nav links."""
        top = self.avatar() + (self.heading() if random.random() < 0.5 else "")
        nav_items = []
        for _ in range(_rint(4, 7)):
            nav_items.append(
                f'<div data-ui="list_item" style="display:flex;align-items:center;'
                f'gap:10px;padding:10px 12px;border-radius:{self.radius}px;'
                f'color:{self.pal["text"]};font:500 14px {self.font}">'
                f'{self.icon_button() if random.random() < 0.4 else ""}'
                f'<span>{_words(1)}</span></div>')
        nav = "".join(nav_items)
        return (f'<div data-ui="card" style="width:{_rint(200,260)}px;'
                f'background:{self.pal["surface"]};border-right:1px solid {self.pal["border"]};'
                f'padding:{self.pad}px {self.pad//2}px;display:flex;flex-direction:column;'
                f'gap:{self.gap}px;height:100%;flex-shrink:0">'
                f'<div style="display:flex;align-items:center;gap:10px;padding:0 12px 12px">{top}</div>'
                f'{nav}</div>')

    def build(self):
        """Assemble a full page. Randomly picks a layout style."""
        if random.random() < 0.35:
            return self._build_app_shell()
        return self._build_simple()

    def _build_simple(self):
        """The original simple/clean layout (sidebar-free)."""
        blocks = []
        if random.random() < 0.7:
            blocks.append(self.navbar())
        body_blocks = []
        n = _rint(2, 4)
        choices = [self.card, self.form, self.list_block, self.stat_cards]
        if random.random() < 0.8:
            body_blocks.append(self.heading())
        for _ in range(n):
            body_blocks.append(random.choice(choices)())
        body = self._col("".join(body_blocks))
        blocks.append(f'<div style="padding:{self.pad}px;display:flex;flex-direction:column;'
                      f'gap:{self.gap+4}px">{body}</div>')
        inner = "".join(blocks)
        return self._wrap(inner)

    def _build_app_shell(self):
        """Dense layout: a left sidebar beside a main content area."""
        main_blocks = [self.heading()]
        if random.random() < 0.7:
            main_blocks.append(self.stat_cards())
        n = _rint(2, 4)
        choices = [self.card, self.list_block, self.form, self.stat_cards]
        for _ in range(n):
            main_blocks.append(random.choice(choices)())
        main = (f'<div style="flex:1;padding:{self.pad}px;display:flex;'
                f'flex-direction:column;gap:{self.gap+4}px;overflow:hidden">'
                f'{"".join(main_blocks)}</div>')
        shell = (f'<div style="display:flex;flex-direction:row;min-height:600px;'
                 f'align-items:stretch">{self.sidebar()}{main}</div>')
        return self._wrap(shell)

    def _wrap(self, inner):
        """Wrap inner HTML in the page boilerplate."""
        return (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                f'<style>*{{margin:0;box-sizing:border-box}}body{{background:{self.pal["bg"]};'
                f'font-family:{self.font}}}</style></head>'
                f'<body><div id="root">{inner}</div></body></html>')


def generate_html():
    """Top-level entry: returns one random UI as an HTML string."""
    return UIBuilder().build()


if __name__ == "__main__":
    html = generate_html()
    with open("sample.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote sample.html ({len(html)} chars). Open it in a browser to eyeball it.")