"""
MARCO 32 — Monitoreo de nivel · Estación 32 (CORNARE)
Nicolás Cataño Durango

    pip install "streamlit>=1.31" pandas numpy requests plotly
    streamlit run app_estacion_32.py
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import requests
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import plotly.graph_objects as go

    PLOTLY = True
except ImportError:
    PLOTLY = False


ESTUDIANTE = "Nicolás Cataño Durango"
CODIGO_ESTACION = "32"
CALIDAD = 1
UNIDAD = "m"
VENTANAS = (7, 30, 365)

API = "https://marco.cornare.gov.co/api/v1/estaciones"
LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"
LAT_DEFECTO = 6.2766
LON_DEFECTO = -75.5901

LLAVES_LAT = ["lat", "latitude", "latitud", "y"]
LLAVES_LON = ["lng", "lon", "long", "longitude", "longitud", "x"]
LLAVES_COD = ["code", "codigo", "id", "station_code", "pk"]
LLAVES_NOM = ["name", "nombre", "descripcion", "description", "label"]
LLAVES_MUN = ["municipio", "municipality", "town", "city", "localidad"]
LLAVES_FUENTE = ["fuente", "corriente", "rio", "river", "stream", "cuerpo_agua", "source"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

VERDE = "#2F7D5C"
VERDE_CLARO = "#7FBF9A"
AZUL = "#1B7FA8"
AZUL_CLARO = "#8FCDE2"
TIERRA = "#5A6B5F"
CREMA = "#F4F8F4"

ESTADOS = [
    ("Normal", "#3E9C6B"),
    ("Atención", "#E4A11B"),
    ("Alerta", "#D9773D"),
    ("Crítico", "#B3352C"),
]

FRANJAS = [
    ("Madrugada", range(0, 6), "#12608A"),
    ("Mañana", range(6, 12), "#4FA9C9"),
    ("Tarde", range(12, 18), "#7FBF9A"),
    ("Noche", range(18, 24), "#2F7D5C"),
]

st.set_page_config(page_title="Estación 32 — MARCO CORNARE", page_icon="💧", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Karla:wght@400;500;600&display=swap');

.stApp { background: #F4F8F4; color: #17251F; font-family: 'Karla', system-ui, sans-serif; }
h1, h2, h3 { font-family: 'Sora', sans-serif; color: #17251F; letter-spacing: -.02em; }
h2 { font-size: 1.35rem; margin: 2.4rem 0 .6rem 0; }
h2:before { content: ''; display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            background: #2F7D5C; margin-right: .6rem; vertical-align: middle; }
p, li, label { color: #17251F; }

.portada { position: relative; border-radius: 18px; overflow: hidden; box-shadow: 0 10px 30px rgba(23,37,31,.10); }
.portada svg { display: block; width: 100%; }
.portada-texto { position: absolute; inset: 0; display: flex; flex-direction: column;
                 justify-content: center; padding: 0 clamp(1.4rem, 4vw, 3.4rem); }
.eyebrow { font-family: 'Karla', sans-serif; font-size: .7rem; font-weight: 600; letter-spacing: .22em;
           color: #2F7D5C; margin-bottom: .5rem; }
.portada h1 { font-size: clamp(2rem, 4.6vw, 3.4rem); font-weight: 700; line-height: 1; margin: 0 0 .5rem 0; }
.portada .lema { font-size: clamp(.9rem, 1.5vw, 1.05rem); color: #33473D; max-width: 30ch; margin: 0 0 1.1rem 0; }
.firma { display: inline-flex; align-items: center; gap: .55rem; background: rgba(255,255,255,.78);
         border: 1px solid rgba(47,125,92,.25); border-radius: 999px; padding: .4rem 1rem;
         font-weight: 600; font-size: .88rem; width: fit-content; backdrop-filter: blur(4px); }
.firma span.punto { width: 8px; height: 8px; border-radius: 50%; background: #2F7D5C; }

.tarjetas { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: .9rem; margin-top: 1.4rem; }
.tarjeta { background: #FFFFFF; border: 1px solid #E1EBE4; border-radius: 14px; padding: 1rem 1.1rem;
           box-shadow: 0 2px 10px rgba(23,37,31,.04); }
.tarjeta .et { font-size: .72rem; letter-spacing: .08em; color: #5A6B5F; margin-bottom: .4rem; }
.tarjeta .va { font-family: 'Sora', sans-serif; font-size: 1.6rem; font-weight: 600; line-height: 1; }
.tarjeta .pi { font-size: .78rem; color: #5A6B5F; margin-top: .35rem; }

.insight { background: #FFFFFF; border: 1px solid #E1EBE4; border-left: 4px solid #1B7FA8;
           border-radius: 12px; padding: .9rem 1.1rem; height: 100%; }
.insight .ti { font-family: 'Sora', sans-serif; font-weight: 600; font-size: .95rem; margin-bottom: .3rem; }
.insight .tx { font-size: .88rem; color: #33473D; line-height: 1.45; }

.nota { color: #5A6B5F; font-size: .86rem; border-left: 3px solid #7FBF9A; padding-left: .8rem; }
div[data-testid="stMetricValue"] { font-family: 'Sora', sans-serif; }
footer, #MainMenu { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


# --- API -----------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def pedir(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=30, verify=False)
    except requests.exceptions.RequestException:
        return None, "No hubo respuesta de la API de MARCO."
    if r.status_code != 200:
        return None, f"La API respondió HTTP {r.status_code}."
    try:
        return r.json(), None
    except ValueError:
        return None, "La respuesta de la API no es JSON."


def valor(d, llaves):
    for k in llaves:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None


def coords(obj, nivel=0):
    if nivel > 4 or not isinstance(obj, dict):
        return None, None
    la, lo = valor(obj, LLAVES_LAT), valor(obj, LLAVES_LON)
    if la is not None and lo is not None:
        try:
            return float(la), float(lo)
        except (TypeError, ValueError):
            pass
    for v in obj.values():
        if isinstance(v, dict):
            a, b = coords(v, nivel + 1)
            if a is not None:
                return a, b
    return None, None


@st.cache_data(ttl=1800, show_spinner=False)
def ficha_estacion(codigo):
    datos, err = pedir(API)
    if err:
        return {}
    bruto = datos
    if isinstance(datos, dict):
        for k in ("values", "data", "results", "estaciones", "items"):
            if isinstance(datos.get(k), list):
                bruto = datos[k]
                break
    if not isinstance(bruto, list):
        return {}
    for it in bruto:
        if isinstance(it, dict) and str(valor(it, LLAVES_COD)) == str(codigo):
            la, lo = coords(it)
            return {
                "nombre": str(valor(it, LLAVES_NOM) or ""),
                "municipio": str(valor(it, LLAVES_MUN) or ""),
                "fuente": str(valor(it, LLAVES_FUENTE) or ""),
                "lat": la,
                "lon": lo,
            }
    return {}


def paginar(datos):
    registros = list(datos.get("values", []) if isinstance(datos, dict) else [])
    siguiente = datos.get("next") if isinstance(datos, dict) else None
    vueltas = 0
    while siguiente and vueltas < 300 and len(registros) < 80000:
        pagina, err = pedir(siguiente)
        if err or not isinstance(pagina, dict):
            break
        registros.extend(pagina.get("values", []))
        siguiente = pagina.get("next")
        vueltas += 1
    return registros


@st.cache_data(ttl=300, show_spinner=False)
def leer_nivel(codigo, desde, hasta, calidad):
    datos, err = pedir(f"{API}/{codigo}/nivel", {"desde": desde, "hasta": hasta, "calidad": calidad})
    if err:
        return pd.DataFrame(), {}, err
    registros = paginar(datos)
    if not registros:
        return pd.DataFrame(), {}, "sin registros"
    df = pd.DataFrame(registros).rename(columns={LLAVE_FECHA: "fecha", LLAVE_VALOR: "nivel"})
    if "fecha" not in df or "nivel" not in df:
        return pd.DataFrame(), {}, "la respuesta no trae fecha y nivel"
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    df = df.dropna(subset=["fecha", "nivel"]).sort_values("fecha").reset_index(drop=True)
    la, lo = coords(datos if isinstance(datos, dict) else {})
    return df, {"lat": la, "lon": lo, "nombre": str(valor(datos, LLAVES_NOM) or "")}, None


@st.cache_data(ttl=300, show_spinner=False)
def cargar(codigo, calidad):
    hoy = date.today()
    for dias in VENTANAS:
        desde = hoy - timedelta(days=dias)
        df, meta, err = leer_nivel(codigo, desde.strftime("%Y-%m-%d"), hoy.strftime("%Y-%m-%d"), calidad)
        if not df.empty:
            return df, meta, desde, hoy, dias, None
    df, meta, err = leer_nivel(codigo, (hoy - timedelta(days=365)).strftime("%Y-%m-%d"),
                               hoy.strftime("%Y-%m-%d"), 0)
    if not df.empty:
        return df, meta, hoy - timedelta(days=365), hoy, 365, None
    return pd.DataFrame(), {}, None, None, None, err or "sin datos"


# --- cálculos ------------------------------------------------------

def paso_tipico(df):
    d = df["fecha"].diff().dropna()
    if d.empty:
        return pd.Timedelta(minutes=10)
    m = d.mode()
    return m.iloc[0] if len(m) else d.median()


def percentiles(df):
    n = df["nivel"]
    return {"min": float(n.min()), "p25": float(n.quantile(.25)), "p50": float(n.quantile(.50)),
            "p75": float(n.quantile(.75)), "p90": float(n.quantile(.90)), "p97": float(n.quantile(.97)),
            "max": float(n.max())}


def estado_de(nivel, q):
    if nivel >= q["p97"]:
        return 3
    if nivel >= q["p90"]:
        return 2
    if nivel >= q["p75"]:
        return 1
    return 0


def tasa(df, minutos=30):
    if len(df) < 2:
        return pd.Series(0.0, index=df.index)
    pasos = max(1, int(round(pd.Timedelta(minutes=minutos) / paso_tipico(df))))
    pasos = min(pasos, max(1, len(df) // 3))
    suave = df["nivel"].rolling(pasos, min_periods=1).median()
    horas = (df["fecha"] - df["fecha"].shift(pasos)).dt.total_seconds() / 3600
    return ((suave - suave.shift(pasos)) / horas.replace(0, np.nan)).fillna(0)


def pendiente(df, horas=6):
    sub = df[df["fecha"] >= df["fecha"].max() - pd.Timedelta(hours=horas)]
    if len(sub) < 3:
        return 0.0
    x = (sub["fecha"] - sub["fecha"].min()).dt.total_seconds().to_numpy() / 3600
    return 0.0 if np.ptp(x) == 0 else float(np.polyfit(x, sub["nivel"].to_numpy(), 1)[0])


def atipicos(df):
    q1, q3 = df["nivel"].quantile(.25), df["nivel"].quantile(.75)
    iqr = q3 - q1
    return (df["nivel"] < q1 - 1.5 * iqr) | (df["nivel"] > q3 + 1.5 * iqr) | (df["nivel"] < 0)


def calidad_serie(df):
    if len(df) < 2:
        return 0.0, 0, 0
    paso = paso_tipico(df)
    esperados = max(1, int((df["fecha"].max() - df["fecha"].min()) / paso) + 1)
    huecos = max(0, esperados - len(df))
    completitud = max(0.0, 1 - huecos / esperados)
    fuera = atipicos(df)
    return round((completitud * .7 + (1 - fuera.mean()) * .3) * 100, 1), huecos, int(fuera.sum())


def horas_por_estado(df, q):
    paso_h = paso_tipico(df).total_seconds() / 3600
    cat = df["nivel"].apply(lambda v: estado_de(v, q))
    return [round(float((cat == i).sum() * paso_h), 1) for i in range(4)]


def franja_de(hora):
    for i, (_, rango, _) in enumerate(FRANJAS):
        if hora in rango:
            return i
    return 0


def altas_por_franja(df, q):
    altas = df[df["nivel"] >= q["p75"]].copy()
    if altas.empty:
        return [0, 0, 0, 0]
    idx = altas["fecha"].dt.hour.apply(franja_de)
    return [int((idx == i).sum()) for i in range(4)]


def resumen_diario(df):
    d = df.set_index("fecha")["nivel"].resample("1D").agg(["min", "mean", "max"]).dropna()
    d["amplitud"] = d["max"] - d["min"]
    return d.reset_index()


def perfil_horario(df):
    d = df.copy()
    d["hora"] = d["fecha"].dt.hour
    return d.groupby("hora")["nivel"].mean().reindex(range(24))


def curva_duracion(df, maximo=2000):
    orden = np.sort(df["nivel"].to_numpy())[::-1]
    excedencia = np.arange(1, len(orden) + 1) / len(orden) * 100
    if len(orden) > maximo:
        paso = int(np.ceil(len(orden) / maximo))
        orden, excedencia = orden[::paso], excedencia[::paso]
    return pd.DataFrame({"excedencia": excedencia, "nivel": orden})


def compactar(df, maximo=3000):
    if len(df) <= maximo:
        return df
    factor = int(np.ceil(len(df) / maximo))
    regla = paso_tipico(df) * factor
    return df.set_index("fecha")["nivel"].resample(regla).mean().dropna().reset_index()


def generar_insights(df, q, diario, perfil, horas_estado, indice, huecos):
    total = sum(horas_estado) or 1
    pico = df.loc[df["nivel"].idxmax()]
    hora_alta = int(perfil.idxmax()) if perfil.notna().any() else 0
    dia_movido = diario.loc[diario["amplitud"].idxmax()]
    subidas = tasa(df)
    ideas = []
    ideas.append({
        "titulo": "Pico del periodo",
        "texto": f"El nivel más alto fue {pico['nivel']:.2f} {UNIDAD} el "
                 f"{pico['fecha']:%d/%m/%Y a las %H:%M}, un {(pico['nivel'] / q['p50'] - 1) * 100:.0f} % "
                 f"por encima de la mediana del periodo.",
    })
    ideas.append({
        "titulo": "Cauce tranquilo la mayor parte del tiempo",
        "texto": f"El {horas_estado[0] / total * 100:.0f} % de las horas el nivel estuvo en estado normal y "
                 f"{horas_estado[3]:.0f} h alcanzaron condición crítica, sobre el percentil 97.",
    })
    ideas.append({
        "titulo": "La hora en que más crece",
        "texto": f"El promedio más alto del día se da hacia las {hora_alta:02d}:00 h, y el ascenso más rápido "
                 f"registrado fue de {subidas.max():.2f} {UNIDAD}/h.",
    })
    ideas.append({
        "titulo": "Día más movido",
        "texto": f"El {dia_movido['fecha']:%d/%m/%Y} el río osciló {dia_movido['amplitud']:.2f} {UNIDAD} "
                 f"entre su mínimo y su máximo, la mayor amplitud del periodo.",
    })
    ideas.append({
        "titulo": "Confianza de los datos",
        "texto": f"La serie llega a {indice:.0f} sobre 100 en el índice de calidad, con {huecos} huecos de "
                 f"reporte y una frecuencia típica de {paso_tipico(df)}.",
    })
    return ideas


# --- portada -------------------------------------------------------

def portada_svg():
    return """
