import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex", layout="wide")


@st.cache_data
def cargar_datos_locales():
    # Usamos 'latin-1' porque es el estándar que mejor lee tus archivos de Excel
    df = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')

    # Limpiamos el nombre de la columna que vimos en el diagnóstico
    df = df.rename(columns={df.columns[0]: "FECHA_PROCESO"})
    return df


st.title("🔎 Buscador Comex")

try:
    df = cargar_datos_locales()

    col1, col2 = st.columns(2)
    with col1:
        buscar_empresa = st.text_input("Filtrar por Empresa:")
    with col2:
        buscar_texto = st.text_input("Buscar por Subpartida:")

    df_filtrado = df.copy()

    if buscar_empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False, na=False)]

    if buscar_texto:
        df_filtrado = df_filtrado[
            df_filtrado['SUBPARTIDA'].astype(str).str.contains(buscar_texto, case=False, na=False)]

    st.write(f"Resultados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
