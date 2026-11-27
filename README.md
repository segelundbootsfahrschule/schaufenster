# Schaufenster – Segel-und-Bootsfahrschule.de

Die Präsentation für den Bildschirm im Schaufenster (Raspberry Pi 4, Chromium im Kiosk-Modus).

**Live-Ansicht:** https://segelundbootsfahrschule.github.io/schaufenster/

## Was wo liegt
| Datei | Zweck |
|---|---|
| `index.html` | Die komplette Präsi: Folien, Animationen, Wetter, Kurstermine |
| `assets/` | Logo, Fotos, QR-Code |
| `kurse.json` | Kurstermine – wird **automatisch** einmal pro Woche (montags) aus dem Shop aktualisiert |
| `scripts/kurse.py` | Holt die Termine (Kombi SBF See+Binnen, SRC) aus dem WooCommerce-Shop |
| `.github/workflows/kurse.yml` | Startet `kurse.py` jeden Montag und speichert Änderungen |
| `version.json` | Bei jeder Änderung an der Präsi hochzählen – dann lädt der Bildschirm neu |

## So bleibt alles aktuell
- **Kurstermine:** neue Kurse im Shop anlegen – am nächsten Montag stehen sie hier. Sofort geht's über GitHub → Actions → „Kurstermine aktualisieren“ → „Run workflow“. Die Seite zeigt jeweils den nächsten Termin, der noch nicht begonnen hat.
- **Wetter:** live von Open-Meteo.com, alle 15 Minuten.
- **Präsi ändern:** Änderung hier einspielen, `version.json` hochzählen. Der Raspi holt sich die neue Version alle 5 Minuten.

## Raspberry Pi
Der Raspi holt dieses Repo per `git pull` und zeigt die lokale Kopie an – fällt das WLAN aus, läuft die letzte Version weiter.