<svg viewBox="0 0 1200 340" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" aria-hidden="true">
  <defs>
    <linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E7F3EC"/><stop offset="100%" stop-color="#CFE7DE"/>
    </linearGradient>
    <linearGradient id="rio" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8FCDE2"/><stop offset="100%" stop-color="#1B7FA8"/>
    </linearGradient>
    <linearGradient id="velo" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#F4F8F4" stop-opacity=".96"/>
      <stop offset="58%" stop-color="#F4F8F4" stop-opacity=".55"/>
      <stop offset="100%" stop-color="#F4F8F4" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect width="1200" height="340" fill="url(#cielo)"/>
  <circle cx="1010" cy="82" r="46" fill="#F3EAC8" opacity=".85"/>
  <ellipse cx="880" cy="118" rx="150" ry="14" fill="#FFFFFF" opacity=".5"/>
  <ellipse cx="1060" cy="146" rx="120" ry="11" fill="#FFFFFF" opacity=".42"/>

  <path d="M0 186 L120 142 L232 178 L348 120 L472 172 L604 128 L724 176 L852 132 L982 172 L1102 146 L1200 182 L1200 340 L0 340 Z"
        fill="#A8CBBB"/>
  <path d="M0 224 L152 182 L286 218 L424 166 L566 212 L706 176 L846 218 L1002 182 L1124 218 L1200 198 L1200 340 L0 340 Z"
        fill="#7FB59B"/>
  <path d="M0 262 L182 226 L334 260 L502 216 L682 258 L864 222 L1032 258 L1200 236 L1200 340 L0 340 Z"
        fill="#4E8F72"/>

  <path d="M596 232 C572 268 528 296 472 340 L742 340 C700 292 646 262 626 232 Z" fill="url(#rio)" opacity=".92"/>
  <path d="M612 244 C598 276 566 300 534 340 L586 340 C600 300 616 274 622 246 Z" fill="#CDEAF4" opacity=".55">
    <animate attributeName="opacity" values=".25;.6;.25" dur="5s" repeatCount="indefinite"/>
  </path>

  <path d="M0 300 C210 286 320 316 520 322 C764 328 906 302 1200 314 L1200 340 L0 340 Z" fill="#2F6B52"/>
  <rect width="1200" height="340" fill="url(#velo)"/>
