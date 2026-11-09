# CLAUDE.md – China-Ideen-Atlas

Quelle dieser Datei: das Dokument https://claude.ai/artifact/XuJRm5tMd7GozvmFdMafrq (Stand 2026-11-09). Ändert sich das Dokument, diese Datei nachziehen.

## Ziel
Du baust einen visuellen Ideen-Atlas für eine 3-wöchige China-Reise. Die Route steht noch nicht fest. Sammle eine möglichst BREITE Auswahl an Orten und Erlebnissen in ganz China, ähnlich wie TripAdvisor, aber gefiltert auf meinen Geschmack. Breite vor Tiefe. Logistik, Zugverbindungen, Preise und Routen sind NICHT gefragt.

## Mein wichtigster Filter: Wow-Faktor
- Orte, an denen man richtig starke Fotos machen kann
- Alles, was sich wie eine andere Welt anfühlt: surreal, gigantisch, farbig, futuristisch oder uralt
- Bewerte jeden Ort mit `wow` von 1 bis 5. Unter 3 nur aufnehmen, wenn es ein absoluter Klassiker ist.

## Was mich interessiert (Startpunkte, nicht abschließend)
- Spektakuläre Berge und Felsen, z. B. Tianmen-Berg / Heaven's Gate, Zhangjiajie
- Wandern, z. B. durch Reisterrassen
- Chinesische Mauer, gern wilde Abschnitte mit Trekking und Zelt
- Tempel und Pagoden, z. B. Sonne-und-Mond-Pagoden in Guilin
- Großstädte erleben: Peking, Shenzhen mit dem Fahrrad, Neon-Skylines
- Camping: gern ab und zu, aber kein Schwerpunkt
- Klassische Touristen-Highlights ebenfalls aufnehmen

## Kategorien
Natur und Landschaft, Wandern und Outdoor, Kultur und Tempel, Städte und Futuristisches, Essen und Märkte, Abenteuer, Ungewöhnliches. Pro Kategorie mindestens 10 Einträge, verteilt über möglichst viele Provinzen.

## Überrasch mich
Mindestens 20 % der Einträge sollen Geheimtipps sein, die ich wahrscheinlich nicht kenne: wenig bekannte Landschaften, skurrile Orte, besondere Feste oder Naturphänomene. Markiere sie mit `geheimtipp: true`.

## Datenformat
Alle Orte stehen in `data/orte.json`. Jeder Eintrag enthält: `id`, `name`, `name_chinesisch`, `provinz`, `kategorie`, `kurzbeschreibung` (2–3 Sätze, mit Gefühl für die Atmosphäre), `aktivitaeten` (Liste: was man dort machen kann), `foto_tipp` (beste Tageszeit oder Jahreszeit für Fotos), `wow` (1–5), `geheimtipp` (true/false), `bilder` (2–4 URLs), `quellen`. Bilder bevorzugt als direkte Bild-URLs von Wikimedia Commons, damit sie zuverlässig laden.

## Ausgabe: index.html
- Eine einzige HTML-Datei ohne Build-Schritt, die `data/orte.json` lädt
- Kachel-Ansicht: pro Ort ein Block mit Bildergalerie (durchklickbar), Name, Provinz, Beschreibung, Aktivitäten, Foto-Tipp, Wow-Sterne
- Pro Kachel zwei Buttons: „Interessiert mich“ und „Nicht interessant“
- Filter: Alle, Interessant, Aussortiert, Unbewertet, dazu Kategorie, Geheimtipps und Wow-Wert
- Optional: kleine China-Karte, auf der die Orte als Punkte erscheinen
- Bewertungen im Browser speichern (localStorage) und per Button als `bewertungen.json` exportieren
- Modernes, bildlastiges Design, dunkler Hintergrund, große Fotos

## Lernschleife
Wenn `bewertungen.json` im Repo liegt: lies sie, erkenne Muster in dem, was ich mag und ablehne, und erweitere die Sammlung beim nächsten Durchlauf gezielt in diese Richtung. Abgelehnte Orte nicht erneut vorschlagen. Schreib eine kurze Zusammenfassung der erkannten Vorlieben in `vorlieben.md`.

