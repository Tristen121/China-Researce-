#!/usr/bin/env python3
"""Laedt ein Foto, prueft es und speichert es als JPEG (max. 1000 px breit) unter img/<id>-<n>.jpg.

Aufruf:  python3 -I tools/foto.py <id> <n> <bild-url>
         python3 -I tools/foto.py --kontakt <id>      -> Kontaktbogen aller Fotos des Orts zum Ansehen

Ehrlicher User-Agent, kein Browser-Fake. Wenn eine Seite den Download verweigert: andere Quelle nehmen.
"""
import io
import os
import sys
import tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
UA = "ChinaIdeenAtlas/1.0 (+https://github.com/Tristen121/China-Researce-)"
SCRATCH = os.environ.get("KONTAKT_DIR", tempfile.gettempdir())


def laden(oid, n, url):
    from PIL import Image
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read(25_000_000)
    im = Image.open(io.BytesIO(data))
    im.load()
    w, h = im.size
    if w < 600:
        sys.exit(f"FEHLER: zu klein ({w}x{h}), anderes Foto suchen")
    if h > w * 1.5:
        sys.exit(f"FEHLER: extremes Hochformat ({w}x{h}), anderes Foto suchen")
    im = im.convert("RGB")
    if w > 1000:
        im = im.resize((1000, round(h * 1000 / w)), Image.LANCZOS)
    os.makedirs(IMG, exist_ok=True)
    dst = os.path.join(IMG, f"{oid}-{n}.jpg")
    im.save(dst, "JPEG", quality=80, optimize=True, progressive=True)
    print(f"ok: img/{oid}-{n}.jpg {im.size[0]}x{im.size[1]} {os.path.getsize(dst) // 1024} KB")


def kontakt(oid):
    from PIL import Image
    files = sorted(f for f in os.listdir(IMG) if f.startswith(oid + "-") and f.endswith(".jpg"))
    if not files:
        sys.exit("keine Fotos")
    thumbs = []
    for f in files:
        im = Image.open(os.path.join(IMG, f)).convert("RGB")
        im.thumbnail((420, 320))
        thumbs.append(im)
    W = sum(t.size[0] for t in thumbs) + 10 * (len(thumbs) + 1)
    H = max(t.size[1] for t in thumbs) + 20
    sheet = Image.new("RGB", (W, H), (30, 30, 30))
    x = 10
    for t in thumbs:
        sheet.paste(t, (x, 10))
        x += t.size[0] + 10
    dst = os.path.join(SCRATCH, f"kontakt-{oid}.png")
    sheet.save(dst)
    print(dst, files)


if __name__ == "__main__":
    if sys.argv[1] == "--kontakt":
        kontakt(sys.argv[2])
    else:
        laden(sys.argv[1], sys.argv[2], sys.argv[3])
