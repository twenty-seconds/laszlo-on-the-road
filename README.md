# Laszlo on the Road

Personality-Website für Laszlo — ayurvedische Massage & Video/Drohne, "on the road".

- Statische Website (HTML/CSS, kein Build).
- Entwurf v1: Mustertexte + Platzhalter (Instagram-Handle, WhatsApp-Nummer, Impressum/Datenschutz-Daten).
- Deployment: GitHub Pages als Muster-Vorschau (analog anderer Markus-Coenen-Kundenseiten).

## Lokal ansehen
```
cd ~/laszlo-on-the-road
python3 -m http.server 8788
# http://127.0.0.1:8788/
```

## Seiten
- index.html — Startseite (Hero, Massage, Video & Drohne, Instagram, Kontakt)
- leistungen.html — Leistungen (Massage-Arten + Video/Drohne im Detail)
- ueber-mich.html — Über mich (Mustergeschichte)
- impressum.html / datenschutz.html — Mustertexte (rechtlich prüfen)

## Instagram-Feed (selbst-gehostet, DSGVO-sauber)
Kein Drittanbieter-Widget — keine Cookies, kein Consent-Banner. Ein GitHub-Action
holt 1x/Tag die neuesten Posts und committet sie in die Seite.

- `scripts/fetch_instagram.py` — Abruf (stdlib-only; ohne Token sauberer No-op)
- `.github/workflows/instagram.yml` — täglicher Cron + manuell auslösbar
- `data/instagram.json` — Feed-Daten (aktuell Beispieldaten)
- Startseite `#ig-grid` lädt die JSON same-origin, mit statischem Fallback

**Aktivierung:** Repo-Secret `IG_TOKEN` (langlebiger Token der „Instagram API with
Instagram Login") setzen. Voraussetzung: Laszlos Konto ist ein Profi-Konto
(Business/Creator). Token ~60 Tage gültig.
