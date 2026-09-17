#!/usr/bin/env python3
"""Generate VS Code Marketplace store screenshots for Jade Veil Theme.

Produces two images (light + dark) showing the editor with syntax-highlighted
sample code, mimicking the real VS Code UI. Colors are read dynamically from
the theme JSON files so the screenshots always match the installed theme.

Output: store-assets/screenshots/en/screenshot-light.png
        store-assets/screenshots/en/screenshot-dark.png
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES = os.path.join(BASE, "themes")
OUT = os.path.join(BASE, "store-assets", "screenshots", "en")
os.makedirs(OUT, exist_ok=True)

def load_theme(name):
    path = os.path.join(THEMES, name)
    data = json.loads(open(path, encoding="utf-8").read())
    colors = data.get("colors", {})
    token_colors = data.get("tokenColors", [])
    tokens = {}
    for tc in token_colors:
        scope = tc.get("scope")
        settings = tc.get("settings", {})
        fg = settings.get("foreground")
        if scope and fg:
            for s in (scope.split(",") if isinstance(scope, str) else scope):
                tokens[s.strip()] = fg
    return colors, tokens

FONT_DIR = r"C:\Windows\Fonts"

def font(size, bold=False):
    name = "consolab.ttf" if bold else "consola.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()

W, H = 1280, 800

# Sample code lines: (text, token-type). Keep lines short to avoid side overlap.
SAMPLE = [
    ("function greet(name) {", "keyword"),
    ('  const msg = `Hello, ${name}!`;', "string"),
    ("  return msg;", "keyword"),
    ("}", "keyword"),
    ("", None),
    ("// Jade Veil — a palette for focused coding", "comment"),
    ("class User {", "keyword"),
    ("  constructor(id, name) {", "keyword"),
    ("    this.id = id;", "variable"),
    ("    this.name = name;", "variable"),
    ("  }", "keyword"),
    ("}", "keyword"),
    ("", None),
    ("const u = new User(42, 'Jade Veil');", "variable"),
    ("console.log(u.name, u.id);", "string"),
    ("", None),
    ("// soft tones for long reading", "comment"),
    ("export default User;", "keyword"),
]

def draw_screenshot(theme_name, out_name):
    colors, tokens = load_theme(theme_name)

    def c(key, default):
        v = colors.get(key, default)
        return tuple(int(v.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    editor_bg = c("editor.background", (255, 255, 255))
    editor_fg = c("editor.foreground", (30, 30, 30))
    side_bg = c("sideBar.background", editor_bg)
    side_fg = c("sideBar.foreground", editor_fg)
    title_bg = c("titleBar.activeBackground", side_bg)
    title_fg = c("titleBar.activeForeground", editor_fg)
    tab_bg = c("tab.activeBackground", editor_bg)
    tab_fg = c("tab.activeForeground", editor_fg)
    tab_inactive = c("tab.inactiveBackground", side_bg)
    activity_bg = c("activityBar.background", side_bg)
    activity_fg = c("activityBar.foreground", side_fg)
    line_no = c("editorLineNumber.foreground", (150, 150, 150))
    status_bg = c("statusBar.background", title_bg)
    status_fg = c("statusBar.foreground", title_fg)

    img = Image.new("RGB", (W, H), editor_bg)
    d = ImageDraw.Draw(img)

    TITLE_H = 36
    ACT_W = 48
    SIDE_W = 200
    GUTTER_W = 52  # wider gutter for line numbers
    STATUS_H = 26

    # Title bar
    d.rectangle([0, 0, W, TITLE_H], fill=title_bg)
    d.text((14, 10), "Jade Veil Theme", font=font(14, True), fill=title_fg)
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        d.ellipse([W - 70 + i * 20, 12, W - 58 + i * 20, 24], fill=col)

    # Activity bar
    d.rectangle([0, TITLE_H, ACT_W, H - STATUS_H], fill=activity_bg)
    d.text((16, TITLE_H + 14), "EXPL", font=font(12, True), fill=activity_fg)

    # Side bar
    sx = ACT_W
    d.rectangle([sx, TITLE_H, sx + SIDE_W, H - STATUS_H], fill=side_bg)
    fy = TITLE_H + 16
    d.text((sx + 14, fy), "EXPLORER", font=font(11, True), fill=side_fg)
    fy += 30
    # Shortened labels to avoid overflow
    for label in ["  theme-project", "    package.json", "    themes/", "      light-color.json", "      dark-color.json", "    scripts/", "    store-assets/"]:
        d.text((sx + 10, fy), label, font=font(13), fill=side_fg)
        fy += 24

    # Editor area
    ex = sx + SIDE_W
    # tabs
    d.rectangle([ex, TITLE_H, ex + (W - ex), TITLE_H + 36], fill=tab_inactive)
    d.rectangle([ex, TITLE_H, ex + 220, TITLE_H + 36], fill=tab_bg)
    d.text((ex + 16, TITLE_H + 10), "sample.js", font=font(13, True), fill=tab_fg)
    d.text((ex + 240, TITLE_H + 12), "README.md", font=font(13), fill=tab_fg)

    # editor background
    ey = TITLE_H + 36
    d.rectangle([ex, ey, W, H - STATUS_H], fill=editor_bg)

    # code
    pad_x = ex + GUTTER_W
    pad_y = ey + 18
    line_h = 26
    code_font = font(19)
    for i, (line, tok) in enumerate(SAMPLE):
        y = pad_y + i * line_h
        # line number
        d.text((ex + 18, y), str(i + 1), font=font(14), fill=line_no)
        if not line:
            continue
        # Token-level highlighting from the theme's TextMate colors.
        import re
        parts = re.findall(r'''//.*|`[^`]*`|"[^"\n]*"|'[^'\n]*'|\b\d+\b|[A-Za-z_$][\w$]*|\s+|.''', line)
        x = pad_x
        for j, part in enumerate(parts):
            scope = 'variable'
            if part.startswith('//'): scope = 'comment'
            elif part[:1] in ('"', "'", '`'): scope = 'string'
            elif part.isdigit(): scope = 'constant.numeric'
            elif part in ('function','const','return','class','this','new','export','default'): scope = 'keyword'
            elif part in ('User',): scope = 'entity.name.type'
            elif j + 1 < len(parts) and parts[j+1] == '(': scope = 'entity.name.function'
            fg = tokens.get(scope, editor_fg)
            d.text((x,y),part,font=code_font,fill=fg)
            x += d.textlength(part,font=code_font)

    # Palette preview block (right side of editor area)
    palette_x = W - 266
    palette_y = ey + 70
    palette_w = W - palette_x - 40
    palette_h = 340
    pal_bg = tuple(min(255, v + 6) for v in editor_bg) if sum(editor_bg) < 384 else tuple(max(0, v - 12) for v in editor_bg)
    d.rounded_rectangle([palette_x, palette_y, palette_x + palette_w, palette_y + palette_h],
                        radius=12, fill=pal_bg, outline=line_no)
    d.text((palette_x + 16, palette_y + 14), "Palette", font=font(15, True), fill=editor_fg)

    def to_rgb(v, default):
        try:
            return tuple(int(v.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            return default

    swatches = [
        ("bg",       colors.get("editor.background", "#ffffff")),
        ("fg",       colors.get("editor.foreground", "#000000")),
        ("side",     colors.get("sideBar.background", "#ffffff")),
        ("title",    colors.get("titleBar.activeBackground", "#ffffff")),
        ("status",   colors.get("statusBar.background", "#ffffff")),
        ("keyword",  tokens.get("keyword.control", tokens.get("keyword", "#000000"))),
        ("string",   tokens.get("string", "#000000")),
        ("comment",  tokens.get("comment", "#000000")),
        ("number",   tokens.get("constant.numeric", "#000000")),
        ("variable", tokens.get("variable", "#000000")),
    ]
    sw_y = palette_y + 46
    sw_x = palette_x + 16
    for label, hexv in swatches:
        rgb = to_rgb(hexv, (200, 200, 200))
        d.rounded_rectangle([sw_x, sw_y, sw_x + 24, sw_y + 24], radius=6, fill=rgb, outline=line_no)
        d.text((sw_x + 36, sw_y + 7), f"{label}  {hexv.upper()}", font=font(11), fill=editor_fg)
        sw_y += 28

    # status bar
    d.rectangle([0, H - STATUS_H, W, H], fill=status_bg)
    d.text((14, H - STATUS_H + 6), "JavaScript  |  " + ("Light" if "light" in theme_name else "Dark"), font=font(12), fill=status_fg)
    d.text((W - 160, H - STATUS_H + 6), "UTF-8", font=font(12), fill=status_fg)

    d.text((ex + 24, H - 74), "Theme color preview / " + ("Light" if "light" in theme_name else "Dark"), font=font(14), fill=line_no)

    out = os.path.join(OUT, out_name)
    img.save(out, "PNG")
    print("saved", out, img.size)

if __name__ == "__main__":
    draw_screenshot("jade-veil-light-color-theme.json", "screenshot-light.png")
    draw_screenshot("jade-veil-dark-color-theme.json", "screenshot-dark.png")
