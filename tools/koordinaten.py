#!/usr/bin/env python3
"""Holt Koordinaten fuer alle Orte von OpenStreetMap Nominatim (max. 1 Anfrage/Sekunde).

Sucht zuerst mit dem chinesischen Namen, dann mit dem Namen + Provinz. Treffer ausserhalb
Chinas werden verworfen. Schreibt data/parts/koordinaten.json: {id: {lat, lon, treffer, approx}}.
Bestehende Eintraege bleiben, nur fehlende werden gesucht.
"""
import glob
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "ChinaIdeenAtlas/1.0 (+https://github.com/Tristen121/China-Researce-)"
DST = os.path.join(ROOT, "data", "parts", "koordinaten.json")


def suche(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "accept-language": "de"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    time.sleep(1.5)
    if not res:
        return None
    lat, lon = float(res[0]["lat"]), float(res[0]["lon"])
    if not (17 < lat < 54 and 73 < lon < 136):
        return None
    return {"lat": round(lat, 4), "lon": round(lon, 4), "treffer": res[0].get("display_name", "")[:120],
            "typ": res[0].get("type")}


def main():
    orte = []
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "parts", "teil-*.json"))):
        orte += json.load(open(p))["orte"]
    out = json.load(open(DST)) if os.path.exists(DST) else {}
    for o in orte:
        if o["id"] in out:
            continue
        zh = re.split(r"[ /（(]", o["name_chinesisch"])[0]
        basis = re.sub(r"\s*\(.*?\)", "", o["name"]).split(":")[0]
        versuche = [(zh, False), (f"{basis}, {o['provinz'].split('/')[0].strip()}", False),
                    (o["provinz"].split("/")[0].strip() + ", China", True)]
        for q, approx in versuche:
            try:
                r = suche(q)
            except Exception as e:  # noqa: BLE001
                print("Fehler", o["id"], e)
                r = None
            if r:
                r["approx"] = approx
                r["suche"] = q
                out[o["id"]] = r
                print(f"{o['id']:20} {q:30} -> {r['lat']}, {r['lon']} {'(ungefaehr)' if approx else ''} {r['treffer'][:60]}")
                break
        json.dump(out, open(DST, "w"), ensure_ascii=False, indent=1)
    print("fertig:", len(out), "ungefaehr:", [k for k, v in out.items() if v.get("approx")])


if __name__ == "__main__":
    main()
