#!/usr/bin/env python3
"""Prueft die _wiki-Titel der Teil-Dateien und holt echte Quellen- und Bild-URLs.

Wikimedia drosselt diese Umgebung stark (HTTP 429). Deshalb: wenige, gebuendelte
Anfragen (bis 50 Titel pro Anfrage), Pause zwischen den Anfragen, Backoff bei 429.
Ergebnis wird in tools/cache/wiki.json zwischengespeichert, damit ein zweiter Lauf
nichts doppelt abfragt.

Aufruf: python3 tools/wiki_bilder.py data/parts/teil-1.json [teil-2.json ...]
Schreibt data/parts/bilder.json: {id: {"quellen": [...], "bilder": [...], "credits": [...]}}
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "ChinaIdeenAtlas/1.0 (https://github.com/Tristen121/China-Researce-)"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "wiki.json")
PAUSE = 8
BAD = re.compile(r"(map|karte|logo|flag|locator|location|icon|svg|seal|emblem|diagram|plan\b|"
                 r"commons-logo|wiki|symbol|coat_of_arms|wappen|chart|graph|signature|stamp|"
                 r"portrait|edit-clear|question_book|ambox|disambig|padlock|\.gif$|\.tif)", re.I)


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return json.load(f)
    return {}


def save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


def api(lang, params):
    params = dict(params, format="json", formatversion="2")
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for wait in (0, 60, 180, 300, 600, 900):
        if wait:
            print(f"  429, warte {wait}s", flush=True)
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            time.sleep(PAUSE)
            return data
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError("dauerhaft 429")


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def resolve_titles(lang, titles, cache):
    """Titel -> {url, title, lead} oder None (existiert nicht)."""
    key = f"pages:{lang}"
    known = cache.setdefault(key, {})
    todo = [t for t in titles if t not in known]
    for batch in chunks(todo, 50):
        print(f"{lang}: pruefe {len(batch)} Titel", flush=True)
        d = api(lang, {"action": "query", "titles": "|".join(batch), "redirects": 1,
                       "prop": "info|pageimages|coordinates", "inprop": "url", "piprop": "name"})
        q = d.get("query", {})
        alias = {}
        for n in q.get("normalized", []):
            alias[n["from"]] = n["to"]
        redir = {r["from"]: r["to"] for r in q.get("redirects", [])}
        pages = {p["title"]: p for p in q.get("pages", [])}
        for t in batch:
            t2 = alias.get(t, t)
            t3 = redir.get(t2, t2)
            p = pages.get(t3)
            if not p or p.get("missing") or p.get("invalid"):
                known[t] = None
            else:
                c = (p.get("coordinates") or [{}])[0]
                known[t] = {"title": p["title"], "url": p["fullurl"], "lead": p.get("pageimage"),
                            "lat": c.get("lat"), "lon": c.get("lon")}
        save_cache(cache)
    return known


def page_images(lang, titles, cache):
    """Echte Seitentitel -> Liste der Dateinamen im Artikel."""
    key = f"images:{lang}"
    known = cache.setdefault(key, {})
    todo = [t for t in titles if t not in known]
    for batch in chunks(todo, 10):
        print(f"{lang}: Bilderlisten fuer {len(batch)} Artikel", flush=True)
        res = {t: [] for t in batch}
        cont = {}
        while True:
            d = api(lang, dict({"action": "query", "titles": "|".join(batch), "prop": "images",
                                "imlimit": "max"}, **cont))
            for p in d.get("query", {}).get("pages", []):
                for im in p.get("images", []):
                    res.setdefault(p["title"], []).append(im["title"].split(":", 1)[1])
            if "continue" in d:
                cont = {k: v for k, v in d["continue"].items()}
            else:
                break
        known.update(res)
        save_cache(cache)
    return known


def image_info(files, cache):
    """Dateiname -> {thumb, w, h, artist, license, page, desc} (ueber en-API, shared repo)."""
    known = cache.setdefault("fileinfo", {})
    todo = [f for f in dict.fromkeys(files) if f not in known]
    for batch in chunks(todo, 50):
        print(f"Bildinfos fuer {len(batch)} Dateien", flush=True)
        d = api("en", {"action": "query", "titles": "|".join("File:" + f for f in batch),
                       "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
                       "iiextmetadatafilter": "Artist|LicenseShortName|ImageDescription|ObjectName",
                       "iiurlwidth": 1280})
        q = d.get("query", {})
        norm = {n["to"]: n["from"] for n in q.get("normalized", [])}
        for p in q.get("pages", []):
            name = norm.get(p["title"], p["title"]).split(":", 1)[1]
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                known[name] = None
                continue
            md = ii.get("extmetadata", {})
            strip = lambda s: re.sub(r"<[^>]+>", "", (s or {}).get("value", "")).strip()
            thumb = (ii.get("thumburl") or ii.get("url") or "").split("?")[0]
            known[name] = {"thumb": thumb, "orig": ii.get("url"), "w": ii.get("width"),
                           "h": ii.get("height"), "mime": ii.get("mime"),
                           "page": ii.get("descriptionurl"), "artist": strip(md.get("Artist"))[:120],
                           "license": strip(md.get("LicenseShortName")),
                           "desc": strip(md.get("ImageDescription"))[:200]}
        for f in batch:
            known.setdefault(f, None)
        save_cache(cache)
    return known


def main(paths, bilder=True):
    orte = []
    for p in paths:
        with open(p) as f:
            orte += json.load(f)["orte"]
    cache = load_cache()
    titles = {"en": set(), "de": set(), "zh": set()}
    for o in orte:
        for lang, t in (o.get("_wiki") or {}).items():
            if t and lang in titles:
                titles[lang].add(t)
    resolved = {lang: resolve_titles(lang, sorted(ts), cache) for lang, ts in titles.items()}

    # Bilder: aus dem englischen Artikel, sonst aus dem deutschen, sonst chinesisch
    src_page = {}
    for o in orte:
        w = o.get("_wiki") or {}
        for lang in ("en", "de", "zh"):
            r = resolved[lang].get(w.get(lang)) if w.get(lang) else None
            if r:
                src_page[o["id"]] = (lang, r)
                break
    by_lang = {}
    for lang, r in src_page.values():
        by_lang.setdefault(lang, set()).add(r["title"])
    imgs = {lang: page_images(lang, sorted(ts), cache) for lang, ts in by_lang.items()} if bilder else {}

    cand = {}
    for o in orte:
        if o["id"] not in src_page or not bilder:
            continue
        lang, r = src_page[o["id"]]
        files = [f for f in imgs[lang].get(r["title"], []) if not BAD.search(f)
                 and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        if r.get("lead") and r["lead"] in files:
            files.remove(r["lead"])
            files.insert(0, r["lead"])
        elif r.get("lead") and not BAD.search(r["lead"]):
            files.insert(0, r["lead"])
        cand[o["id"]] = files[:12]
    info = image_info([f for fs in cand.values() for f in fs], cache)

    out = {}
    for o in orte:
        w = o.get("_wiki") or {}
        quellen = []
        for lang in ("de", "en", "zh"):
            r = resolved[lang].get(w.get(lang)) if w.get(lang) else None
            if r:
                quellen.append(r["url"])
        bilder, credits = [], []
        for f in cand.get(o["id"], []):
            i = info.get(f)
            if not i or not i["thumb"] or (i["w"] or 0) < 640:
                continue
            if i["h"] and i["w"] and i["h"] > i["w"] * 1.6:
                continue  # extreme Hochformate meiden
            bilder.append(i["thumb"])
            credits.append({"datei": f, "autor": i["artist"], "lizenz": i["license"],
                            "seite": i["page"], "beschreibung": i["desc"]})
            if len(bilder) == 4:
                break
        lat = lon = None
        for lang in ("en", "de", "zh"):
            r = resolved[lang].get(w.get(lang)) if w.get(lang) else None
            if r and r.get("lat") is not None:
                lat, lon = round(r["lat"], 4), round(r["lon"], 4)
                break
        out[o["id"]] = {"lat": lat, "lon": lon, "quellen": quellen, "bilder": bilder, "credits": credits,
                        "wiki_fehlt": [lang for lang, t in w.items() if t and not resolved.get(lang, {}).get(t)]}
    dst = os.path.join(os.path.dirname(os.path.abspath(paths[0])), "bilder.json")
    with open(dst, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    wenig = [k for k, v in out.items() if len(v["bilder"]) < 2]
    print(f"fertig: {len(out)} Orte, weniger als 2 Bilder: {len(wenig)} {wenig}")
    print("ohne Quelle:", [k for k, v in out.items() if not v["quellen"]])
    print("Titel nicht gefunden:", {k: v["wiki_fehlt"] for k, v in out.items() if v["wiki_fehlt"]})


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--ohne-bilder"]
    main(args, bilder="--ohne-bilder" not in sys.argv)
