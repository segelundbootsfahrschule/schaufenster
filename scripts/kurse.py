#!/usr/bin/env python3
"""Holt die Kurstermine (Kombi SBF See+Binnen und SRC) aus dem WooCommerce-Shop
und schreibt sie nach kurse.json neben index.html. Läuft stündlich als GitHub Action.
Bei Fehlern bleibt die alte kurse.json stehen."""
import json, html, re, sys, urllib.request, urllib.parse, pathlib, datetime
SHOP = "https://segel-und-bootsfahrschule.de/wp-json/wc/store/v1/products"
ZIEL = pathlib.Path(__file__).resolve().parent.parent / "kurse.json"
DATUM = re.compile(r"\d{2}\.\d{2}\.\d{2}")

def hole(suche):
    url = f"{SHOP}?search={urllib.parse.quote(suche)}&per_page=100"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Schaufenster-Raspi"}), timeout=30) as r:
        return json.load(r)

def eintrag(p):
    name = html.unescape(p["name"])
    preis = int(p["prices"]["price"]) / 10 ** p["prices"]["currency_minor_unit"]
    return {"name": name, "link": p["permalink"], "preis": preis}

try:
    kurse = {
        "kombi": [eintrag(p) for p in hole("Kombi SBF") if "Kombi" in p["name"] and DATUM.search(p["name"])],
        "src":   [eintrag(p) for p in hole("SRC") if "SRC" in p["name"] and DATUM.search(p["name"])],
        "stand": datetime.datetime.now().isoformat(timespec="minutes"),
    }
    if not kurse["kombi"] and not kurse["src"]:
        sys.exit("Keine Kurse gefunden - alte Datei bleibt")
    tmp = ZIEL.with_suffix(".tmp")
    tmp.write_text(json.dumps(kurse, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ZIEL)
    print("kurse.json aktualisiert:", len(kurse["kombi"]), "Kombi,", len(kurse["src"]), "SRC")
except Exception as e:
    sys.exit(f"Fehler beim Abruf: {e} - alte Datei bleibt")
