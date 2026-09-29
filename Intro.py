import streamlit as st
import base64
import os

st.set_page_config(
    page_title="Portafolio Programación Avanzada",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp {
    background: radial-gradient(circle at 10% 0%, #1e1b4b 0%, #0f172a 45%, #020617 100%);
}
.stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: #e2e8f0; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1250px; }

/* HERO */
.hero {
    background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 40%, #ec4899 100%);
    border-radius: 28px;
    padding: 52px 40px;
    margin-bottom: 28px;
    box-shadow: 0 20px 50px rgba(99, 102, 241, .35);
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero::after {
    content: "🤖 📊 🧠";
    position: absolute; right: 30px; top: 20px;
    font-size: 60px; opacity: .22; letter-spacing: 10px;
}
.hero h1 { color: #fff !important; font-size: 2.8rem; font-weight: 800; margin: 0 0 10px 0; }
.hero .autor {
    display: inline-block; padding: 8px 24px;
    background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.4);
    border-radius: 999px; color: #fff !important; font-weight: 600; font-size: 1.05rem;
    backdrop-filter: blur(6px);
}

/* KPIs */
.kpis {
    display: flex; justify-content: center; gap: 22px; flex-wrap: wrap;
    margin-bottom: 40px;
}
.kpi {
    min-width: 220px; text-align: center; padding: 22px 30px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 20px; backdrop-filter: blur(8px);
    transition: transform .3s, border-color .3s;
}
.kpi:hover { transform: translateY(-5px); border-color: rgba(255,255,255,.4); }
.kpi .valor {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi .etiqueta { font-size: .9rem; color: #cbd5e1; margin-top: 4px; }

/* TARJETAS */
.card {
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 22px;
    overflow: hidden;
    margin-bottom: 24px;
    transition: transform .3s, box-shadow .3s, border-color .3s;
    backdrop-filter: blur(8px);
}
.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 18px 40px rgba(0,0,0,.5);
    border-color: rgba(255,255,255,.35);
}
.card-top {
    height: 140px; display: flex; align-items: center; justify-content: center;
    font-size: 64px; position: relative;
}
.card-top img { width: 100%; height: 100%; object-fit: cover; }
.badge-num {
    position: absolute; top: 12px; left: 14px;
    background: rgba(0,0,0,.35); color: #fff; font-size: 12px; font-weight: 600;
    padding: 4px 12px; border-radius: 999px;
}
.card-body { padding: 18px 20px 22px 20px; }
.card-body h3 { color: #fff !important; font-size: 1.1rem; font-weight: 600; margin: 0 0 8px 0; }
.card-body p  { font-size: .88rem; color: #cbd5e1 !important; min-height: 60px; margin: 0 0 12px 0; }
.tag {
    display: inline-block; background: rgba(99,102,241,.22); color: #c7d2fe;
    font-size: 11px; padding: 3px 10px; border-radius: 999px; margin: 0 4px 6px 0;
    border: 1px solid rgba(99,102,241,.4);
}
.btn {
    display: block; text-align: center; margin-top: 10px; padding: 10px;
    background: linear-gradient(90deg, #6366f1, #ec4899);
    color: #fff !important; font-weight: 600; text-decoration: none;
    border-radius: 12px; transition: all .25s;
}
.btn:hover { filter: brightness(1.15); letter-spacing: .5px; }

.footer { text-align: center; color: #64748b; font-size: 13px; margin-top: 30px; padding-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# DATOS: reemplaza cada "url" por tu enlace desplegado.
# "imagen": nombre de archivo opcional (si no, se usa el emoji).
# ---------------------------------------------------------------
apps = [
    {"n": 2,  "emoji": "🍎", "titulo": "App de frutas",
     "desc": "Primera aplicación interactiva construida con Streamlit.",
     "tags": ["Streamlit", "Python"], "colores": ("#f97316", "#ef4444"),
     "url": "https://TU-APP-SESION-2.streamlit.app/", "imagen": None},

    {"n": 3,  "emoji": "📉", "titulo": "Gradiente descendente",
     "desc": "Visualiza cómo el algoritmo de gradiente encuentra el mínimo de una función.",
     "tags": ["Optimización", "Visualización"], "colores": ("#06b6d4", "#3b82f6"),
     "url": "https://TU-APP-SESION-3.streamlit.app/", "imagen": None},

    {"n": 4,  "emoji": "🚨", "titulo": "Detector de anomalías",
     "desc": "Identifica valores atípicos en conjuntos de datos de forma interactiva.",
     "tags": ["Anomalías", "Estadística"], "colores": ("#ef4444", "#be123c"),
     "url": "https://TU-APP-SESION-4.streamlit.app/", "imagen": None},

    {"n": 5,  "emoji": "🧹", "titulo": "Preparación de datos",
     "desc": "Limpieza, transformación y preparación de datos antes de modelar.",
     "tags": ["Pandas", "Limpieza"], "colores": ("#10b981", "#059669"),
     "url": "https://TU-APP-SESION-5.streamlit.app/", "imagen": None},

    {"n": 6,  "emoji": "🌊", "titulo": "Preparación de datos · Cornare",
     "desc": "Caso práctico de preparación de datos con niveles de Cornare.",
     "tags": ["Caso real", "Pandas"], "colores": ("#0ea5e9", "#0369a1"),
     "url": "https://TU-APP-SESION-6.streamlit.app/", "imagen": None},

    {"n": 7,  "emoji": "📈", "titulo": "Regresión lineal",
     "desc": "Conceptos clave de la regresión lineal explicados de forma interactiva.",
     "tags": ["Regresión", "Scikit-learn"], "colores": ("#8b5cf6", "#6d28d9"),
     "url": "https://TU-APP-SESION-7.streamlit.app/", "imagen": None},

    {"n": 8,  "emoji": "⏳", "titulo": "Series de tiempo",
     "desc": "Análisis, descomposición y visualización de series temporales.",
     "tags": ["Tendencia", "Estacionalidad"], "colores": ("#f59e0b", "#d97706"),
     "url": "https://TU-APP-SESION-8.streamlit.app/", "imagen": None},

    {"n": 9,  "emoji": "🌬️", "titulo": "Calidad del aire · Pronóstico",
     "desc": "Predicción y modelado de la calidad del aire con datos de Cornare.",
     "tags": ["Pronóstico", "Ambiental"], "colores": ("#14b8a6", "#0f766e"),
     "url": "https://TU-APP-SESION-9.streamlit.app/", "imagen": None},

    {"n": 10, "emoji": "📡", "titulo": "Sistema IoT",
     "desc": "Captura y procesamiento de datos propios usando tecnologías IoT.",
     "tags": ["IoT", "Sensores", "Tiempo real"], "colores": ("#ec4899", "#be185d"),
     "url": "https://TU-APP-SESION-10.streamlit.app/", "imagen": None},

    {"n": 11, "emoji": "🎯", "titulo": "Regresión logística",
     "desc": "Del modelo lineal al logístico: clasificación binaria paso a paso.",
     "tags": ["Clasificación", "Probabilidad"], "colores": ("#6366f1", "#4338ca"),
     "url": "https://TU-APP-SESION-11.streamlit.app/", "imagen": None},

    {"n": 12, "emoji": "🌱", "titulo": "KNN · Fertilidad de suelos",
     "desc": "Clasificación de la fertilidad de suelos con K-Nearest Neighbors.",
     "tags": ["KNN", "Agro", "Clasificación"], "colores": ("#84cc16", "#4d7c0f"),
     "url": "https://TU-APP-SESION-12.streamlit.app/", "imagen": None},
]

# ---------------------------------------------------------------
# KPIs: edita los valores y etiquetas a tu gusto
# ---------------------------------------------------------------
kpis = [
    (str(len(apps)), "Apps desplegadas"),
    ("2 – 12", "Sesiones cubiertas"),
    ("Streamlit", "Plataforma de despliegue"),
]


def img_base64(ruta):
    """Convierte una imagen local a base64 para incrustarla en el HTML."""
    if ruta and os.path.exists(ruta):
        ext = ruta.split(".")[-1].lower()
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        with open(ruta, "rb") as f:
            return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"
    return None


def tarjeta(app):
    c1, c2 = app["colores"]
    src = img_base64(app["imagen"])
    visual = f'<img src="{src}">' if src else app["emoji"]
    tags = "".join(f'<span class="tag">{t}</span>' for t in app["tags"])
    return (
        f'<div class="card">'
        f'<div class="card-top" style="background: linear-gradient(135deg, {c1}, {c2});">'
        f'<span class="badge-num">Sesión {app["n"]}</span>{visual}</div>'
        f'<div class="card-body"><h3>{app["titulo"]}</h3>'
        f'<p>{app["desc"]}</p>{tags}'
        f'<a class="btn" href="{app["url"]}" target="_blank">Abrir app →</a>'
        f'</div></div>'
    )


# ---------------------------------------------------------------
# HERO
# ---------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Portafolio Programación Avanzada</h1>
    <span class="autor">👨‍💻 Nicolas Cataño Durango</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# KPIs (centrados)
# ---------------------------------------------------------------
kpi_html = "".join(
    f'<div class="kpi"><div class="valor">{v}</div><div class="etiqueta">{e}</div></div>'
    for v, e in kpis
)
st.markdown(f'<div class="kpis">{kpi_html}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# GALERÍA
# ---------------------------------------------------------------
for i in range(0, len(apps), 3):
    cols = st.columns(3, gap="large")
    for col, app in zip(cols, apps[i:i + 3]):
        with col:
            st.markdown(tarjeta(app), unsafe_allow_html=True)

st.markdown(
    '<div class="footer">Hecho con ❤️ y Streamlit · Nicolas Cataño Durango</div>',
    unsafe_allow_html=True,
)
