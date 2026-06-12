import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Buscador Comex Colombia", layout="wide")


@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()


@st.cache_data(ttl=3600)
def cargar_datos():
    # Cargamos solo la tabla que existe en Supabase
    res_comex = supabase.table("todo_comex_consolidado").select("*").execute()
    df_comex = pd.DataFrame(res_comex.data)
    return df_comex


st.title("🔎 Buscador Comex — Modo Validación")

try:
    df_final = cargar_datos()

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        buscar_empresa = st.text_input("Filtrar por Empresa:")
    with col2:
        buscar_texto = st.text_input("Buscar por Subpartida o Palabra:")

    df_filtrado = df_final.copy()

    # Filtro de Empresa
    if buscar_empresa:
        df_filtrado = df_filtrado[
            df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False, na=False)]

    # Filtro de Subpartida (usando la columna existente)
    if buscar_texto:
        df_filtrado = df_filtrado[
            df_filtrado['SUBPARTIDA'].astype(str).str.contains(buscar_texto, case=False, na=False)]

    st.write(f"Resultados encontrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar la aplicación: {e}")