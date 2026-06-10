#!/usr/bin/env python3
"""
GOBO - GOB OSINT
Extracción de directorios públicos desde la Plataforma Nacional de Transparencia.
Base legal: LGTAIP Art. 70 | Fuente: plataformadetransparencia.org.mx (INAI)
"""

import json, time, csv, urllib.request, argparse, sys
from pathlib import Path

BASE_URL   = "https://backbuscadortematico.plataformadetransparencia.org.mx/api"
URL        = f"{BASE_URL}/tematico/buscador/consulta"
URL_OGS    = f"{BASE_URL}/federado/organosGarantes/listadoTotal"
URL_SUJETO = f"{BASE_URL}/federado/sujetosObligados/recuperaEntidad"
UA         = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"

# ── Poderes del Estado ──────────────────────────────────────────────────────
# ── Organismos autónomos ────────────────────────────────────────────────────
# ── Secretarías de Estado ───────────────────────────────────────────────────
# ── Empresas productivas del Estado ─────────────────────────────────────────
ENTIDADES = {
    # Poder Legislativo
    "diputados":     ("Fo1gQSyzrFDpZIEhyJkeOA==", "FED - Cámara de Diputados (CD)"),
    "senado":        ("lCZtP4661XVSq_4KGTzI5A==", "FED - Senado de la República"),
    "asf":           ("CVg5aJNiLtxaQvyz7He0dQ==", "FED - Auditoría Superior de la Federación (ASF)"),
    # Poder Ejecutivo - Presidencia
    "presidencia":   ("nFnQ9RL6sOrudbNHGdj8nQ==", "FED - Oficina de la Presidencia de la República"),
    # Poder Ejecutivo - Secretarías
    "segob":         ("XqRbfaJ-Cf7DUNqzgWioHQ==", "FED - Secretaría de Gobernación (SEGOB)"),
    "shcp":          ("MwVTl7OzE60PWAKyoUvKcg==", "FED - Secretaría de Hacienda y Crédito Público (SHCP)"),
    "sre":           ("LGEH45M5SwvnTKeRU2CG0A==", "FED - Secretaría de Relaciones Exteriores (SRE)"),
    "sedena":        ("Zqw3bL7QQQpNpDQWgGDGpg==", "FED - Secretaría de la Defensa Nacional (DEFENSA)"),
    "semar":         ("7h4CJo8_sm34rqVeHXeTwA==", "FED - Secretaría de Marina (SEMAR)"),
    "ssa":           ("0xgnnqeBMp5D1JP9N0_-vA==", "FED - Secretaría de Salud (SSA)"),
    "sep":           ("dp4zc_pCcluMiFE1MjA-5Q==", "FED - Secretaría de Educación Pública (SEP)"),
    "se":            ("7oiGqAWHxvHcohawU7191A==", "FED - Secretaría de Economía (SE)"),
    "agricultura":   ("388JRGsX2xOY_AToQP4Aag==", "FED - Secretaría de Agricultura y Desarrollo Rural"),
    "stps":          ("t_PRHqW_TJIYioWu60rR5w==", "FED - Secretaría del Trabajo y Previsión Social (STPS)"),
    "semarnat":      ("qbelgYLkoJQM6v0TFd-3Rw==", "FED - Secretaría de Medio Ambiente y Recursos Naturales (SEMARNAT)"),
    "sspc":          ("wlr2E133as1CrgyywBuchw==", "FED - Secretaría de Seguridad y Protección Ciudadana"),
    # Poder Judicial
    "scjn":          ("Bj1y47_Ran9GuOpcdw3bHA==", "FED - Suprema Corte de Justicia de la Nación (SCJN)"),
    "cjf":           ("upk0nhn-Vr37xM8cZSp-AQ==", "FED - Consejo de la Judicatura Federal (CJF)"),
    "tfja":          ("F1_E7HnKU4ZHn0D_oF0opg==", "FED - Tribunal Federal de Justicia Administrativa (TFJA)"),
    # Organismos constitucionales autónomos
    "ine":           ("Dqjo6Q8yBopEJUcQ1v1y0g==", "FED - Instituto Nacional Electoral (INE)"),
    "cndh":          ("cmIk-VmFziwA4N4RD5u04Q==", "FED - Comisión Nacional de los Derechos Humanos (CNDH)"),
    "inegi":         ("2tCn4X-o_gCBg7ZEXNNj7g==", "FED - Instituto Nacional de Estadística y Geografía (INEGI)"),
    "banxico":       ("W-_ABiGT6heW1mLXnIOUQQ==", "FED - Banco de México (BANXICO)"),
    "fgr":           ("wso_AjkSE2xAM7n-OpenVg==", "FED - Fiscalía General de la República"),
    # Seguridad Social
    "imss":          ("iCncpW99eqwYZSbgMtsugw==", "FED - Instituto Mexicano del Seguro Social (IMSS)"),
    "imss-bienestar":("MRs4uWr7SQOForRrufSosA==", "FED - Servicios de Salud IMSS-BIENESTAR"),
    "issste":        ("L6mZx6TXZqqt-GSxE_-g-A==", "FED - Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado (ISSSTE)"),
    # Recaudación
    "sat":           ("To-NkkjK_Ze5d2LcaZTj-w==", "FED - Servicio de Administración Tributaria (SAT)"),
    # Empresas productivas del Estado
    "pemex":         ("BovYZVC-uejkVJGYLVSlFw==", "FED - Petróleos Mexicanos (PEMEX)"),
    "cfe":           ("cdXPNFAfhSZncMqy3y4WFQ==", "FED - Comisión Federal de Electricidad (CFE)"),
    # Universidades e Investigación
    "unam":          ("GiY088NPemHmVPjBet-cBQ==", "FED - Universidad Nacional Autónoma de México (UNAM)"),
    "ipn":           ("xhoG7V6Gl-SzwubXxr20JA==", "FED - Instituto Politécnico Nacional (IPN)"),
    "uam":           ("3dFKfVZQmlt1gCw5NLTcIw==", "FED - Universidad Autónoma Metropolitana"),
    # Protección al consumidor / servicios
    "condusef":      ("wY2EqI2Zot9Bt9u1qq4xSg==", "FED - Comisión Nacional para la Protección y Defensa de los Usuarios de Servicios Financieros (CONDUSEF)"),
}


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_args():
    p = argparse.ArgumentParser(
        prog="gobo",
        description="GOBO – GOB OSINT: extrae directorios públicos de la Plataforma Nacional de Transparencia.",
        epilog="Ejemplos: python gobo.py --entidad diputados --domain diputados.gob.mx\n         python gobo.py --entidad imss --search 'director' --out ./resultados",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--entidad", metavar="ALIAS",
        help=f"Alias de entidad conocida (ver --list)"
    )
    group.add_argument(
        "--filter-id", metavar="BASE64",
        help="ID de filtro base64 para entidades no listadas (ver --discover)"
    )
    group.add_argument(
        "--list", action="store_true",
        help="Muestra las entidades precargadas y sus IDs"
    )
    group.add_argument(
        "--discover", metavar="TEXTO",
        help="Busca entidades por nombre en el catálogo de la PNT (descarga IDs en vivo)"
    )

    p.add_argument("--search",    default="", metavar="TEXTO",
                   help="Filtra registros por texto dentro de la institución (ej: 'director general'). Omitir = todos los registros.")
    p.add_argument("--domain",    metavar="DOMINIO",
                   help="Filtra correos por dominio (ej: diputados.gob.mx)")
    p.add_argument("--out",       default=".", metavar="DIR",
                   help="Directorio de salida (default: directorio actual)")

    p.add_argument("--delay",     type=float, default=0.4, metavar="SEG",
                   help="Segundos de espera entre páginas (default: 0.4)")
    p.add_argument("--no-csv",    action="store_true",
                   help="No genera el CSV completo, solo el TXT de correos")
    return p.parse_args()


