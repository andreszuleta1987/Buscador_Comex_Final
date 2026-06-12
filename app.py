import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex", layout="wide")


# Cargamos el archivo que ya tiene todo unido (más rápido y sin errores)
@st.cache_data
def cargar_datos():
    # Usamos on_bad_lines='skip' para que ignore filas con errores
    # Usamos engine='python' para que sea más tolerante a formatos de Excel
    df = pd.read_csv("datos_finales.csv", encoding='latin-1', on_bad_lines='skip', engine='python')
    return df


st.title("🔎 Buscador Comex")

try:
    df = cargar_datos()

    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Filtrar por Empresa (Exportador):")
    with col2:
        producto = st.text_input("Buscar por Nombre de producto:")

    with st.expander("⚙️ Filtros Avanzados"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nit = st.text_input("NIT Exportador:")
        with c2:
            subpartida = st.text_input("Subpartida numérica:")
        with c3:
            agencia = st.text_input("Agencia de Aduanas:")

    df_filtrado = df.copy()

    # Filtros
    if empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(empresa, case=False, na=False)]
    if producto:
        df_filtrado = df_filtrado[
            df_filtrado['DESCRIPCION_SUBPARTIDA'].astype(str).str.contains(producto, case=False, na=False)]
    if nit:
        df_filtrado = df_filtrado[df_filtrado['NIT_EXPORTADOR'].astype(str).str.contains(nit, case=False, na=False)]
    if subpartida:
        df_filtrado = df_filtrado[df_filtrado['SUBPARTIDA'].astype(str).str.contains(subpartida, case=False, na=False)]
    if agencia:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_DECLARANTE'].astype(str).str.contains(agencia, case=False, na=False)]

    if empresa or producto or nit or subpartida or agencia:
        st.write(f"Resultados encontrados: {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Escribe en cualquiera de los filtros para comenzar la búsqueda.")

except Exception as e:
    st.error(f"Error cargando los datos: {e}")
