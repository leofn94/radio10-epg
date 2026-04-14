import csv
import urllib.request
from datetime import datetime, timedelta
import pytz
import html
import xml.etree.ElementTree as ET

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

# 1. CANALES DESDE GOOGLE SHEETS
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

# 2. FUENTES XML EXTERNAS
# Aquí puedes agregar todas las URLs y los IDs de canales que quieras extraer.
EXTERNAL_SOURCES = [
    {
        "url": "https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/vilma/guia-de-programacion.xml",
        "ids": ["0855", "0533", "0839", "XXX8", "0861", "0827", "0528", "0135","0860"]
    }
    ,{
        "url": "https://epg.programadorx.cl/mdiaz/gratis.xml",
        "ids": ["503dtv.cl", "504", "517dtv.cl", "531", "532", "536", "537", "538", "539", "567", "568", "569", "581", "608", "663", "664", "1503dtv.cl"]
     }
   # ,{
   #     "url": "https://raw.githubusercontent.com/luisms123/tdt/master/guiaxmltv.xml",
   #    "ids": ["Magic Kids Tv", "Zaz TV", "Ani Retro", "Dreiko TV", "El Chavo", "Cine Sony", "Frecuencia Musical TV", "Tv Retro Palmares"]
   #  }
  #    Ejemplo de cómo agregar otra fuente:
    # ,{
    #    "url": "https://otra-fuente.com/guia.xml",
    #    "ids": ["Canal1", "Canal2"]
    # }
]

TIMEZONE = "America/Argentina/Buenos_Aires"
OUTPUT_FILE = "epg.xml"

# ─── FUNCIONES DE APOYO ──────────────────────────────────────────────────────

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as r:
            return r.read()
    except Exception as e:
        print(f"  ❌ Error de conexión con {url} → {e}")
        return None

def parse_time(t):
    if not t: raise ValueError("Hora vacía")
    t = t.strip().lower().replace("hs", "").replace(".", ":").replace("·", "").replace(" ", "")
    if len(t) >= 5: t = t[:5]
    return datetime.strptime(t, "%H:%M").time()

def xmltv_ts(dt):
    # Formato estándar XMLTV: AAAAMMDDHHMMSS +HHMM
    return dt.strftime("%Y%m%d%H%M%S %z")

def get_monday():
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    return today - timedelta(days=today.weekday())

def get_days_from_type(tipo):
    tipo = tipo.lower()
    days_map = {
        "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
        "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6,
    }
    if tipo == "weekdays": return [0, 1, 2, 3, 4]
    elif tipo == "weekend": return [5, 6]
    elif tipo in days_map: return [days_map[tipo]]
    return []

# ─── PROCESAMIENTO EPG EXTERNA ───────────────────────────────────────────────

def process_external_sources(sources):
    data = []
    # Definimos la zona horaria de Argentina para la conversión
    tz_arg = pytz.timezone(TIMEZONE)
    
    for source in sources:
        url = source["url"]
        target_ids = source["ids"]
        
        print(f"\nDescargando EPG externa de {url}...")
        raw_xml = fetch_url(url)
        if not raw_xml: continue
        
        try:
            root = ET.fromstring(raw_xml)
            for ch_id in target_ids:
                ch_node = root.find(f"./channel[@id='{ch_id}']")
                ch_name = ch_node.find("display-name").text if ch_node is not None else f"Extra {ch_id}"
                
                programmes = []
                for prog in root.findall(f"./programme[@channel='{ch_id}']"):
                    fmt = "%Y%m%d%H%M%S %z"
                    # 1. Leemos la fecha original (venga con el offset que venga)
                    s_dt = datetime.strptime(prog.get("start"), fmt)
                    e_dt = datetime.strptime(prog.get("stop"), fmt)
                    
                    # 2. La convertimos a la hora de Argentina (-0300)
                    s_dt = s_dt.astimezone(tz_arg)
                    e_dt = e_dt.astimezone(tz_arg)
                    
                    title = prog.find("title").text if prog.find("title") is not None else "Sin título"
                    desc = prog.find("desc").text if prog.find("desc") is not None else ""
                    
                    programmes.append((s_dt, e_dt, title, desc, ch_id))
                
                print(f"  ✅ Canal Externo: {ch_name} [{ch_id}] → {len(programmes)} programas (normalizados a -0300)")
                data.append({"id": ch_id, "name": ch_name, "programmes": programmes})
        except Exception as e:
            print(f"  ❌ Error procesando XML: {e}")
    return data
    
