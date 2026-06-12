import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex", layout="wide")


@st.cache_data
def cargar_datos():
    df = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')
    df = df.rename(columns={df.columns[0]: "FECHA_PROCESO"})

    arancel = pd.read_csv("arancel_convertido.csv", encoding='latin-1', sep=';')

    df['SUBPARTIDA'] = df['SUBPARTIDA'].astype(str)
    arancel['SUBPARTIDA'] = arancel['SUBPARTIDA'].astype(str)

    return pd.merge(df, arancel, on='SUBPARTIDA', how='left')


st.title("🔎 Buscador Comex")

try:
    df = cargar_datos()

    # Filtros principales siempre visibles
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Filtrar por Empresa (Exportador):")
    with col2:
        descripcion = st.text_input("Buscar por Nombre de producto:")

    # Filtros avanzados en un expansor
    with st.expander("⚙️ Filtros Avanzados"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nit = st.text_input("NIT Exportador:")
        with c2:
            subpartida = st.text_input("Subpartida numérica:")
        with c3:
            agencia = st.text_input("Agencia de Aduanas:")

    df_filtrado = df.copy()

    # Aplicación de filtros
    if empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(empresa, case=False, na=False)]
    if descripcion:
        df_filtrado = df_filtrado[
            df_filtrado['DESCRIPCION_SUBPARTIDA'].astype(str).str.contains(descripcion, case=False, na=False)]
    if nit:
        df_filtrado = df_filtrado[df_filtrado['NIT_EXPORTADOR'].astype(str).str.contains(nit, case=False, na=False)]
    if subpartida:
        df_filtrado = df_filtrado[df_filtrado['SUBPARTIDA'].astype(str).str.contains(subpartida, case=False, na=False)]
    if agencia:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_DECLARANTE'].astype(str).str.contains(agencia, case=False, na=False)]

    if empresa or descripcion or nit or subpartida or agencia:
        st.write(f"Resultados: {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Escribe en cualquiera de los filtros para buscar.")

except Exception as e:
    st.error(f"Error: {e}")