def list_entities():
    cats = {}
    for alias, (fid, desc) in ENTIDADES.items():
        cat = _category(desc)
        cats.setdefault(cat, []).append((alias, fid, desc))
    for cat, items in cats.items():
        print(f"\n  {cat}")
        print("  " + "─" * 70)
        for alias, fid, desc in items:
            label = desc[len("FED - "):] if desc.startswith("FED - ") else desc
            print(f"    {alias:<20} {label}")
    print(f"\n  Total: {len(ENTIDADES)} entidades precargadas")
    print("  Usa --discover TEXTO para buscar más entidades en el catálogo completo.\n")
    sys.exit(0)


def _category(desc):
    d = desc.lower()
    if any(x in d for x in ["diputados", "senado", "auditoría superior"]): return "Poder Legislativo"
    if any(x in d for x in ["presidencia", "gobernación", "hacienda", "relaciones exteriores",
                             "defensa", "marina", "salud", "educación pública", "economía",
                             "agricultura", "trabajo", "medio ambiente", "seguridad y protección"]): return "Poder Ejecutivo – Secretarías"
    if any(x in d for x in ["suprema corte", "judicatura", "tribunal federal"]): return "Poder Judicial"
    if any(x in d for x in ["electoral", "derechos humanos", "estadística", "banco de méxico",
                             "fiscalía"]): return "Organismos Autónomos"
    if any(x in d for x in ["imss", "issste", "bienestar"]): return "Seguridad Social"
    if any(x in d for x in ["petróleos", "electricidad"]): return "Empresas del Estado"
    if any(x in d for x in ["universidad", "politécnico", "autónoma metropolitana"]): return "Universidades"
    return "Otros"


