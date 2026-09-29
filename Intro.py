import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Portafolio de Aplicaciones", layout="wide")
st.title("Portafolio de Aplicaciones de Ciencia de Datos e IA")

with st.sidebar:
    st.subheader("Sobre este portafolio")
    st.write(
        "Colección de aplicaciones desarrolladas en Streamlit durante el curso de "
        "Programación Avanzada: regresión, clasificación, series de tiempo, IoT, "
        "detección de anomalías y preparación de datos."
    )

# ---------------------------------------------------------------
# Lista de apps: reemplaza cada "url" por tu enlace desplegado.
# "imagen" es opcional: pon el nombre del archivo si tienes una.
# ---------------------------------------------------------------
apps = [
    {
        "titulo": "Sesión 2. App de frutas",
        "descripcion": "Primera aplicación interactiva con Streamlit.",
        "url": "https://TU-APP-SESION-2.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 3. Gradiente descendente",
        "descripcion": "Visualización interactiva del algoritmo de gradiente.",
        "url": "https://TU-APP-SESION-3.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 4. Detector de anomalías",
        "descripcion": "Detección de valores atípicos en datos.",
        "url": "https://TU-APP-SESION-4.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 5. Preparación de datos",
        "descripcion": "Limpieza y transformación de datos.",
        "url": "https://TU-APP-SESION-5.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 6. Preparación de datos (Cornare)",
        "descripcion": "Aplicación práctica de preparación de datos con niveles de Cornare.",
        "url": "https://TU-APP-SESION-6.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 7. Regresión lineal",
        "descripcion": "Conceptos de regresión lineal de forma interactiva.",
        "url": "https://TU-APP-SESION-7.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 8. Series de tiempo",
        "descripcion": "Análisis y visualización de series temporales.",
        "url": "https://TU-APP-SESION-8.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 9. Calidad del aire",
        "descripcion": "Predicción y modelado de la calidad del aire (Cornare).",
        "url": "https://TU-APP-SESION-9.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 10. Sistema IoT",
        "descripcion": "Captura y procesamiento de datos propios con IoT.",
        "url": "https://TU-APP-SESION-10.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 11. Regresión logística",
        "descripcion": "De la regresión lineal a la logística.",
        "url": "https://TU-APP-SESION-11.streamlit.app/",
        "imagen": None,
    },
    {
        "titulo": "Sesión 12. KNN: fertilidad de suelos",
        "descripcion": "Clasificación de la fertilidad de suelos con K-Nearest Neighbors.",
        "url": "https://TU-APP-SESION-12.streamlit.app/",
        "imagen": None,
    },
]

# Enlace general (opcional): si no lo necesitas, borra estas 3 líneas
url_ia = "https://sites.google.com/view/aplicacionesdeia/inicio"
st.subheader("Más páginas y ejercicios prácticos")
st.write(f"[Ir al sitio de ejercicios]({url_ia})")

st.divider()

# Cuadrícula de 3 columnas: reparte las apps en orden
cols = st.columns(3)
for i, app in enumerate(apps):
    with cols[i % 3]:
        st.subheader(app["titulo"])
        if app["imagen"] and os.path.exists(app["imagen"]):
            st.image(Image.open(app["imagen"]), width=200)
        st.write(app["descripcion"])
        st.link_button("Abrir app", app["url"])
        st.write("")  # espacio entre tarjetas
