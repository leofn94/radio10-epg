import csv
import urllib.request
from datetime import datetime, timedelta
import pytz

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
# Reemplazá SHEET_ID con el ID de tu Google Sheet (ver instrucciones abajo)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?output=csv"


CHANNEL_ID   = "radio10.ar"
CHANNEL_NAME = "Radio 10 AM 710"
TIMEZONE     = "America/Argentina/Buenos_Aires"
OUTPUT_FILE  = "epg.xml"
# ──────────────────────────────────────────────────────────────────────────────

DAYS_MAP = {
    "lunes":    0,
    "martes":   1,
    "miercoles":2,
    "miércoles":2,
    "jueves":   3,
    "viernes":  4,
    "sabado":   5,
    "sábado":   5,
    "domingo":  6,
}

def fetch_sheet():
    with urllib.request.urlopen(SHEET_URL) as r:
        return r.read().decode("utf-8").splitlines()

def parse_time(t):
    return datetime.strptime(t.strip(), "%H:%M").time()

def xmltv_ts(dt):
    return dt.strftime("%Y%m%d%H%M%S") + " -0300"

def get_monday():
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    return today - timedelta(days=today.weekday())  # lunes de esta semana

def build_epg(rows):
    tz = pytz.timezone(TIMEZONE)
    monday = get_monday()
    programmes = []

    for row in rows:
        if len(row) < 4:
            continue
        day_raw, start_raw, end_raw, title = row[0], row[1], row[2], row[3]
        desc = row[4] if len(row) > 4 else ""

        day_key = day_raw.strip().lower()
        if day_key not in DAYS_MAP:
            continue

        offset = DAYS_MAP[day_key]
        date = monday + timedelta(days=offset)

        start_t = parse_time(start_raw)
        end_t   = parse_time(end_raw)

        start_dt = tz.localize(datetime.combine(date, start_t))
        end_dt   = tz.localize(datetime.combine(date, end_t))

        # Si la hora de fin es menor que la de inicio, el programa cruza medianoche
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        programmes.append((start_dt, end_dt, title.strip(), desc.strip()))

    programmes.sort(key=lambda x: x[0])
    return programmes

def write_xmltv(programmes):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE tv SYSTEM "xmltv.dtd">')
    lines.append('<tv generator-info-name="radio10-epg">')
    lines.append(f'  <channel id="{CHANNEL_ID}">')
    lines.append(f'    <display-name>{CHANNEL_NAME}</display-name>')
    lines.append( '  </channel>')

    for start, end, title, desc in programmes:
        lines.append(
            f'  <programme start="{xmltv_ts(start)}" '
            f'stop="{xmltv_ts(end)}" channel="{CHANNEL_ID}">'
        )
        lines.append(f'    <title lang="es">{title}</title>')
        if desc:
            lines.append(f'    <desc lang="es">{desc}</desc>')
        lines.append( '  </programme>')

    lines.append('</tv>')
    return "\n".join(lines)

def main():
    print("Descargando grilla desde Google Sheets...")
    raw = fetch_sheet()
    reader = csv.reader(raw)
    rows = list(reader)
    rows = rows[1:]  # saltar encabezado

    print(f"  {len(rows)} filas encontradas")
    programmes = build_epg(rows)
    print(f"  {len(programmes)} programas generados")

    xml = write_xmltv(programmes)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  EPG guardado en {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
