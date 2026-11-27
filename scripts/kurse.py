#!/usr/bin/env python3
"""Holt die Kurstermine (Kombi SBF See+Binnen und SRC) aus dem WooCommerce-Shop
und schreibt sie nach kurse.json neben index.html. Läuft stündlich als GitHub Action.

- Bei einem Fehler wird bis zu 3x mit Pause neu versucht.
- Klappt es trotzdem nicht, bleibt die alte kurse.json stehen und der Lauf gilt als
  erfolgreich (keine Fehler-Mail wegen kurzer Aussetzer der Website).
- Erst wenn die Termine älter als MAX_ALTER_STUNDEN sind, schlägt der Lauf fehl,
  damit GitHub per Mail Bescheid gibt.
"""
import datetime as dt
import html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

SHOP = "https://segel-und-bootsfahrschule.de/wp-json/wc/store/v1/products"
ZIEL = pathlib.Path(__file__).resolve().parent.parent / "kurse.json"
DATUM = re.compile(r"\d{2}\.\d{2}\.\d{2}")
VERSUCHE = 3
PAUSE_SEK = 30
MAX_ALTER_STUNDEN = 48


def hole(suche):
    url = f"{SHOP}?search={urllib.parse.quote(suche)}&per_page=100"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Schaufenster Segel-und-Bootsfahrschule)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        roh = r.read().decode("utf-8", "replace")
        try:
            return json.loads(roh)
        except json.JSONDecodeError:
            raise RuntimeError(f"Shop lieferte kein JSON (HTTP {r.status}, "
                               f"{r.headers.get('Content-Type')}): {roh[:200]!r}")


def eintrag(p):
    preis = int(p["prices"]["price"]) / 10 ** p["prices"]["currency_minor_unit"]
    return {"name": html.unescape(p["name"]), "link": p["permalink"], "preis": preis}


def abrufen():
    return {
        "kombi": [eintrag(p) for p in hole("Kombi SBF") if "Kombi" in p["name"] and DATUM.search(p["name"])],
        "src": [eintrag(p) for p in hole("SRC") if "SRC" in p["name"] and DATUM.search(p["name"])],
        "stand": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
    }


def alter_stunden():
    try:
        stand = dt.datetime.fromisoformat(json.loads(ZIEL.read_text(encoding="utf-8"))["stand"])
        if stand.tzinfo is None:
            stand = stand.replace(tzinfo=dt.timezone.utc)
        return (dt.datetime.now(dt.timezone.utc) - stand).total_seconds() / 3600
    except Exception:
        return float("inf")


for versuch in range(1, VERSUCHE + 1):
    try:
        kurse = abrufen()
        if not kurse["kombi"] and not kurse["src"]:
            raise RuntimeError("Keine Kurse mit Datum gefunden")
        tmp = ZIEL.with_suffix(".tmp")
        tmp.write_text(json.dumps(kurse, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(ZIEL)
        print(f"kurse.json aktualisiert: {len(kurse['kombi'])} Kombi, {len(kurse['src'])} SRC")
        sys.exit(0)
    except Exception as e:
        print(f"Versuch {versuch}/{VERSUCHE} fehlgeschlagen: {e}")
        if versuch < VERSUCHE:
            time.sleep(PAUSE_SEK)

alter = alter_stunden()
if alter > MAX_ALTER_STUNDEN:
    sys.exit(f"Termine seit {alter:.0f} Stunden nicht aktualisiert - bitte prüfen!")
print(f"::warning::Abruf fehlgeschlagen, alte Termine ({alter:.0f} h alt) bleiben stehen.")