</svg>
"""


def tarjeta(etiqueta, valor_txt, pie=""):
    return (f'<div class="tarjeta"><div class="et">{etiqueta}</div>'
            f'<div class="va">{valor_txt}</div><div class="pi">{pie}</div></div>')


# --- carga ---------------------------------------------------------

ficha = ficha_estacion(CODIGO_ESTACION)
with st.spinner("Consultando la red MARCO…"):
    df, meta, desde, hasta, dias, error = cargar(CODIGO_ESTACION, CALIDAD)

nombre = ficha.get("nombre") or (meta.get("nombre") if meta else "") or "Estación 32"
municipio = ficha.get("municipio") or ""
fuente = ficha.get("fuente") or ""
lat = ficha.get("lat") or (meta.get("lat") if meta else None)
lon = ficha.get("lon") or (meta.get("lon") if meta else None)
sitio = " · ".join([x for x in (fuente, municipio) if x]) or "Oriente antioqueño"

st.markdown(
    f"""
<div class="portada">
  {portada_svg()}
  <div class="portada-texto">
    <div class="eyebrow">SISTEMA DE MONITOREO AMBIENTAL REGIONAL · CORNARE</div>
    <h1>{nombre}</h1>
    <p class="lema">Nivel de ríos y quebradas en tiempo real · Estación {CODIGO_ESTACION} · {sitio}</p>
    <div class="firma"><span class="punto"></span>{ESTUDIANTE}</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        f"<h2>Sin lecturas disponibles</h2><p class='nota'>La estación {CODIGO_ESTACION} no devolvió datos "
        f"en el último año ({error}). La red MARCO reporta minuto a minuto, así que suele tratarse de una "
        "interrupción momentánea del servicio.</p>",
        unsafe_allow_html=True,
    )
    st.stop()