# ─── CONSTRUCCIÓN EPG DESDE SHEETS (CON VENTANA DE 3 DÍAS) ───────────────────

def build_epg_from_sheets(rows, channel_id):
    tz = pytz.timezone(TIMEZONE)
    monday = get_monday()
    programmes = []
    
    now = datetime.now(tz)
    today = now.date()
    # Límite: Hoy + 3 días
    limit_date = today + timedelta(days=3)

    for row in rows:
        if len(row) < 4: continue
        row = [col.strip() for col in row]
        tipo, start_raw, end_raw, title = row[0], row[1], row[2], row[3]
        desc = row[4] if len(row) > 4 else ""
        
        days_to_apply = get_days_from_type(tipo)

        for day_offset in days_to_apply:
            target_date = monday + timedelta(days=day_offset)
            
            # Filtro de ventana de tiempo (3 días)
            if not (today <= target_date <= limit_date):
                continue
            
            try:
                s_t, e_t = parse_time(start_raw), parse_time(end_raw)
                s_dt = tz.localize(datetime.combine(target_date, s_t))
                e_dt = tz.localize(datetime.combine(target_date, e_t))
                
                if e_dt <= s_dt:
                    e_dt += timedelta(days=1)
                
                programmes.append((s_dt, e_dt, title, desc, channel_id))
            except:
                continue
    
    programmes.sort(key=lambda x: x[0])
    return programmes

# ─── GENERADOR XML ───────────────────────────────────────────────────────────

def write_final_xml(channels_data):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE tv SYSTEM "xmltv.dtd">',
        '<tv generator-info-name="radios-epg-custom">'
    ]

    # Escribir Cabeceras de Canales
    for ch in channels_data:
        name = ch.get("name") or "Canal sin nombre"
        lines.append(f'  <channel id="{ch["id"]}">')
        lines.append(f'    <display-name>{html.escape(str(name))}</display-name>')
        lines.append('  </channel>')

    # Escribir Programación
    total_prog_count = 0
    for ch in channels_data:
        for start, end, title, desc, channel_id in ch["programmes"]:
            # Validamos que title y desc no sean None antes de hacer escape
            safe_title = html.escape(str(title)) if title is not None else "Sin título"
            safe_desc = html.escape(str(desc)) if desc is not None else ""

            lines.append(f'  <programme start="{xmltv_ts(start)}" stop="{xmltv_ts(end)}" channel="{channel_id}">')
            lines.append(f'    <title lang="es">{safe_title}</title>')
            if safe_desc:
                lines.append(f'    <desc lang="es">{safe_desc}</desc>')
            lines.append('  </programme>')
            total_prog_count += 1

    lines.append('</tv>')
    return "\n".join(lines), total_prog_count

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    final_data = []
    print("🚀 Iniciando generación de EPG unificada...\n")

    # 1. Procesar Google Sheets
    for ch in CHANNELS:
        content = fetch_url(ch["url"])
        if not content:
            print(f"  ⚠️ Error en Sheet de {ch['name']}")
            continue
        
        csv_lines = content.decode("utf-8").splitlines()
        rows = list(csv.reader(csv_lines))[1:]
        progs = build_epg_from_sheets(rows, ch["id"])
        
        print(f"  📁 Sheet: {ch['name']} → {len(progs)} programas (ventana 3 días)")
        final_data.append({"id": ch["id"], "name": ch["name"], "programmes": progs})

    # 2. Procesar Fuentes Externas
    external_channels = process_external_sources(EXTERNAL_SOURCES)
    final_data.extend(external_channels)

    # 3. Generar archivo y Resumen
    xml_output, total_programs = write_final_xml(final_data)
    
    # Guardar con UTF-8 con BOM para máxima compatibilidad
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as f:
        f.write(xml_output)

    print("\n" + "="*40)
    print("✨ PROCESO FINALIZADO CON ÉXITO")
    print(f"📺 Total Canales: {len(final_data)}")
    print(f"📅 Total Programas: {total_programs}")
    print(f"💾 Guardado en: {OUTPUT_FILE}")
    print("="*40)

if __name__ == "__main__":
    main()
