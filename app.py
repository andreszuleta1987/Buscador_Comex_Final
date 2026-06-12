import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex", layout="wide")


@st.cache_data
def cargar_datos():
    # 1. Cargar datos principales
    df = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')
    df = df.rename(columns={df.columns[0]: "FECHA_PROCESO"})

    # 2. Cargar archivo de descripciones
    arancel = pd.read_csv("arancel_convertido.csv", encoding='latin-1')

    # 3. Cruzar ambos dataframes por la columna SUBPARTIDA
    # Aseguramos que ambas columnas sean tipo string para que el merge funcione
    df['SUBPARTIDA'] = df['SUBPARTIDA'].astype(str)
    arancel['Subpartida'] = arancel['Subpartida'].astype(str)

    df_final = pd.merge(df, arancel, left_on='SUBPARTIDA', right_on='Subpartida', how='left')
    return df_final


st.title("🔎 Buscador Comex")

try:
    df = cargar_datos()

    col1, col2 = st.columns(2)
    with col1:
        buscar_empresa = st.text_input("Filtrar por Empresa:")
    with col2:
        # Nuevo filtro para descripciones
        buscar_descripcion = st.text_input("Buscar por nombre (ej: Hass, Aguacate):")

    df_filtrado = df.copy()

    if buscar_empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False, na=False)]

    if buscar_descripcion:
        # Filtra sobre la columna 'Descripción' que viene del archivo arancel_convertido.csv
        df_filtrado = df_filtrado[
            df_filtrado['Descripción'].astype(str).str.contains(buscar_descripcion, case=False, na=False)]

    if buscar_empresa or buscar_descripcion:
        st.write(f"Resultados: {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Escribe en los filtros para ver los resultados.")

except Exception as e:
    st.error(f"Error al procesar datos: {e}")
