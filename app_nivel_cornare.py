"""
App básica de Streamlit — Nivel de ríos/quebradas (CORNARE / MARCO)
--------------------------------------------------------------------
Cada estudiante debe cambiar, como mínimo, el código de la estación
en el sidebar. Los valores de fecha y calidad también son ajustables.

Para correrla:
    streamlit run app_nivel_cornare.py
"""

import requests
import pandas as pd
import numpy as np
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------------------------------------------------------
# Coordenadas por defecto (Institución Universitaria Pascual Bravo)
# Se usan solo si la API no trae la latitud/longitud de la estación.
# ------------------------------------------------------------------
LAT_DEFECTO = 6.2766
LON_DEFECTO = -75.5901

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"
CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]

SEMAFORO = [
    ("🟢", "Normal", "#2ECC71"),
    ("🟡", "Atención", "#F1C40F"),
    ("🟠", "Alerta", "#E67E22"),
    ("🔴", "Crítico", "#E74C3C"),
]

st.set_page_config(page_title="Nivel de estación — CORNARE", page_icon="🌊", layout="wide")


# ------------------------------------------------------------------
# Funciones de consulta
# ------------------------------------------------------------------
def obtener_serie_nivel(codigo_estacion, desde, hasta, calidad=1, timeout=30):
    url = f"{API_BASE_URL}/{codigo_estacion}/nivel"
    params = {"desde": desde, "hasta": hasta, "calidad": calidad}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"
    except requests.exceptions.RequestException as e:
        return None, f"Error de red: {e}"


def obtener_todas_las_paginas(datos_json, timeout=30):
    registros = list(datos_json.get("values", []))
    siguiente_url = datos_json.get("next")
    while siguiente_url:
        try:
            resp = requests.get(siguiente_url, timeout=timeout, verify=False)
        except requests.exceptions.RequestException:
            break
        if resp.status_code != 200:
            break
        pagina = resp.json()
        registros.extend(pagina.get("values", []))
        siguiente_url = pagina.get("next")
    return registros


def detectar_coordenadas(datos_json):
    """Busca lat/lon en las llaves raíz de la respuesta. Si no las encuentra, usa el valor por defecto."""
    if not isinstance(datos_json, dict):
        return LAT_DEFECTO, LON_DEFECTO, False

    lat = next((datos_json[k] for k in CANDIDATOS_LAT if k in datos_json), None)
    lon = next((datos_json[k] for k in CANDIDATOS_LON if k in datos_json), None)

    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon), True
        except (TypeError, ValueError):
            pass
    return LAT_DEFECTO, LON_DEFECTO, False


def calcular_indice_calidad(df):
    """Índice simple (0-100) combinando completitud de la serie y proporción de outliers."""
    if df.empty or len(df) < 2:
        return 0.0, 0, 0

    df_idx = df.set_index("fecha")
    frecuencia_tipica = df["fecha"].diff().dropna().mode()
    if len(frecuencia_tipica) == 0:
        return 0.0, 0, 0
    frecuencia_tipica = frecuencia_tipica[0]

    rango_completo = pd.date_range(start=df_idx.index.min(), end=df_idx.index.max(), freq=frecuencia_tipica)
    esperados = len(rango_completo)
    huecos = esperados - len(df_idx)
    completitud = max(0.0, 1 - (huecos / esperados)) if esperados > 0 else 0.0

    Q1, Q3 = df["nivel"].quantile(0.25), df["nivel"].quantile(0.75)
    IQR = Q3 - Q1
    lim_inf, lim_sup = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    es_outlier = (df["nivel"] < lim_inf) | (df["nivel"] > lim_sup) | (df["nivel"] < 0)
    proporcion_outliers = es_outlier.mean()

    indice = (completitud * 0.7 + (1 - proporcion_outliers) * 0.3) * 100
    return round(indice, 1), int(huecos), int(es_outlier.sum())


# ------------------------------------------------------------------
# Funciones de análisis y métricas
# ------------------------------------------------------------------
def construir_dataframe(registros):
    df = pd.DataFrame(registros)
    df = df.rename(columns={LLAVE_FECHA: "fecha", LLAVE_VALOR: "nivel"})
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    return df.dropna(subset=["fecha", "nivel"]).sort_values("fecha").reset_index(drop=True)


def paso_tipico(df):
    diferencias = df["fecha"].diff().dropna()
    if diferencias.empty:
        return pd.Timedelta(minutes=10)
    modo = diferencias.mode()
    return modo.iloc[0] if len(modo) else diferencias.median()


