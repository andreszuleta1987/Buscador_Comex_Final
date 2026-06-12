import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex Local", layout="wide")


# Función para cargar datos desde un archivo local
@st.cache_data
def cargar_datos_locales():
    # Asegúrate de que el nombre del archivo coincida exactamente con el que tienes en tu carpeta
    df = pd.read_csv("arancel_convertido.csv")
    return df


st.title("🔎 Buscador Comex — Modo Local")

try:
    df = cargar_datos_locales()

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        buscar_empresa = st.text_input("Filtrar por Empresa:")
    with col2:
        buscar_texto = st.text_input("Buscar por Subpartida o Palabra:")

    df_filtrado = df.copy()

    # Filtro de Empresa (ajusta 'RAZON_SOCIAL' al nombre real de tu columna en el CSV)
    if buscar_empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False, na=False)]

    # Filtro de Subpartida/Palabra
    if buscar_texto:
        df_filtrado = df_filtrado[
            df_filtrado['SUBPARTIDA'].astype(str).str.contains(buscar_texto, case=False, na=False)]

    st.write(f"Resultados encontrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar el archivo local: {e}. Verifica que 'arancel_convertido.csv' esté en la carpeta.")