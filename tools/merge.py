#!/usr/bin/env python3
"""Fuehrt data/parts/teil-*.json und data/parts/bilder.json zu data/orte.json zusammen.

Bestehende Eintraege in data/orte.json bleiben erhalten (nie ueberschreiben, siehe CLAUDE.md);
nur Felder, die dort fehlen oder leer sind (bilder, quellen, lat/lon), werden ergaenzt.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["id", "name", "name_chinesisch", "provinz", "kategorie", "kurzbeschreibung",
          "aktivitaeten", "foto_tipp", "wow", "geheimtipp", "unsicher", "bilder", "quellen",
          "lat", "lon", "bild_credits"]


def main():
    parts = []
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "parts", "teil-*.json"))):
        with open(p) as f:
            parts += json.load(f)["orte"]
    bpath = os.path.join(ROOT, "data", "parts", "bilder.json")
    bilder = json.load(open(bpath)) if os.path.exists(bpath) else {}
    fotos = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "parts", "fotos-*.json"))):
        with open(p) as f:
            fotos.update(json.load(f))
    dst = os.path.join(ROOT, "data", "orte.json")
    alt = {o["id"]: o for o in json.load(open(dst))["orte"]} if os.path.exists(dst) else {}

    out, seen = [], set()
    for o in parts:
        if o["id"] in seen:
            raise SystemExit(f"doppelte id: {o['id']}")
        seen.add(o["id"])
        b = bilder.get(o["id"], {})
        neu = dict(o)
        neu.pop("_wiki", None)
        neu["bilder"] = b.get("bilder", [])
        neu["bild_credits"] = [{k: c.get(k) for k in ("datei", "autor", "lizenz", "seite")}
                               for c in b.get("credits", [])]
        lokal = [x for x in fotos.get(o["id"], []) if os.path.exists(os.path.join(ROOT, x["datei"]))]
        if lokal:
            neu["bilder"] = [x["datei"] for x in lokal][:4]
            neu["bild_credits"] = [{"autor": x.get("credit"), "seite": x.get("seite")} for x in lokal][:4]
        neu["quellen"] = b.get("quellen", [])
        neu["lat"], neu["lon"] = b.get("lat"), b.get("lon")
        if o["id"] in alt:
            fertig = dict(alt[o["id"]])
            for k in ("bilder", "bild_credits", "quellen", "lat", "lon"):
                if not fertig.get(k) and neu.get(k):
                    fertig[k] = neu[k]
            neu = fertig
        out.append({k: neu.get(k) for k in FIELDS if k in neu} | {k: v for k, v in neu.items() if k not in FIELDS})
    for i, o in alt.items():
        if i not in seen:
            out.append(o)

    with open(dst, "w") as f:
        json.dump({"orte": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = len(out)
    gt = sum(1 for o in out if o.get("geheimtipp"))
    kats = {}
    for o in out:
        kats[o["kategorie"]] = kats.get(o["kategorie"], 0) + 1
    print(f"{n} Orte, {gt} Geheimtipps ({gt * 100 // n} %), Provinzen: {len({o['provinz'] for o in out})}")
    print("pro Kategorie:", kats)
    print("unter 2 Bildern:", [o["id"] for o in out if len(o.get("bilder") or []) < 2])
    print("ohne Quelle:", [o["id"] for o in out if not o.get("quellen")])
    print("ohne Koordinaten:", [o["id"] for o in out if o.get("lat") is None])


if __name__ == "__main__":
    main()
