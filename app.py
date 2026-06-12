import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Buscador Comex", layout="wide")


@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


supabase = init_supabase()


@st.cache_data(ttl=3600)
def cargar_datos():
    # Cargamos SOLAMENTE la tabla principal que sí existe
    res_comex = supabase.table("todo_comex_consolidado").select("*").execute()
    df_comex = pd.DataFrame(res_comex.data)
    return df_comex


st.title("🔎 Buscador Comex — Modo Validación")

try:
    df_comex = cargar_datos()

    # Filtro sencillo
    buscar_empresa = st.text_input("Filtrar por Empresa:")

    df_filtrado = df_comex.copy()

    if buscar_empresa:
        # Filtro básico
        mask = df_filtrado['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False, na=False)
        df_filtrado = df_filtrado[mask]

    st.write(f"Resultados encontrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")