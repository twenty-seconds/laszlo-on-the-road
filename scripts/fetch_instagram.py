#!/usr/bin/env python3
"""
Holt Laszlos neueste Instagram-Posts und legt sie selbst-gehostet in die Seite.

Laeuft serverseitig (GitHub Actions, 1x/Tag) — NICHT im Browser der Besucher.
Dadurch: keine Drittanbieter-Skripte, keine Cookies, kein Consent-Banner noetig.

Nutzt die "Instagram API with Instagram Login" (graph.instagram.com).
Benoetigt einen langlebigen Access-Token (GitHub-Secret IG_TOKEN).
Stdlib-only — keine Abhaengigkeiten.

Verhalten ohne Token: bricht sauber ab und laesst vorhandene Daten unangetastet
(so kann das Skript lokal ohne Geheimnis laufen, ohne etwas kaputtzumachen).
"""

import json
import os
import sys
import urllib.request
import urllib.error

API_VERSION = os.environ.get("IG_API_VERSION", "v21.0")
TOKEN = os.environ.get("IG_TOKEN", "").strip()
LIMIT = int(os.environ.get("IG_LIMIT", "8"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "instagram")
DATA_FILE = os.path.join(ROOT, "data", "instagram.json")

FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp"


def log(msg):
    print(f"[instagram] {msg}")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "laszlo-on-the-road/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "laszlo-on-the-road/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def clean_caption(text, maxlen=160):
    if not text:
        return ""
    text = " ".join(text.split())
    return text if len(text) <= maxlen else text[: maxlen - 1].rstrip() + "…"


def main():
    if not TOKEN:
        log("Kein IG_TOKEN gesetzt — ueberspringe Abruf, bestehende Daten bleiben.")
        # Exit 0, damit lokale Laeufe / Builds ohne Secret nicht scheitern.
        return 0

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    url = (
        f"https://graph.instagram.com/{API_VERSION}/me/media"
        f"?fields={FIELDS}&limit={LIMIT}&access_token={TOKEN}"
    )
    try:
        payload = fetch_json(url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        log(f"HTTP-Fehler {e.code}: {body}")
        return 1
    except Exception as e:  # noqa: BLE001
        log(f"Abruf fehlgeschlagen: {e}")
        return 1

    items = payload.get("data", [])
    if not items:
        log("Keine Medien erhalten.")
        return 0

    posts = []
    idx = 0
    for media in items:
        mtype = media.get("media_type")
        # Bei Videos das Vorschaubild nutzen, sonst das Bild selbst.
        src = media.get("thumbnail_url") if mtype == "VIDEO" else media.get("media_url")
        if not src:
            continue
        fname = f"ig-{idx}.jpg"
        dest = os.path.join(IMG_DIR, fname)
        try:
            size = download(src, dest)
        except Exception as e:  # noqa: BLE001
            log(f"Bild-Download fehlgeschlagen ({media.get('id')}): {e}")
            continue
        posts.append(
            {
                "img": f"assets/instagram/{fname}",
                "permalink": media.get("permalink", "https://www.instagram.com/laszlo.healing.oasis/"),
                "caption": clean_caption(media.get("caption", "")),
                "timestamp": media.get("timestamp", ""),
            }
        )
        log(f"gespeichert: {fname} ({size} bytes)")
        idx += 1

    out = {
        "handle": "laszlo.healing.oasis",
        "profile": "https://www.instagram.com/laszlo.healing.oasis/",
        "posts": posts,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    log(f"{len(posts)} Posts in data/instagram.json geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
