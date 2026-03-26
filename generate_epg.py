import csv
import urllib.request
from datetime import datetime, timedelta
import pytz
import re

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
CHANNELS = [
    {
        "id":   "animestation.ar",
        "name": "Animestation",
        "url":  "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=446220036&single=true&output=csv",
    },
]

TIMEZONE    = "America/Argentina/Buenos_Aires"
OUTPUT_FILE = "epg.xml"

DAYS_MAP = {
    "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6,
}

def fetch_sheet(url):
    try:
        with urllib.request.urlopen(url) as r:
            return r.read().decode("utf-8").splitlines()
    except Exception as e:
        print(f"❌ Error descargando {url} → {e}")
        return []

#  NUEVO PARSER
def parse_time(t):
    if not t:
        raise ValueError("Hora vacía")

    t = t.strip()

    # limpiar basura común
    t = t.replace("hs", "")
    t = t.replace(".", ":")
    t = t.replace("·", "")
    t = t.replace(" ", "")

    # cortar segundos si vienen
    if len(t) >= 5:
        t = t[:5]

    return datetime.strptime(t, "%H:%M").time()

def xmltv_ts(dt):
    return dt.strftime("%Y%m%d%H%M%S") + " -0300"

def get_monday():
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    return today - timedelta(days=today.weekday())

def build_epg(rows, channel_id):
    tz = pytz.timezone(TIMEZONE)
    monday = get_monday()
    programmes = []

    for i, row in enumerate(rows, start=1):
        try:
            if len(row) < 4:
                continue

            day_raw, start_raw, end_raw, title = row[0], row[1], row[2], row[3]
            desc = row[4] if len(row) > 4 else ""

            day_key = day_raw.strip().lower()
            if day_key not in DAYS_MAP:
                continue

            offset = DAYS_MAP[day_key]
            date = monday + timedelta(days=offset)

            try:
                start_t = parse_time(start_raw)
                end_t   = parse_time(end_raw)
            except Exception as e:
                 print(f"⚠️ Error en fila {row}")
                 continue

            start_dt = tz.localize(datetime.combine(date, start_t))
            end_dt   = tz.localize(datetime.combine(date, end_t))

            if end_dt <= start_dt:
                end_dt += timedelta(days=1)

            programmes.append((start_dt, end_dt, title.strip(), desc.strip(), channel_id))

        except Exception as e:
            print(f"⚠️ Error en fila {i} ({channel_id}): {row} → {e}")
            continue

    programmes.sort(key=lambda x: x[0])
    return programmes

def write_xmltv(channels_data):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE tv SYSTEM "xmltv.dtd">')
    lines.append('<tv generator-info-name="radios-epg">')

    for ch in channels_data:
        lines.append(f'  <channel id="{ch["id"]}">')
        lines.append(f'    <display-name>{ch["name"]}</display-name>')
        lines.append('  </channel>')

    for ch in channels_data:
        for start, end, title, desc, channel_id in ch["programmes"]:
            lines.append(
                f'  <programme start="{xmltv_ts(start)}" stop="{xmltv_ts(end)}" channel="{channel_id}">'
            )
            lines.append(f'    <title lang="es">{title}</title>')
            if desc:
                lines.append(f'    <desc lang="es">{desc}</desc>')
            lines.append('  </programme>')

    lines.append('</tv>')
    return "\n".join(lines)

def main():
    channels_data = []

    for ch in CHANNELS:
        print(f"Descargando grilla de {ch['name']}...")

        raw = fetch_sheet(ch["url"])
        if not raw:
            print(f"⚠️ Saltando canal {ch['name']} por error de descarga")
            continue

        rows = list(csv.reader(raw))[1:]
        print(f"  {len(rows)} filas encontradas")

        programmes = build_epg(rows, ch["id"])
        print(f"  {len(programmes)} programas generados")

        channels_data.append({
            "id": ch["id"],
            "name": ch["name"],
            "programmes": programmes,
        })

    xml = write_xmltv(channels_data)

    # 🔥 limpieza BOM / basura
    xml = xml.encode("utf-8").decode("utf-8-sig").lstrip()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"\nEPG guardado en {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
    
