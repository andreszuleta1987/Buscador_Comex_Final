import streamlit as st
import pandas as pd
from supabase import create_client

# Configuración de Streamlit
st.set_page_config(page_title="Buscador Comex Web", layout="wide")

# Conexión a Supabase usando los secretos guardados en Streamlit Cloud
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🔎 Buscador Comex Web")

# Filtros principales
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Filtrar por Empresa (Exportador):")
with col2:
    descripcion = st.text_input("Buscar por Nombre de producto:")

# Filtros avanzados
with st.expander("⚙️ Filtros Avanzados"):
    c1, c2, c3 = st.columns(3)
    with c1:
        nit = st.text_input("NIT Exportador:")
    with c2:
        subpartida = st.text_input("Subpartida numérica:")
    with c3:
        agencia = st.text_input("Agencia de Aduanas:")

# Lógica de búsqueda mejorada para evitar timeout
if empresa or descripcion or nit or subpartida or agencia:
    try:
        # Iniciar la consulta
        query = supabase.table("todo_comex_consolidado").select("*")

        # Aplicar filtros
        if empresa: query = query.ilike("RAZON_SOCIAL_EXPORTADOR", f"%{empresa}%")
        if descripcion: query = query.ilike("DESCRIPCION_SUBPARTIDA", f"%{descripcion}%")
        if nit: query = query.ilike("NIT_EXPORTADOR", f"%{nit}%")
        if subpartida: query = query.ilike("SUBPARTIDA", f"%{subpartida}%")
        if agencia: query = query.ilike("RAZON_SOCIAL_DECLARANTE", f"%{agencia}%")

        # IMPORTANTE: Limitamos a 500 registros para que Supabase responda rápido
        # y no cancele la consulta por tiempo agotado.
        response = query.limit(500).execute()
        data = response.data

        if data:
            df = pd.DataFrame(data)
            st.write(f"Resultados encontrados (mostrando hasta 500): {len(df)}")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No se encontraron resultados.")

    except Exception as e:
        st.error(f"Error de consulta: {e}")