# --- métricas ------------------------------------------------------

q = percentiles(df)
actual = float(df["nivel"].iloc[-1])
previo = float(df["nivel"].iloc[-2]) if len(df) > 1 else actual
idx_estado = estado_de(actual, q)
nombre_estado, color_estado = ESTADOS[idx_estado]
tend = pendiente(df, 6)
tasas = tasa(df)
indice, huecos, n_atipicos = calidad_serie(df)
horas_estado = horas_por_estado(df, q)
diario = resumen_diario(df)
perfil = perfil_horario(df)
percentil_actual = float((df["nivel"] <= actual).mean() * 100)
flecha = "↑" if tend > 0.001 else ("↓" if tend < -0.001 else "→")

st.markdown(
    '<div class="tarjetas">'
    + tarjeta("NIVEL ACTUAL", f"{actual:.2f} <span style='font-size:.9rem;color:#5A6B5F'>{UNIDAD}</span>",
              f"{actual - previo:+.3f} frente a la lectura previa")
    + tarjeta("ESTADO DEL CAUCE", f"<span style='color:{color_estado}'>{nombre_estado}</span>",
              f"supera al {percentil_actual:.0f} % del periodo")
    + tarjeta("TENDENCIA 6 H", f"{flecha} {abs(tend):.3f}", f"{UNIDAD} por hora")
    + tarjeta("PROMEDIO", f"{df['nivel'].mean():.2f}", f"mediana {q['p50']:.2f} {UNIDAD}")
    + tarjeta("MÁXIMO / MÍNIMO", f"{q['max']:.2f} / {q['min']:.2f}", f"amplitud {q['max'] - q['min']:.2f} {UNIDAD}")
    + tarjeta("LECTURAS", f"{len(df):,}".replace(",", "."), f"últimos {dias} días · calidad {indice:.0f}/100")
    + "</div>",
    unsafe_allow_html=True,
)


