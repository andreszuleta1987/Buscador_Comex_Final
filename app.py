import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnóstico", layout="wide")

st.title("🔎 Diagnóstico de Archivos")

try:
    # 1. Cargar principales
    df = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')
    st.write("### Columnas en 'todo_comex_consolidado':")
    st.write(df.columns.tolist())

    # 2. Cargar arancel
    arancel = pd.read_csv("arancel_convertido.csv", encoding='latin-1')
    st.write("### Columnas en 'arancel_convertido':")
    st.write(arancel.columns.tolist())

except Exception as e:
    st.error(f"Error al leer archivos: {e}")