def calcular_umbrales(df):
    nivel = df["nivel"]
    return {
        "min": float(nivel.min()),
        "p25": float(nivel.quantile(0.25)),
        "p50": float(nivel.quantile(0.50)),
        "p75": float(nivel.quantile(0.75)),
        "p90": float(nivel.quantile(0.90)),
        "p97": float(nivel.quantile(0.97)),
        "max": float(nivel.max()),
    }


def clasificar_estado(nivel, umbrales):
    if nivel >= umbrales["p97"]:
        return 3
    if nivel >= umbrales["p90"]:
        return 2
    if nivel >= umbrales["p75"]:
        return 1
    return 0


def calcular_tasa_cambio(df, ventana_minutos=30):
    if len(df) < 2:
        return pd.Series(0.0, index=df.index)
    pasos = max(1, int(round(pd.Timedelta(minutes=ventana_minutos) / paso_tipico(df))))
    pasos = min(pasos, max(1, len(df) // 3))
    suave = df["nivel"].rolling(pasos, min_periods=1).median()
    horas = (df["fecha"] - df["fecha"].shift(pasos)).dt.total_seconds() / 3600
    return ((suave - suave.shift(pasos)) / horas.replace(0, np.nan)).fillna(0)


def calcular_tendencia(df, horas=6):
    corte = df["fecha"].max() - pd.Timedelta(hours=horas)
    sub = df[df["fecha"] >= corte]
    if len(sub) < 3:
        return 0.0
    x = (sub["fecha"] - sub["fecha"].min()).dt.total_seconds().to_numpy() / 3600
    if np.ptp(x) == 0:
        return 0.0
    return float(np.polyfit(x, sub["nivel"].to_numpy(), 1)[0])


def variacion_en_horas(df, horas=24):
    referencia = df[df["fecha"] <= df["fecha"].max() - pd.Timedelta(hours=horas)]
    if referencia.empty:
        return float("nan")
    return float(df["nivel"].iloc[-1] - referencia["nivel"].iloc[-1])


def serie_con_umbrales(df, umbrales, ventana):
    tabla = pd.DataFrame(index=df["fecha"])
    tabla["Nivel"] = df["nivel"].to_numpy()
    tabla["Media móvil"] = df["nivel"].rolling(ventana, center=True, min_periods=1).mean().to_numpy()
    tabla["Atención (P75)"] = umbrales["p75"]
    tabla["Alerta (P90)"] = umbrales["p90"]
    tabla["Crítico (P97)"] = umbrales["p97"]
    return tabla


def construir_histograma(df, bins=25):
    conteo, bordes = np.histogram(df["nivel"].to_numpy(), bins=bins)
    centros = np.round((bordes[:-1] + bordes[1:]) / 2, 3)
    return pd.DataFrame({"Nivel": centros, "Lecturas": conteo}).set_index("Nivel")


def perfil_horario(df):
    d = df.copy()
    d["Hora"] = d["fecha"].dt.hour
    perfil = d.groupby("Hora")["nivel"].agg(Mínimo="min", Promedio="mean", Máximo="max")
    return perfil


def resumen_diario(df):
    diario = df.set_index("fecha")["nivel"].resample("1D").agg(Mínimo="min", Promedio="mean", Máximo="max")
    return diario.dropna()


def rachas_de_ascenso(df):
    signo = np.sign(df["nivel"].diff().fillna(0))
    grupo = (signo != signo.shift()).cumsum()
    tramos = df.assign(signo=signo, grupo=grupo)
    ascensos = tramos[tramos["signo"] > 0].groupby("grupo").agg(
        Inicio=("fecha", "first"),
        Fin=("fecha", "last"),
        Desde=("nivel", "first"),
        Hasta=("nivel", "last"),
    )
    if ascensos.empty:
        return ascensos
    ascensos["Ascenso"] = (ascensos["Hasta"] - ascensos["Desde"]).round(3)
    ascensos["Minutos"] = (ascensos["Fin"] - ascensos["Inicio"]).dt.total_seconds() / 60
    return ascensos.sort_values("Ascenso", ascending=False).reset_index(drop=True)


def diagrama_histeresis(df):
    d = df.copy()
    d["Tasa"] = calcular_tasa_cambio(d).to_numpy()
    d["Hora"] = d["fecha"].dt.hour
    return d[["nivel", "Tasa", "Hora"]].rename(columns={"nivel": "Nivel"})


def rango_anterior(desde, hasta):
    inicio, fin = pd.to_datetime(desde), pd.to_datetime(hasta)
    duracion = fin - inicio
    nuevo_fin = inicio - pd.Timedelta(days=1)
    nuevo_inicio = nuevo_fin - duracion
    return nuevo_inicio.strftime("%Y-%m-%d"), nuevo_fin.strftime("%Y-%m-%d")


def alinear_por_horas(df):
    horas = ((df["fecha"] - df["fecha"].min()).dt.total_seconds() / 3600).round(1)
    return pd.Series(df["nivel"].to_numpy(), index=horas.to_numpy()).groupby(level=0).mean()


# ------------------------------------------------------------------
# Sidebar — parámetros de la consulta (editables por cada estudiante)
# ------------------------------------------------------------------
st.sidebar.header("Parámetros de tu consulta")
nombre_estudiante = st.sidebar.text_input("Nombre del estudiante", "Tu Nombre Aquí")
codigo_estacion = st.sidebar.text_input("Código de estación", "42")
fecha_desde = st.sidebar.date_input("Desde", pd.to_datetime("2026-08-23")).strftime("%Y-%m-%d")
fecha_hasta = st.sidebar.date_input("Hasta", pd.to_datetime("2026-08-30")).strftime("%Y-%m-%d")
calidad = st.sidebar.selectbox("Calidad", [1, 0], index=0, help="1 = solo datos validados")
unidad = st.sidebar.text_input("Unidad del nivel", "m", max_chars=6)
comparar_periodo = st.sidebar.checkbox("Comparar con el periodo anterior", value=False)
consultar = st.sidebar.button("🔍 Consultar", type="primary")

st.title("🌊 Nivel de ríos y quebradas — CORNARE")
st.caption(f"Estudiante: **{nombre_estudiante}** · Estación: **{codigo_estacion}**")

# ------------------------------------------------------------------
# Consulta y procesamiento
# ------------------------------------------------------------------
if consultar:
    with st.spinner("Consultando la API..."):
        datos_crudos, error = obtener_serie_nivel(codigo_estacion, fecha_desde, fecha_hasta, calidad)

    if error:
        st.error(f"❌ {error}")
    else:
        registros = obtener_todas_las_paginas(datos_crudos)

        if not registros:
            st.warning("No hay registros para esta estación y rango de fechas. Prueba otro código u otro rango.")
        else:
            df = construir_dataframe(registros)

            lat, lon, coords_reales = detectar_coordenadas(datos_crudos)
            indice_calidad, huecos, n_outliers = calcular_indice_calidad(df)

            umbrales = calcular_umbrales(df)
            nivel_actual = float(df["nivel"].iloc[-1])
            nivel_previo = float(df["nivel"].iloc[-2]) if len(df) > 1 else nivel_actual
            idx_estado = clasificar_estado(nivel_actual, umbrales)
            emoji_estado, texto_estado, color_estado = SEMAFORO[idx_estado]
            tasas = calcular_tasa_cambio(df)
            pendiente = calcular_tendencia(df, 6)
            delta_24 = variacion_en_horas(df, 24)
            percentil_actual = float((df["nivel"] <= nivel_actual).mean() * 100)

            # --- Métricas principales ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Lecturas", len(df))
            col2.metric("Nivel promedio", f"{df['nivel'].mean():.2f}")
            col3.metric("Índice de calidad", f"{indice_calidad} / 100")
            col4.metric("Outliers detectados", n_outliers)

            col5, col6, col7, col8 = st.columns(4)
            col5.metric(f"Nivel actual ({unidad})", f"{nivel_actual:.2f}", f"{nivel_actual - nivel_previo:+.3f}")
            col6.metric(f"Tendencia 6 h ({unidad}/h)", f"{pendiente:+.3f}")
            col7.metric(f"Variación 24 h ({unidad})", "sin dato" if pd.isna(delta_24) else f"{delta_24:+.2f}")
            col8.metric("Estado del cauce", f"{emoji_estado} {texto_estado}", f"percentil {percentil_actual:.0f}")

            col9, col10, col11, col12 = st.columns(4)
            col9.metric(f"Máximo ({unidad})", f"{umbrales['max']:.2f}")
            col10.metric(f"Mínimo ({unidad})", f"{umbrales['min']:.2f}")
            col11.metric(f"Amplitud ({unidad})", f"{umbrales['max'] - umbrales['min']:.2f}")
            col12.metric(f"Ascenso más rápido ({unidad}/h)", f"{tasas.max():+.3f}")

            st.progress(min(1.0, indice_calidad / 100), text=f"Calidad de la serie: {indice_calidad} / 100")

            # --- Gráfico de la serie ---
            st.subheader("Serie de nivel")
            ventana_media = max(3, len(df) // 24)
            st.line_chart(
                serie_con_umbrales(df, umbrales, ventana_media),
                color=["#1F77B4", "#7F8C8D", "#F1C40F", "#E67E22", "#E74C3C"],
            )
            st.caption(
                f"Media móvil de {ventana_media} lecturas. Los umbrales son los percentiles 75, 90 y 97 del periodo consultado."
            )

            st.subheader("📈 Velocidad de subida y bajada")
            st.bar_chart(pd.DataFrame({"Tasa": tasas.to_numpy()}, index=df["fecha"]), color="#3498DB")
            st.caption(f"Cambio de nivel en {unidad}/h medido sobre ventanas de 30 minutos.")

            col_izq, col_der = st.columns(2)
            with col_izq:
                st.subheader("📊 Distribución del nivel")
                st.bar_chart(construir_histograma(df), color="#2E86C1")
            with col_der:
                st.subheader("🕒 Ciclo de un día promedio")
                st.line_chart(perfil_horario(df), color=["#5DADE2", "#1F77B4", "#154360"])

            st.subheader("📅 Resumen por día")
            st.bar_chart(resumen_diario(df), color=["#AED6F1", "#5499C7", "#1B4F72"])

            st.subheader("🌀 Nivel contra velocidad de cambio")
            st.scatter_chart(diagrama_histeresis(df), x="Nivel", y="Tasa", color="Hora", size=18)
            st.caption(
                "Cada punto es una lectura. Los lazos hacia arriba indican crecientes y los lazos hacia abajo, recesiones."
            )

            # --- Mapa de la estación ---
            st.subheader("Ubicación de la estación")
            if not coords_reales:
                st.caption("La API no trajo latitud/longitud de la estación — se muestra el punto de partida (Pascual Bravo). Ajusta `CANDIDATOS_LAT` / `CANDIDATOS_LON` si conoces el nombre real de esas llaves.")
            st.map(
                pd.DataFrame({"lat": [lat], "lon": [lon], "color": [color_estado], "tamaño": [900]}),
                latitude="lat",
                longitude="lon",
                color="color",
                size="tamaño",
                zoom=10,
            )
            st.caption(f"El punto toma el color del estado actual: {emoji_estado} {texto_estado}.")

            if comparar_periodo:
                st.subheader("🔁 Comparación con el periodo anterior")
                desde_prev, hasta_prev = rango_anterior(fecha_desde, fecha_hasta)
                with st.spinner("Consultando el periodo anterior..."):
                    datos_prev, error_prev = obtener_serie_nivel(codigo_estacion, desde_prev, hasta_prev, calidad)
                registros_prev = obtener_todas_las_paginas(datos_prev) if not error_prev else []
                if not registros_prev:
                    st.info(f"Sin datos entre {desde_prev} y {hasta_prev} para comparar.")
                else:
                    df_prev = construir_dataframe(registros_prev)
                    comparativo = pd.DataFrame(
                        {"Periodo actual": alinear_por_horas(df), "Periodo anterior": alinear_por_horas(df_prev)}
                    )
                    st.line_chart(comparativo, color=["#1F77B4", "#B0B0B0"])
                    st.caption(f"Eje horizontal en horas desde el inicio de cada periodo. Anterior: {desde_prev} a {hasta_prev}.")

                    cp1, cp2, cp3 = st.columns(3)
                    cp1.metric(
                        f"Promedio ({unidad})",
                        f"{df['nivel'].mean():.2f}",
                        f"{df['nivel'].mean() - df_prev['nivel'].mean():+.2f}",
                    )
                    cp2.metric(
                        f"Máximo ({unidad})",
                        f"{df['nivel'].max():.2f}",
                        f"{df['nivel'].max() - df_prev['nivel'].max():+.2f}",
                    )
                    cp3.metric("Lecturas", len(df), int(len(df) - len(df_prev)))

            # --- Detalle de calidad ---
            with st.expander("Detalle del índice de calidad"):
                st.write(f"- Huecos de reporte detectados: **{huecos}**")
                st.write(f"- Outliers (IQR + nivel negativo): **{n_outliers}** de {len(df)} lecturas")
                st.write(f"- Frecuencia típica de reporte: **{paso_tipico(df)}**")
                st.write("El índice combina completitud de la serie (70%) y proporción de datos sin outliers (30%).")

            with st.expander("Mayores ascensos del periodo"):
                rachas = rachas_de_ascenso(df)
                if rachas.empty:
                    st.write("El nivel no registró tramos de ascenso sostenido en este periodo.")
                else:
                    st.dataframe(rachas.head(10), use_container_width=True)

            with st.expander("Percentiles del periodo"):
                st.dataframe(
                    pd.DataFrame(
                        {"Referencia": list(umbrales.keys()), f"Nivel ({unidad})": [round(v, 3) for v in umbrales.values()]}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            # --- Tabla y descarga ---
            with st.expander("Ver datos crudos"):
                st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar CSV", csv, file_name=f"nivel_estacion_{codigo_estacion}.csv", mime="text/csv")
else:
    st.info("Ajusta los parámetros en el sidebar y presiona **Consultar**.")