# --- insights ------------------------------------------------------

st.markdown("## Lo que dicen los datos")
ideas = generar_insights(df, q, diario, perfil, horas_estado, indice, huecos)
fila1 = st.columns(3)
for col, idea in zip(fila1, ideas[:3]):
    col.markdown(f"<div class='insight'><div class='ti'>{idea['titulo']}</div>"
                 f"<div class='tx'>{idea['texto']}</div></div>", unsafe_allow_html=True)
fila2 = st.columns(2)
for col, idea in zip(fila2, ideas[3:]):
    col.markdown(f"<div class='insight'><div class='ti'>{idea['titulo']}</div>"
                 f"<div class='tx'>{idea['texto']}</div></div>", unsafe_allow_html=True)


# --- gráficos ------------------------------------------------------

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#17251F", family="Karla"),
              margin=dict(l=10, r=10, t=40, b=10),
              hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E1EBE4"))


def formatear(fig):
    fig.update_xaxes(gridcolor="#E1EBE4", linecolor="#E1EBE4", zerolinecolor="#E1EBE4")
    fig.update_yaxes(gridcolor="#E1EBE4", linecolor="#E1EBE4", zerolinecolor="#E1EBE4")
    fig.update_layout(**LAYOUT)
    return fig


st.markdown("## Serie del nivel")
if not PLOTLY:
    st.line_chart(compactar(df).set_index("fecha")["nivel"])