def discover_entities(query):
    """Descarga el catálogo de la PNT y busca entidades que coincidan con el texto."""
    HEADERS_JSON = {
        "Content-Type": "application/json",
        "User-Agent": UA,
        "Origin":  "https://tematicos.plataformadetransparencia.org.mx",
        "Referer": "https://tematicos.plataformadetransparencia.org.mx/",
    }
    HEADERS_TEXT = {**HEADERS_JSON, "Content-Type": "text/plain"}

    print(f"[*] Descargando catálogo de organismos garantes...")
    req = urllib.request.Request(URL_OGS, data=b"{}", headers=HEADERS_JSON)
    with urllib.request.urlopen(req, timeout=30) as r:
        ogs = json.load(r)
    print(f"[*] {len(ogs)} organismos garantes — buscando '{query}'...")

    found = {}
    q = query.lower()
    for og in ogs:
        try:
            req = urllib.request.Request(URL_SUJETO, data=og["id"].encode(), headers=HEADERS_TEXT)
            with urllib.request.urlopen(req, timeout=30) as r:
                sujetos = json.load(r)
            if isinstance(sujetos, list):
                for s in sujetos:
                    if q in s["nombre"].lower():
                        found[s["id"]] = s["nombre"]
            time.sleep(0.15)
        except Exception:
            pass

    if not found:
        print(f"[!] No se encontraron entidades que contengan '{query}'.")
        sys.exit(1)

    print(f"\n[+] Resultados ({len(found)}):\n")
    print(f"  {'Filter ID':<32}  Nombre")
    print("  " + "─" * 70)
    for fid, nombre in sorted(found.items(), key=lambda x: x[1]):
        print(f"  {fid:<32}  {nombre}")
    print(f"\nUsa el Filter ID con: python gobo.py --filter-id \"ID_AQUI\"\n")
    sys.exit(0)


# ── HTTP ──────────────────────────────────────────────────────────────────────

PAGE_SIZE = 200

def build_body(query, filter_id, page):
    return {
        "contenido": query,
        "cantidad": PAGE_SIZE,
        "numeroPagina": page,
        "coleccion": "DIRECTORIO",
        "dePaginador": True,
        "idCompartido": "",
        "filtroSeleccionado": "",
        "tipoOrdenamiento": "COINCIDENCIA",
        "sujetosObligados": {"seleccion": [filter_id], "descartado": []},
        "organosGarantes":  {"seleccion": [], "descartado": []},
        "anioFechaInicio":  {"seleccion": [], "descartado": []},
    }


