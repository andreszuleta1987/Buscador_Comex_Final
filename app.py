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
    # Carga básica
    res_comex = supabase.table("todo_comex_consolidado").select("*").execute()
    res_arancel = supabase.table("arancel_convertido").select("*").execute()

    df_comex = pd.DataFrame(res_comex.data)
    df_arancel = pd.DataFrame(res_arancel.data)

    # Merge directo (asumiendo que las columnas se llaman igual)
    df_final = pd.merge(df_comex, df_arancel, on='SUBPARTIDA', how='left')
    return df_final


st.title("🔎 Buscador Comex — Modo Validación")

try:
    df_final = cargar_datos()

    # Filtro básico y sencillo
    buscar_empresa = st.text_input("Filtrar por Empresa:")

    df_filtrado = df_final.copy()

    if buscar_empresa:
        # Filtro simple: convierte a string y busca, ignorando mayúsculas
        df_filtrado = df_final[df_final['RAZON_SOCIAL_EXPORTADOR'].astype(str).str.contains(buscar_empresa, case=False)]

    st.write(f"Resultados encontrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")