else:
    grafico = compactar(df)
    ventana = max(3, len(grafico) // 40)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grafico["fecha"], y=grafico["nivel"], name="Nivel", mode="lines",
                             line=dict(color=AZUL, width=1.6), fill="tozeroy",
                             fillcolor="rgba(27,127,168,.12)",
                             hovertemplate="%{x|%d/%m %H:%M}<br>%{y:.3f} " + UNIDAD + "<extra></extra>"))
    fig.add_trace(go.Scatter(x=grafico["fecha"], y=grafico["nivel"].rolling(ventana, center=True, min_periods=1).mean(),
                             name="Media móvil", mode="lines", line=dict(color=VERDE, width=1.6, dash="dot")))
    for clave, color, etq in (("p75", ESTADOS[1][1], "P75"), ("p90", ESTADOS[2][1], "P90"),
                              ("p97", ESTADOS[3][1], "P97")):
        fig.add_hline(y=q[clave], line=dict(color=color, width=1, dash="dash"),
                      annotation_text=etq, annotation_position="top left",
                      annotation_font=dict(color=color, size=10))
    fig.update_layout(height=400, hovermode="x unified", legend=dict(orientation="h", y=1.14, x=0))
    fig.update_yaxes(title=f"Nivel ({UNIDAD})")
    st.plotly_chart(formatear(fig), use_container_width=True)