def fetch(body_dict, retries=4, timeout=60):
    data = json.dumps(body_dict).encode()
    req  = urllib.request.Request(URL, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "User-Agent":   UA,
        "Origin":  "https://tematicos.plataformadetransparencia.org.mx",
        "Referer": "https://tematicos.plataformadetransparencia.org.mx/",
    })
    page = body_dict["numeroPagina"]
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)["paylod"]
        except Exception as e:
            wait = 3 * (attempt + 1)
            print(f"  [!] Página {page} — intento {attempt+1}/{retries}: {e} (reintento en {wait}s)")
            time.sleep(wait)
    raise RuntimeError(f"No se pudo obtener la página {page} tras {retries} intentos.")


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_record(r):
    ip = r.get("informacionPrincipal", {})
    return {
        "nombre":      ip.get("nombre")      or r.get("nombre", ""),
        "cargo":       ip.get("cargo")       or r.get("denominacion", ""),
        "area":        ip.get("area")        or r.get("areaadscripcion", ""),
        "correo":      (ip.get("correo")     or "").strip().lower(),
        "telefono":    ip.get("telefono", ""),
        "institucion": ip.get("institucion") or r.get("sujetoobligado", ""),
        "direccion":   ip.get("direccion", ""),
        "periodo":     ip.get("periodoinforma") or r.get("periodoreporta", ""),
    }


def absorb(payload, records):
    for r in payload["datosSolr"]:
        records[r["id"]] = parse_record(r)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = build_args()

    if args.list:
        list_entities()

    if args.discover:
        discover_entities(args.discover)

    if args.entidad:
        if args.entidad not in ENTIDADES:
            print(f"[!] Entidad '{args.entidad}' desconocida. Usa --list para ver opciones o --filter-id para un ID directo.")
            sys.exit(1)
        filter_id, desc = ENTIDADES[args.entidad]
        label = args.entidad
    else:
        filter_id = args.filter_id
        desc  = f"custom ({filter_id})"
        label = "custom"

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  ██████╗  ██████╗ ██████╗  ██████╗")
    print(f"  ██╔════╝ ██╔═══██╗██╔══██╗██╔═══██╗")
    print(f"  ██║  ███╗██║   ██║██████╔╝██║   ██║")
    print(f"  ██║   ██║██║   ██║██╔══██╗██║   ██║")
    print(f"  ╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝")
    print(f"   ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝")
    print(f"   GOB OSINT — Plataforma Nacional de Transparencia - Xanny A\n")

    print(f"[*] Entidad   : {desc}")
    if args.search:
        print(f"[*] Filtro texto: '{args.search}'")
    print(f"[*] Filter ID : {filter_id}")
    if args.domain:
        print(f"[*] Dominio   : @{args.domain.lstrip('@').lower()}")
    print(f"[*] Salida    : {out_dir.resolve()}\n")

    records = {}
    first   = fetch(build_body(args.search, filter_id, 0))
    total   = first["paginador"]["total"]
    npages  = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"[*] Registros en plataforma : {total}  |  Páginas : {npages}")

    absorb(first, records)

    for pg in range(1, npages):
        absorb(fetch(build_body(args.search, filter_id, pg)), records)
        if pg % 10 == 0 or pg == npages - 1:
            print(f"  -> Página {pg+1}/{npages}  |  únicos acumulados: {len(records)}")
        time.sleep(args.delay)

    rows = list(records.values())

    # Filtro opcional por dominio de correo
    if args.domain:
        dom  = args.domain.lstrip("@").lower()
        rows = [r for r in rows if r["correo"].endswith(f"@{dom}")]
        print(f"\n[*] Registros tras filtro @{dom} : {len(rows)}")

    emails      = [r["correo"] for r in rows if r["correo"]]
    uniq_emails = sorted(set(emails))

    # CSV completo
    if not args.no_csv:
        csv_path = out_dir / f"{label}_directorio.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=[
                "nombre", "cargo", "area", "correo",
                "telefono", "institucion", "direccion", "periodo"
            ])
            w.writeheader()
            w.writerows(rows)
        print(f"[+] CSV        -> {csv_path}")

    # TXT de correos únicos
    txt_path = out_dir / f"{label}_correos.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(uniq_emails))

    print(f"\n[+] Registros únicos  : {len(rows)}")
    print(f"[+] Con correo        : {len(emails)}")
    print(f"[+] Correos únicos    : {len(uniq_emails)}")
    print(f"[+] TXT correos    -> {txt_path}\n")


if __name__ == "__main__":
    main()
