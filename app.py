import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex", layout="wide")

@st.cache_data
def cargar_datos_locales():
    # Usamos latin-1 para evitar el error de codificación que viste antes
    df_comex = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')
    return df_comex

st.title("🔎 Diagnóstico de Columnas")

try:
    df = cargar_datos_locales()
    st.write("### Nombres exactos de las columnas en tu archivo:")
    st.write(df.columns.tolist())
    st.dataframe(df.head())
except Exception as e:
    st.error(f"Error: {e}")