izq, der = st.columns(2)

with izq:
    st.markdown("## Tiempo en cada estado")
    if PLOTLY:
        ft = go.Figure(go.Pie(labels=[e[0] for e in ESTADOS], values=horas_estado,
                              marker=dict(colors=[e[1] for e in ESTADOS], line=dict(color="#FFFFFF", width=2)),
                              hole=.45, sort=False, textinfo="label+percent",
                              hovertemplate="%{label}: %{value:.1f} h<extra></extra>"))
        ft.update_layout(height=340, showlegend=False, **LAYOUT)
        st.plotly_chart(ft, use_container_width=True)
    else:
        st.bar_chart(pd.Series(horas_estado, index=[e[0] for e in ESTADOS]))
    st.markdown(f"<p class='nota'>De {sum(horas_estado):.0f} horas monitoreadas, "
                f"{horas_estado[0]:.0f} transcurrieron en estado normal.</p>", unsafe_allow_html=True)

with der:
    st.markdown("## Lecturas altas por franja del día")
    altas = altas_por_franja(df, q)
    if PLOTLY:
        fa = go.Figure(go.Pie(labels=[f[0] for f in FRANJAS], values=altas,
                              marker=dict(colors=[f[2] for f in FRANJAS], line=dict(color="#FFFFFF", width=2)),
                              hole=.45, sort=False, textinfo="label+percent",
                              hovertemplate="%{label}: %{value} lecturas<extra></extra>"))
        fa.update_layout(height=340, showlegend=False, **LAYOUT)
        st.plotly_chart(fa, use_container_width=True)
    else:
        st.bar_chart(pd.Series(altas, index=[f[0] for f in FRANJAS]))
    franja_top = FRANJAS[int(np.argmax(altas))][0].lower() if sum(altas) else "—"
    st.markdown(f"<p class='nota'>Las lecturas sobre el percentil 75 se concentran en la {franja_top}.</p>",
                unsafe_allow_html=True)

st.markdown("## Comportamiento diario")
if PLOTLY:
    fd = go.Figure()
    fd.add_trace(go.Bar(x=diario["fecha"], y=diario["mean"], name="Promedio", marker_color=AZUL,
                        hovertemplate="%{x|%d/%m}<br>%{y:.3f} " + UNIDAD + "<extra></extra>"))
    fd.add_trace(go.Scatter(x=diario["fecha"], y=diario["max"], name="Máximo", mode="lines+markers",
                            line=dict(color=ESTADOS[2][1], width=1.6), marker=dict(size=5)))
    fd.add_trace(go.Scatter(x=diario["fecha"], y=diario["min"], name="Mínimo", mode="lines+markers",
                            line=dict(color=VERDE_CLARO, width=1.6), marker=dict(size=5)))
    fd.update_layout(height=360, legend=dict(orientation="h", y=1.14, x=0), yaxis_title=f"Nivel ({UNIDAD})")
    st.plotly_chart(formatear(fd), use_container_width=True)
else:
    st.bar_chart(diario.set_index("fecha")[["min", "mean", "max"]])

izq2, der2 = st.columns(2)

with izq2:
    st.markdown("## Nivel promedio por hora")
    if PLOTLY:
        valores = perfil.fillna(0)
        tope = valores.max() or 1
        colores = [f"rgba(27,127,168,{0.35 + 0.65 * (v / tope):.2f})" for v in valores]
        fh = go.Figure(go.Bar(x=[f"{h:02d}" for h in valores.index], y=valores, marker_color=colores,
                              hovertemplate="%{x}:00 h<br>%{y:.3f} " + UNIDAD + "<extra></extra>"))
        fh.update_layout(height=330, showlegend=False, xaxis_title="Hora", yaxis_title=f"Nivel ({UNIDAD})")
        st.plotly_chart(formatear(fh), use_container_width=True)
    else:
        st.bar_chart(perfil)

