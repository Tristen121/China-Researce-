# Auftrag für Text-Agenten (China-Ideen-Atlas)

Du schreibst Einträge für einen visuellen Ideen-Atlas für eine 3-wöchige China-Reise (2.–22. September 2027, 4 Reisende).
Der Reisende filtert nach **Wow-Faktor**: starke Fotomotive, alles, was sich wie eine andere Welt anfühlt (surreal, gigantisch, farbig, futuristisch oder uralt).
Logistik, Zugverbindungen, Preise und Routen sind NICHT gefragt. Alles auf Deutsch.

## Eingabe
`data/parts/ortsliste.tsv` (Tab-getrennt). Bearbeite NUR die Zeilen deines Teils (Spalte `teil`).
`id`, `name`, `name_chinesisch`, `provinz`, `kategorie`, `wow`, `geheimtipp` sind vorgegeben. Übernimm sie unverändert.
Ausnahme: Wenn ein vorgegebener Wert sachlich falsch ist (z. B. falsches chinesisches Zeichen oder falsche Provinz), korrigiere ihn und nenne die Korrektur in deinem Abschlussbericht.

## Ausgabe
Eine JSON-Datei `data/parts/teil-<N>.json`, Format `{"orte": [ ... ]}`, ein Objekt pro Zeile, in der Reihenfolge der Liste:

```json
{
  "id": "…", "name": "…", "name_chinesisch": "…", "provinz": "…", "kategorie": "…",
  "kurzbeschreibung": "2–3 Sätze mit Gefühl für die Atmosphäre: was man sieht, hört, spürt. Konkret, keine Werbefloskeln.",
  "aktivitaeten": ["3–5 kurze Punkte: was man dort machen kann"],
  "foto_tipp": "Beste Tageszeit/Jahreszeit für Fotos. Wenn sich September deutlich unterscheidet (z. B. Reisterrassen grün statt geflutet, Herbstfarben, Regenzeit, Nebel), sag in einem Halbsatz, wie es im September aussieht.",
  "wow": 4,
  "geheimtipp": false,
  "unsicher": false,
  "_wiki": {"en": "Exakter Titel des englischen Wikipedia-Artikels oder null", "de": "Exakter Titel des deutschen Artikels oder null", "zh": "Titel des chinesischen Artikels oder null"}
}
```

## Regeln
- Nur echte, existierende Orte, nichts erfinden. Bei Unsicherheit zu einem Fakt: `"unsicher": true` setzen und den Fakt vorsichtig formulieren, statt etwas zu behaupten.
- Keine Zahlen (Höhen, Längen, Jahreszahlen), bei denen du dir nicht sicher bist. Lieber weglassen.
- Keine Preise, Öffnungszeiten, Anreise, Tickets.
- `_wiki`: Nenne die Artikeltitel so, wie du sie für richtig hältst. Sie werden danach zentral automatisch geprüft und in Quellen- und Bild-URLs umgewandelt. **Ruf die Wikipedia- oder Wikimedia-APIs NICHT selbst auf** (Rate-Limit, die Umgebung wird sonst gesperrt). Wenn ein Ort sicher keinen eigenen Artikel hat, nimm den nächstbesten passenden Artikel (z. B. Stadt oder Region) oder null.
- Du darfst WebSearch für einzelne Faktenchecks nutzen, sparsam.
- Stil: kurze Sätze, keine Emojis, kein „atemberaubend“, „ein Muss“ oder „Paradies“. Schreib so, dass man das Bild im Kopf hat.
- Prüfe am Ende mit `python3 -c "import json;d=json.load(open('data/parts/teil-<N>.json'));print(len(d['orte']))"`, dass die Datei gültiges JSON ist und die richtige Anzahl hat.

## Abschlussbericht (kurz)
Anzahl Einträge, welche du als `unsicher` markiert hast und warum, und vorgeschlagene Korrekturen an der Liste.
