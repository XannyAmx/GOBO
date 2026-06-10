# GOBO — GOB OSINT

> Herramienta de OSINT para extracción automatizada de directorios públicos desde la **Plataforma Nacional de Transparencia** del gobierno mexicano (INAI).

```
  ██████╗  ██████╗ ██████╗  ██████╗
  ██╔════╝ ██╔═══██╗██╔══██╗██╔═══██╗
  ██║  ███╗██║   ██║██████╔╝██║   ██║
  ██║   ██║██║   ██║██╔══██╗██║   ██║
  ╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝
   ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝
```

---

## ¿Qué hace?

GOBO consulta el endpoint JSON público que utiliza el portal [tematicos.plataformadetransparencia.org.mx](https://tematicos.plataformadetransparencia.org.mx/) y extrae los directorios de servidores públicos que cada sujeto obligado publica por mandato legal. Genera:

- **CSV** con nombre, cargo, área, correo, teléfono, institución, dirección y periodo.
- **TXT** con la lista de correos únicos (útil para campañas de investigación o validación).

---

## Requisitos

- Python 3.8+
- Sin dependencias externas (usa únicamente la librería estándar)

---

## Uso

```bash
# Ver entidades precargadas (34 instituciones federales)
python gobo.py --list

# Buscar entidades en el catálogo completo de la PNT (~9,600 instituciones)
python gobo.py --discover "comunicaciones"
python gobo.py --discover "poder judicial jalisco"

# Extraer directorio completo de una institución
python gobo.py --entidad diputados
python gobo.py --entidad imss

# Filtrar solo correos de un dominio específico
python gobo.py --entidad diputados --domain diputados.gob.mx

# Buscar solo ciertos cargos dentro de la institución
python gobo.py --entidad sep --search "director general"

# Usar un filter-id obtenido con --discover
python gobo.py --filter-id "BASE64_ID_AQUI"

# Guardar resultados en carpeta específica
python gobo.py --entidad senado --out ./resultados

# Solo generar TXT de correos (sin CSV)
python gobo.py --entidad imss --no-csv
```

### Opciones

| Argumento | Default | Descripción |
|---|---|---|
| `--entidad ALIAS` | — | Alias de entidad precargada (ver `--list`) |
| `--filter-id BASE64` | — | Filter ID directo obtenido con `--discover` |
| `--list` | — | Lista las 34 entidades precargadas por categoría |
| `--discover TEXTO` | — | Busca entidades en el catálogo completo de la PNT |
| `--search TEXTO` | *(vacío)* | Filtra por texto dentro de los registros (ej: `"director general"`). Sin este argumento trae **todos** los registros. |
| `--domain DOMINIO` | — | Filtra resultados por dominio de correo |
| `--out DIR` | `.` | Directorio de salida |
| `--delay SEG` | `0.4` | Segundos de espera entre peticiones |
| `--no-csv` | — | Omite el CSV, solo genera el TXT de correos |

---

## Entidades precargadas

| Categoría | Alias |
|---|---|
| Poder Legislativo | `diputados`, `senado`, `asf` |
| Poder Ejecutivo | `presidencia`, `segob`, `shcp`, `sre`, `sedena`, `semar`, `ssa`, `sep`, `se`, `agricultura`, `stps`, `semarnat`, `sspc` |
| Poder Judicial | `scjn`, `cjf`, `tfja` |
| Organismos Autónomos | `ine`, `cndh`, `inegi`, `banxico`, `fgr` |
| Seguridad Social | `imss`, `imss-bienestar`, `issste` |
| Recaudación | `sat` |
| Empresas del Estado | `pemex`, `cfe` |
| Universidades | `unam`, `ipn`, `uam` |
| Financiero | `condusef` |

Para entidades estatales o no precargadas, usa `--discover`.

---

## Agregar entidades permanentemente

Edita el diccionario `ENTIDADES` en `gobo.py`:

```python
ENTIDADES = {
    ...
    "jalisco":  ("ID_OBTENIDO_CON_DISCOVER==", "JAL - Gobierno del Estado de Jalisco"),
}
```

---

## Base legal

La información extraída por GOBO es **pública por mandato legal**. Su publicación está ordenada por las siguientes disposiciones:

| Instrumento legal | Artículo relevante | Contenido |
|---|---|---|
| **Ley General de Transparencia y Acceso a la Información Pública (LGTAIP)** | Art. 70, fracc. I | Obliga a todo sujeto obligado a publicar su directorio de servidores públicos (nombre, cargo, correo institucional, teléfono). |
| **Ley Federal de Transparencia y Acceso a la Información Pública (LFTAIP)** | Art. 71 | Reitera la obligación de publicación en el ámbito federal. |
| **Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados (LGPDPPSO)** | Art. 6 | Los datos publicados por obligación de transparencia no se consideran datos personales protegidos en ese contexto. |

El acceso a la API pública no requiere autenticación y no vulnera ningún control de seguridad; por lo tanto, no encuadra en el delito de acceso ilícito previsto en el **Código Penal Federal, Art. 211bis**.

---

## Disclaimer legal

> **GOBO es una herramienta de investigación para fuentes abiertas (OSINT).**
>
> - El uso de esta herramienta debe limitarse a **fines legítimos**: investigación periodística, académica, auditoría ciudadana o análisis de transparencia.
> - **Queda prohibido** el uso de los datos obtenidos para spam, phishing, acoso, o cualquier actividad ilícita conforme a la legislación mexicana y aplicable.
> - El autor no se responsabiliza del uso indebido que terceros hagan de esta herramienta.
> - El usuario es el único responsable de cumplir con las leyes aplicables en su jurisdicción.

---

## Fuente de datos

- **Portal**: [Plataforma Nacional de Transparencia — Buscador Temático](https://tematicos.plataformadetransparencia.org.mx/)
- **Operador**: Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (**INAI**)
- **Endpoint público**: `backbuscadortematico.plataformadetransparencia.org.mx`

---

## Licencia

MIT — libre uso, modificación y distribución con atribución al autor original.