with der2:
    st.markdown("## Días de mayor oscilación")
    top = diario.nlargest(7, "amplitud").sort_values("amplitud")
    if PLOTLY:
        fo = go.Figure(go.Bar(x=top["amplitud"], y=top["fecha"].dt.strftime("%d/%m"), orientation="h",
                              marker_color=VERDE,
                              hovertemplate="%{y}<br>amplitud %{x:.3f} " + UNIDAD + "<extra></extra>"))
        fo.update_layout(height=330, showlegend=False, xaxis_title=f"Amplitud del día ({UNIDAD})")
        st.plotly_chart(formatear(fo), use_container_width=True)
    else:
        st.bar_chart(top.set_index("fecha")["amplitud"])

st.markdown("## Curva de duración de niveles")
cd = curva_duracion(df)
if PLOTLY:
    fc = go.Figure(go.Scatter(x=cd["excedencia"], y=cd["nivel"], mode="lines",
                              line=dict(color=VERDE, width=2.2), fill="tozeroy",
                              fillcolor="rgba(47,125,92,.14)",
                              hovertemplate="Superado el %{x:.0f} % del tiempo<br>%{y:.3f} " + UNIDAD + "<extra></extra>"))
    for pct, color in ((10, ESTADOS[3][1]), (50, TIERRA), (90, AZUL_CLARO)):
        fc.add_vline(x=pct, line=dict(color=color, width=1, dash="dot"),
                     annotation_text=f"{pct} %", annotation_font=dict(color=color, size=10))
    fc.update_layout(height=330, xaxis_title="Porcentaje del tiempo en que el nivel fue igualado o superado",
                     yaxis_title=f"Nivel ({UNIDAD})")
    st.plotly_chart(formatear(fc), use_container_width=True)
else:
    st.line_chart(cd.set_index("excedencia")["nivel"])
st.markdown(
    f"<p class='nota'>El nivel superó {np.interp(10, cd['excedencia'], cd['nivel']):.2f} {UNIDAD} solo el 10 % "
    f"del tiempo y se mantuvo sobre {np.interp(90, cd['excedencia'], cd['nivel']):.2f} {UNIDAD} el 90 % del periodo.</p>",
    unsafe_allow_html=True,
)

st.markdown("## Dónde está la estación")
punto = pd.DataFrame({"lat": [lat if lat is not None else LAT_DEFECTO],
                      "lon": [lon if lon is not None else LON_DEFECTO],
                      "color": [color_estado], "tamaño": [900]})
st.map(punto, latitude="lat", longitude="lon", color="color", size="tamaño", zoom=10)
if lat is None:
    st.markdown("<p class='nota'>La API no entregó coordenadas para esta estación: el punto corresponde al "
                "lugar de partida (Pascual Bravo, Medellín).</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p class='nota'>Coordenadas de la estación: {punto['lat'][0]:.4f}, {punto['lon'][0]:.4f}.</p>",
                unsafe_allow_html=True)

st.markdown("## Registro de lecturas")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Índice de calidad", f"{indice}/100")
c2.metric("Huecos de reporte", huecos)
c3.metric("Lecturas atípicas", n_atipicos)
c4.metric("Frecuencia", str(paso_tipico(df)))
st.dataframe(df.assign(atípico=atipicos(df)), use_container_width=True, height=320)

st.download_button("Descargar la serie en CSV", df.to_csv(index=False).encode("utf-8"),
                   file_name=f"estacion_{CODIGO_ESTACION}_{desde}_{hasta}.csv", mime="text/csv")

st.markdown(
    f"<p class='nota' style='margin-top:2rem'>Datos de la red MARCO, Sistema de Monitoreo Ambiental Regional "
    f"de CORNARE · periodo {desde:%d/%m/%Y} a {hasta:%d/%m/%Y} · calidad {CALIDAD} · elaborado por {ESTUDIANTE}.</p>",
    unsafe_allow_html=True,
)
