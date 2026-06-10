import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador Comex Local", layout="wide")


@st.cache_data
def cargar_datos_base():
    # Lee el nuevo CSV consolidado con textos reales
    df = pd.read_csv("todo_comex_consolidado.csv", dtype={'SUBPARTIDA': str, 'NIT_EXPORTADOR': str})
    df['RAZON_SOCIAL_DECLARANTE'] = df['RAZON_SOCIAL_DECLARANTE'].fillna("")
    df['RAZON_SOCIAL_EXPORTADOR'] = df['RAZON_SOCIAL_EXPORTADOR'].fillna("")
    df['PAIS_DESTINO_FINAL'] = df['PAIS_DESTINO_FINAL'].fillna("")
    df['MODO_TRANSPORTE'] = df['MODO_TRANSPORTE'].fillna("")
    df['SUBPARTIDA'] = df['SUBPARTIDA'].astype(str).str.strip()
    return df


@st.cache_data
def cargar_maestro_arancel():
    try:
        df_m = pd.read_excel("arancel_convertido.xlsx", header=None, usecols=[0, 1])
        df_m.columns = ['SUBPARTIDA', 'DESCRIPCION_SUBPARTIDA']
        df_m['SUBPARTIDA'] = df_m['SUBPARTIDA'].astype(str).str.split('.').str[0].str.strip()
        df_m['DESCRIPCION_SUBPARTIDA'] = df_m['DESCRIPCION_SUBPARTIDA'].fillna("").astype(str)
        return df_m
    except Exception as e:
        st.error(f"Error al cargar arancel_convertido.xlsx: {e}")
        return pd.DataFrame(columns=['SUBPARTIDA', 'DESCRIPCION_SUBPARTIDA'])


st.title("🔎 Buscador Comex — Modo Validación Local")

try:
    df_comex = cargar_datos_base()
    df_arancel = cargar_maestro_arancel()

    st.success(f"✅ ¡Base de datos local conectada! Registros: {len(df_comex):,}")

    # --- LOS DOS FILTROS INTELIGENTES ---
    st.markdown("### Filtros de Búsqueda")
    col1, col2 = st.columns(2)

    with col1:
        buscar_empresa = st.text_input("Filtrar por Empresa / Agencia de Aduanas:")
    with col2:
        buscar_subpartida_o_texto = st.text_input("Filtrar por Subpartida Arancelaria o Palabra (ej: hass, aguacate):")

    df_filtrado = df_comex.copy()

    # 1. Filtro por Empresa / Agencia
    if buscar_empresa:
        condicion_agencia = df_filtrado['RAZON_SOCIAL_DECLARANTE'].str.contains(buscar_empresa, case=False, na=False)
        condicion_exportador = df_filtrado['RAZON_SOCIAL_EXPORTADOR'].str.contains(buscar_empresa, case=False, na=False)
        df_filtrado = df_filtrado[condicion_agencia | condicion_exportador]

    # 2. Filtro por Subpartida / Texto
    if buscar_subpartida_o_texto:
        if buscar_subpartida_o_texto.isdigit():
            df_filtrado = df_filtrado[df_filtrado['SUBPARTIDA'].str.startswith(buscar_subpartida_o_texto)]
        else:
            codigos_coincidentes = df_arancel[
                df_arancel['DESCRIPCION_SUBPARTIDA'].str.contains(buscar_subpartida_o_texto, case=False, na=False)][
                'SUBPARTIDA'].unique()
            df_filtrado = df_filtrado[df_filtrado['SUBPARTIDA'].isin(codigos_coincidentes)]

    # Inyección de la descripción arancelaria en caliente
    df_filtrado = pd.merge(df_filtrado, df_arancel, on='SUBPARTIDA', how='left')
    df_filtrado['DESCRIPCION_SUBPARTIDA'] = df_filtrado['DESCRIPCION_SUBPARTIDA'].fillna("SIN DESCRIPCION")

    # ORDEN EXACTO SOLICITADO POR EL USUARIO
    COLUMNAS_ORDENADAS_VISIBLES = [
        'FECHA_PROCESO',
        'SUBPARTIDA',
        'DESCRIPCION_SUBPARTIDA',  # Tercera posición
        'NIT_EXPORTADOR',
        'RAZON_SOCIAL_EXPORTADOR',
        'RAZON_SOCIAL_DESTINATARIO',
        'PAIS_DESTINO_FINAL',
        'MODO_TRANSPORTE',
        'VALOR_FOB_USD',
        'RAZON_SOCIAL_DECLARANTE'
    ]

    columnas_validas = [col for col in COLUMNAS_ORDENADAS_VISIBLES if col in df_filtrado.columns]
    df_vista_final = df_filtrado[columnas_validas]

    st.markdown(f"📊 **Resultados encontrados: {len(df_vista_final):,}**")
    st.dataframe(df_vista_final.head(50), use_container_width=True)

except FileNotFoundError:
    st.error("❌ Archivos base no encontrados.")