## Arbeitsweise
- Nur echte, existierende Orte. Nichts erfinden.
- Bei Unsicherheit den Eintrag mit `unsicher: true` markieren.
- Neue Funde ergänzen, Bestehendes und meine Bewertungen nie überschreiben.
- Erster Durchlauf: mindestens 70 Orte sammeln, dann index.html bauen.

---

## Technik (ergänzt von Claude)
- Zusätzliche Felder pro Ort: `unsicher`, `lat`/`lon` (aus Wikipedia, für die Karte; fehlt, wenn Wikipedia keine Koordinaten hat), `bild_credits` (Fotograf oder Seite und Quellseite je Bild).
- Bilder: Abweichend von „bevorzugt Wikimedia“ liegen die Fotos lokal in `img/<id>-<n>.jpg` (max. 1000 px). Grund: Wikimedia blockt die Cloud-Umgebung (429), und Tristan hat am 2026-11-09 erlaubt, auch andere Bildquellen zu nutzen. Weil darunter urheberrechtlich geschützte Fotos sind, muss das Repo **privat** bleiben. Fotos lädt `tools/foto.py`; Ablauf und Prüfregeln in `data/parts/FOTO-AUFTRAG.md`.
- `tools/wiki_bilder.py` prüft die Wikipedia-Titel (`_wiki` in `data/parts/teil-*.json`) und holt echte Quellen-URLs, Koordinaten und Bild-URLs aus den Artikeln. Wikimedia drosselt Cloud-Umgebungen stark (HTTP 429): das Skript fragt gebündelt und langsam ab und speichert in `tools/cache/`. Nie den User-Agent fälschen, um die Drosselung zu umgehen.
- `tools/merge.py` führt `data/parts/teil-*.json` + `data/parts/bilder.json` zu `data/orte.json` zusammen. Neue Orte für spätere Durchläufe: neue Teil-Datei anlegen, nie bestehende Einträge überschreiben.
- Ansehen: `index.html` lädt `data/orte.json` per `fetch`. Direkt als Datei geöffnet blockiert der Browser das; dann im Repo `python3 -m http.server` starten und http://localhost:8000 öffnen (oder in der Seite die `orte.json` per Dateiauswahl laden).

## Aktivitäten (Tristan, 2026-11-09)
- An jedem Ort braucht man Dinge, die man dort **machen** kann. `aktivitaeten`: 4–6 konkrete Punkte, mindestens 2 zum Selbermachen (Wanderroute, Bootsfahrt, Rad, Gericht, Kurs, Nachtmarkt, Übernachtung …), höchstens 1 reines Fotografieren. Details: `data/parts/AKTIVITAETEN-AUFTRAG.md`.

## Stand
- 2026-11-09: Erster Durchlauf, 95 Orte in 7 Kategorien, 30 Provinzen, 40 Geheimtipps (42 %). Texte von Sonnet-Agenten, Faktenprüfung durch Opus (`data/parts/review.md`), Aktivitäten neu geschrieben und geprüft (`data/parts/review-aktivitaeten.md`). 284 Fotos (2–3 pro Ort), bei 13 Orten nur Symbolfotos (`foto_hinweis`).
- Ansehen mit allen Fotos: privates Artifact https://claude.ai/artifact/FPDLBwEgCSQmwQRSHX5Hfv (beim Aktualisieren `data/orte.json` und neue Fotos dorthin mitveröffentlichen).
- Offen: Repo ist noch öffentlich, deshalb ist `img/` in `.gitignore` und die Fotos fehlen im Repo. Sobald Tristan es auf privat stellt: `img/` aus `.gitignore` nehmen, Fotos committen. Die Fotos liegen bis dahin nur in der Cloud-Sitzung und im Artifact.
- Noch keine `bewertungen.json`, also noch keine Lernschleife.
