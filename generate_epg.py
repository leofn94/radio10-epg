import csv
import urllib.request
from datetime import datetime, timedelta
import pytz
import html
import xml.etree.ElementTree as ET # Nueva importación para el XML externo

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
# Tus canales de Google Sheets se mantienen igual
CHANNELS = [
    {"id": "radio10.ar", "name": "Radio 10 AM 710", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?output=csv"},
    {"id": "rivadavia.ar", "name": "Radio Rivadavia AM 630", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1982230184&single=true&output=csv"},
    {"id": "mitre.ar", "name": "Radio Mitre AM 590", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=753334140&single=true&output=csv"},
    {"id": "nacionalclasica.ar", "name": "Radio Nacional clasica FM 96.7", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1242936527&single=true&output=csv"},
    {"id": "clasica.ar", "name": "Radio clasica", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1953325678&single=true&output=csv"},
    {"id": "ciudadmagica.ar", "name": "Ciudad Magica", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=314883977&single=true&output=csv"},
    {"id": "retromagico.ar", "name": "Retro Magico", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1067661478&single=true&output=csv"},
    {"id": "magickids.ar", "name": "Magic Kids", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1797674806&single=true&output=csv"},
    {"id": "locomotion1.ar", "name": "Locomotion 1", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=309534154&single=true&output=csv"},
    {"id": "aztv.ar", "name": "AZTV", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=955136670&single=true&output=csv"},
    {"id": "mitv.ar", "name": "MiTV 1", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=1227571137&single=true&output=csv"},
    {"id": "animestation.ar", "name": "Animestation", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=446220036&single=true&output=csv"},
    {"id": "elmagis.ar", "name": "El Magis", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=267517003&single=true&output=csv"},
    {"id": "retroblast", "name": "retroblast", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=441139638&single=true&output=csv"},
    {"id": "telered.ar", "name": "Telered", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=763195247&single=true&output=csv"},
    {"id": "telesistema.ar", "name": "telesistema", "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1YPyXdfmd2n7W6tAEnS_7aPb1r9j8fmdF_XP-jxi5cYdcZwkx_4t5OEIqYpGzr98wcF4nHUzhbval/pub?gid=503971923&single=true&output=csv"},
]

# CONFIGURACIÓN EPG EXTERNA
EXTERNAL_EPG_URL = "http://epg.programadorx.cl/mdiaz/gratis.xml"
EXTERNAL_CHANNELS_IDS = ["506", "633", "537"]

TIMEZONE = "America/Argentina/Buenos_Aires"
OUTPUT_FILE = "epg.xml"

DAYS_MAP = {
    "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6,
}

# ─── FUNCIONES DE APOYO ──────────────────────────────────────────────────────
def fetch_url(url):
    try:
        with urllib.request.urlopen(url) as r:
            return r.read()
    except Exception as e:
        print(f"❌ Error descargando {url} → {e}")
        return None

def parse_time(t):
    if not t: raise ValueError("Hora vacía")
    t = t.strip().lower().replace("hs", "").replace(".", ":").replace("·", "").replace(" ", "")
    if len(t) >= 5: t = t[:5]
    return datetime.strptime(t, "%H:%M").time()

def xmltv_ts(dt):
    return dt.strftime("%Y%m%d%H%M%S") + " -0300"

def get_monday():
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    return today - timedelta(days=today.weekday())

def get_days_from_type(tipo):
    tipo = tipo.lower()
    if tipo == "weekdays": return [0,1,2,3,4]
    elif tipo == "weekend": return [5,6]
    elif tipo in DAYS_MAP: return [DAYS_MAP[tipo]]
    return []

# ─── PROCESAMIENTO EPG EXTERNA ───────────────────────────────────────────────
def fetch_external_epg_data(url, target_ids):
    print(f"Descargando EPG externa de {url}...")
    content = fetch_url(url)
    if not content: return []
    
    root = ET.fromstring(content)
    external_data = []
    
    # Extraer canales y programas
    for channel_id in target_ids:
        # Buscar el nombre del canal en el XML original
        ch_node = root.find(f"./channel[@id='{channel_id}']")
        ch_name = ch_node.find("display-name").text if ch_node is not None else f"Extra {channel_id}"
        
        programmes = []
        # Buscar programas de este canal
        for prog in root.findall(f"./programme[@channel='{channel_id}']"):
            # En el XML original las fechas ya vienen en formato XMLTV
            # Para mantener compatibilidad con tu función write_xmltv, 
            # las convertiremos a objetos datetime
            start_str = prog.get("start")
            stop_str = prog.get("stop")
            title = prog.find("title").text if prog.find("title") is not None else "Sin título"
            desc = prog.find("desc").text if prog.find("desc") is not None else ""
            
            # Formato esperado: 20240414000000 +0000
            fmt = "%Y%m%d%H%M%S %z"
            start_dt = datetime.strptime(start_str, fmt)
            stop_dt = datetime.strptime(stop_str, fmt)
            
            programmes.append((start_dt, stop_dt, title, desc, channel_id))
            
        external_data.append({
            "id": channel_id,
            "name": ch_name,
            "programmes": programmes
        })
    return external_data

# ─── CONSTRUCCIÓN EPG DESDE SHEETS ──────────────────────────────────────────
def build_epg_from_sheets(rows, channel_id):
    tz = pytz.timezone(TIMEZONE)
    monday = get_monday()
    programmes = []
    today = datetime.now(tz).date()
    limit = today + timedelta(days=2)

    for row in rows:
        if len(row) < 4: continue
        row = [col.strip() for col in row]
        tipo, start_raw, end_raw, title = row[0], row[1], row[2], row[3]
        desc = row[4] if len(row) > 4 else ""
        days = get_days_from_type(tipo)

        for day_offset in days:
            date = monday + timedelta(days=day_offset)
            if not (today <= date <= limit): continue
            try:
                start_t, end_t = parse_time(start_raw), parse_time(end_raw)
            except: continue

            start_dt = tz.localize(datetime.combine(date, start_t))
            end_dt = tz.localize(datetime.combine(date, end_t))
            if end_dt <= start_dt: end_dt += timedelta(days=1)

            programmes.append((start_dt, end_dt, title.strip(), desc.strip(), channel_id))
    
    programmes.sort(key=lambda x: x[0])
    return programmes

# ─── GENERADOR XML FINAL ─────────────────────────────────────────────────────
def write_xmltv(channels_data):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE tv SYSTEM "xmltv.dtd">',
        '<tv generator-info-name="radios-epg">'
    ]

    for ch in channels_data:
        lines.append(f'  <channel id="{ch["id"]}">')
        lines.append(f'    <display-name>{html.escape(ch["name"])}</display-name>')
        lines.append('  </channel>')

    for ch in channels_data:
        for start, end, title, desc, channel_id in ch["programmes"]:
            # Normalizamos el formato de salida de tiempo
            lines.append(f'  <programme start="{xmltv_ts(start)}" stop="{xmltv_ts(end)}" channel="{channel_id}">')
            lines.append(f'    <title lang="es">{html.escape(title)}</title>')
            if desc: lines.append(f'    <desc lang="es">{html.escape(desc)}</desc>')
            lines.append('  </programme>')

    lines.append('</tv>')
    return "\n".join(lines)

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    all_channels_combined = []

    # 1. Procesar Canales de Google Sheets
    for ch in CHANNELS:
        print(f"Procesando Sheet de {ch['name']}...")
        raw_content = fetch_url(ch["url"])
        if not raw_content: continue
        
        lines = raw_content.decode("utf-8").splitlines()
        rows = list(csv.reader(lines))[1:]
        programmes = build_epg_from_sheets(rows, ch["id"])
        
        all_channels_combined.append({
            "id": ch["id"],
            "name": ch["name"],
            "programmes": programmes,
        })

    # 2. Procesar Canales de EPG Externa
    try:
        external_data = fetch_external_epg_data(EXTERNAL_EPG_URL, EXTERNAL_CHANNELS_IDS)
        all_channels_combined.extend(external_data)
        print(f"✅ Se agregaron {len(external_data)} canales externos.")
    except Exception as e:
        print(f"❌ Error procesando EPG externa: {e}")

    # 3. Escribir archivo final
    xml = write_xmltv(all_channels_combined)
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as f:
        f.write(xml)

    print(f"\nEPG completa guardada en {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
