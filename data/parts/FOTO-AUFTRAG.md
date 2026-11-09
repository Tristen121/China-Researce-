# Auftrag für Foto-Agenten (China-Ideen-Atlas)

Arbeitsverzeichnis: /home/user/China-Researce-
Ziel: Für jeden deiner Orte **3 starke Fotos des Orts selbst**. Der Atlas ist bildlastig und filtert nach Wow-Faktor, also das Motiv, das den Ort berühmt macht (z. B. Zhangjiajie: Sandsteinsäulen im Nebel, nicht das Eingangstor).
Die Daten der Orte (Name, chinesischer Name, Provinz, Beschreibung) stehen in data/parts/teil-1.json, teil-2.json, teil-3.json. Lies nur die Einträge deiner IDs, ändere diese Dateien nicht.

## Quellen
- Beliebige Webseiten sind erlaubt (das Repo wird privat, private Familienplanung): Reiseseiten, Trip.com, Travel China Guide, Blogs, Unsplash, Pexels, Flickr, Baidu Baike, Nachrichtenseiten.
- **Nicht** Wikimedia/Wikipedia-Bildserver (upload.wikimedia.org, commons): die Umgebung ist dort gesperrt (HTTP 429).
- Vorgehen: WebSearch nach dem Ort (gern auch mit chinesischem Namen), dann WebFetch auf gute Seiten und nach direkten Bild-URLs fragen (.jpg/.jpeg/.png/.webp, möglichst groß).

## Herunterladen
- Nur so: `python3 -I tools/foto.py <id> <n> "<bild-url>"` mit n = 1, 2, 3. Das Skript lädt, prüft Mindestgröße und speichert `img/<id>-<n>.jpg` (max. 1000 px).
- Das Skript nutzt einen ehrlichen User-Agent. Wenn ein Server ablehnt (403, 429, Fehler): **nicht** mit anderem User-Agent, curl-Tricks oder Proxies umgehen, sondern eine andere Quelle nehmen.
- Kein Bild herunterladen, das nicht über diese Befehle läuft.

## Ansehen (Pflicht)
- Danach `KONTAKT_DIR=/tmp/claude-0/-home-user/cb615220-ecc2-595f-8e98-930eedf7a5e5/scratchpad python3 -I tools/foto.py --kontakt <id>` und das ausgegebene PNG mit dem Read-Tool ansehen.
- Aussortieren und ersetzen: falscher Ort, Logos, Karten, Textbanner, große Wasserzeichen, Collagen, Screenshots, unscharfe oder winzige Bilder, Menschen-Porträts ohne Ort. Drei fast gleiche Bilder vermeiden, lieber drei Perspektiven.
- Ein ersetztes Foto einfach mit derselben Nummer neu laden (überschreibt).

## Ausgabe
`data/parts/fotos-<N>.json`:
```json
{"zhangjiajie": [
  {"datei": "img/zhangjiajie-1.jpg", "seite": "https://… (Seite, von der das Bild stammt)", "credit": "Fotograf oder Seitenname"},
  …
]}
```
- Wenn du nach ehrlicher Suche nur 2 gute Fotos findest: 2 eintragen. Weniger als 2: im Bericht nennen.
- Keine Git-Befehle. Keine anderen Dateien ändern.

## Abschlussbericht (kurz)
Anzahl Orte, Anzahl Fotos, welche Orte weniger als 3 Fotos haben und warum.
