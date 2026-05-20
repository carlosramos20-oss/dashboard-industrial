import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ====================================
# CONFIGURACIÓN STREAMLIT
# ====================================

st.set_page_config(
    page_title="Dashboard Industrial",
    layout="wide"
)

# ====================================
# TÍTULO
# ====================================

st.title("Dashboard de Producción Industrial")

st.write("Sistema automatizado de KPIs conectado a Google Sheets")

# ====================================
# CONEXIÓN GOOGLE SHEETS
# ====================================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import streamlit as st

credenciales_dict = dict(st.secrets["gcp_service_account"])

credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    credenciales_dict,
    scope
)

cliente = gspread.authorize(credenciales)

# ====================================
# ABRIR GOOGLE SHEET
# ====================================

sheet = cliente.open(
    "Produccion_Industrial"
).sheet1

# ====================================
# LEER DATOS
# ====================================

datos = sheet.get_all_records()

datos = pd.DataFrame(datos)

# ====================================
# LIMPIEZA DE DATOS
# ====================================

datos = datos.dropna(subset=["Producción"])

datos["Producción"] = pd.to_numeric(
    datos["Producción"],
    errors="coerce"
)

datos["Defectos"] = pd.to_numeric(
    datos["Defectos"],
    errors="coerce"
)

datos["Horas_Trabajadas"] = pd.to_numeric(
    datos["Horas_Trabajadas"],
    errors="coerce"
)

datos["Tiempo_Muerto"] = pd.to_numeric(
    datos["Tiempo_Muerto"],
    errors="coerce"
)

# ====================================
# ELIMINAR FILAS INVÁLIDAS
# ====================================

datos = datos.dropna(
    subset=[
        "Producción",
        "Defectos",
        "Horas_Trabajadas",
        "Tiempo_Muerto"
    ]
)

# ====================================
# KPIs CALCULADOS
# ====================================

datos["Productividad"] = (
    datos["Producción"]
    /
    datos["Horas_Trabajadas"]
).round(2)

datos["Porcentaje_Defectos"] = (
    datos["Defectos"]
    /
    datos["Producción"]
    * 100
).round(2)

datos["Disponibilidad"] = (
    (
        datos["Horas_Trabajadas"] * 60
        - datos["Tiempo_Muerto"]
    )
    /
    (datos["Horas_Trabajadas"] * 60)
    * 100
).round(2)

# ====================================
# ALERTAS
# ====================================

datos["Alerta"] = ""

datos.loc[
    datos["Porcentaje_Defectos"] > 4,
    "Alerta"
] += "Defectos altos "

datos.loc[
    datos["Tiempo_Muerto"] > 30,
    "Alerta"
] += "Tiempo muerto alto"

# ====================================
# FILTRO SIDEBAR
# ====================================

st.sidebar.header("Filtros")

turno = st.sidebar.selectbox(
    "Seleccionar turno",
    ["Todos"] + list(datos["Turno"].unique())
)

# ====================================
# APLICAR FILTRO
# ====================================

if turno != "Todos":

    datos = datos[
        datos["Turno"] == turno
    ]

# ====================================
# KPIs GENERALES
# ====================================

produccion_total = datos["Producción"].sum()

defectos_totales = datos["Defectos"].sum()

promedio_productividad = (
    datos["Productividad"].mean()
).round(2)

# ====================================
# MOSTRAR KPIs
# ====================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Producción Total",
    produccion_total
)

col2.metric(
    "Defectos Totales",
    defectos_totales
)

col3.metric(
    "Promedio Productividad",
    promedio_productividad
)

# ====================================
# TABLA DE DATOS
# ====================================

st.subheader("Datos de Producción")

st.dataframe(datos)

# ====================================
# GRÁFICO PRODUCCIÓN
# ====================================

st.subheader("Producción por Registro")

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    datos.index.astype(str),
    datos["Producción"]
)

ax.set_xlabel("Registro")

ax.set_ylabel("Producción")

plt.xticks(rotation=45)

st.pyplot(fig)

# ====================================
# GRÁFICO PRODUCTIVIDAD
# ====================================

st.subheader("Productividad")

fig2, ax2 = plt.subplots(figsize=(10, 5))

ax2.plot(
    datos.index,
    datos["Productividad"],
    marker="o"
)

ax2.set_xlabel("Registro")

ax2.set_ylabel("Productividad")

st.pyplot(fig2)

# ====================================
# ALERTAS DETECTADAS
# ====================================

st.subheader("Alertas Detectadas")

alertas = datos[
    datos["Alerta"] != ""
]

st.dataframe(alertas)
