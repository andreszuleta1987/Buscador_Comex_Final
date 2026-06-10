import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import re

# 1. CONFIGURACIÓN DE LA PÁGINA WEB
st.set_page_config(page_title="Data Comex Pro", layout="wide")
st.title("🇨🇴 Inteligencia Comercial: Exportaciones Colombianas")
st.write("Versión 5.8 - Buscador Basado en Columnas Oficiales")

# Credenciales de Conexión
SUPABASE_URL = "https://pkcfoxntuegjvbhivoid.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrY2ZveG50dWVnanZiaGl2b2lkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAwNjUyNjEsImV4cCI6MjA5NTY0MTI2MX0.bgodRksfujcJtt2rxQ-LITkDqBPf2c6fX2M9YEC4_cc"
NOMBRE_TABLA = "export_data_final"

conn = st.connection("supabase", type=SupabaseConnection, url=SUPABASE_URL, key=SUPABASE_KEY)


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    texto = re.sub(r'[áàäâ]', 'a', texto)
    texto = re.sub(r'[éèëê]', 'e', texto)
    texto = re.sub(r'[íìïî]', 'i', texto)
    texto = re.sub(r'[óòöô]', 'o', texto)
    texto = re.sub(r'[úùüû]', 'u', texto)
    return texto


# Mapeo de columnas corregido a minúsculas según la base de datos real
COLUMNAS_VISUALES = {
    "fecha_proceso": "Fecha Proceso",
    "nit_exportador": "NIT Exportador",
    "razon_social_exportador": "Cliente Exportador",
    "razon_social_destinatario": "Destinatario Internacional",
    "pais_destino_final": "País Destino",
    "modo_transporte": "Modo Transporte",
    "valor_fob_usd": "Valor FOB (USD)",
    "subpartida": "Subpartida Arancelaria",
    "cod_lug_salida": "Puerto / Lugar Salida",
    "razon_social_declarante": "Agencia de Aduanas",
    "producto_mapeado": "Producto Mapeado"
}


def formatear_y_mostrar_tabla(datos, desc_producto=None):
    """Función auxiliar para limpiar, ordenar y mostrar las columnas A-J"""
    df = pd.DataFrame(datos)

    # Si viene la descripción del producto, la agregamos
    if desc_producto:
        df['producto_mapeado'] = desc_producto

    # Filtrar solo las columnas que existan en el diccionario de mapeo
    columnas_existentes = [col for col in COLUMNAS_VISUALES.keys() if col in df.columns]
    df_filtrado = df[columnas_existentes].copy()

    # Renombrar columnas para la vista del usuario
    df_filtrado = df_filtrado.rename(columns=COLUMNAS_VISUALES)

    st.balloons()
    st.success(f"📊 ¡Reporte Comercial Generado! {len(df_filtrado)} operaciones halladas.")
    st.dataframe(df_filtrado, use_container_width=True)


# --- SECCIÓN PRINCIPAL: BUSCADOR ---
st.subheader("🔍 Buscador Comercial Inteligente")
opcion_busqueda = st.radio("Selecciona el método de consulta:",
                           ("Buscar por Producto (Texto)", "Buscar por NIT Empresarial",
                            "Buscar por Agencia de Aduanas"), horizontal=True)

# 1. BÚSQUEDA POR PRODUCTO
if opcion_busqueda == "Buscar por Producto (Texto)":
    producto_usuario = st.text_input("Escribe el nombre del producto o variedad a buscar:",
                                     placeholder="Ej: hass, cocos, banano")

    if producto_usuario:
        st.info("Analizando coincidencias en el universo arancelario...")
        try:
            termino_limpio = normalizar_texto(producto_usuario)
            termino_sql = f"%{termino_limpio}%"

            coincidencias = conn.table("productos").select("subpartida, descripcion_producto").ilike(
                "busqueda_normalizada", termino_sql).execute()

            if coincidencias.data:
                df_coincidencias = pd.DataFrame(coincidencias.data)
                df_coincidencias['opcion_visual'] = df_coincidencias['subpartida'] + " - " + df_coincidencias[
                    'descripcion_producto']

                st.success(f"🔍 Se encontraron {len(df_coincidencias)} posibles productos relacionados.")

                seleccion = st.selectbox("Selecciona el producto específico que deseas consultar:",
                                         options=df_coincidencias['opcion_visual'].tolist())

                if seleccion:
                    subpartida_seleccionada = seleccion.split(" - ")[0]
                    descripcion_seleccionada = seleccion.split(" - ")[1]

                    # CONSULTA CORREGIDA A MINÚSCULAS: "subpartida"
                    reporte = conn.table(NOMBRE_TABLA).select("*").eq("subpartida", subpartida_seleccionada).execute()

                    if reporte.data:
                        formatear_y_mostrar_tabla(reporte.data, descripcion_seleccionada)
                    else:
                        st.warning(
                            f"La subpartida {subpartida_seleccionada} ({descripcion_seleccionada}) no registra transacciones en el histórico cargado.")
            else:
                st.warning(f"No se encontraron coincidencias arancelarias asociadas al término '{producto_usuario}'.")
        except Exception as e:
            st.error(f"Error en la consulta de productos: {e}")

# 2. BÚSQUEDA POR NIT
elif opcion_busqueda == "Buscar por NIT Empresarial":
    nit_usuario = st.text_input("Introduce el NIT empresarial a consultar:", placeholder="Ej: 900549654")

    if nit_usuario:
        st.info("Consultando registros consolidados en la nube...")
        try:
            nit_busqueda = int(float(str(nit_usuario).strip()))
            # CONSULTA CORREGIDA A MINÚSCULAS: "nit_exportador"
            respuesta = conn.table(NOMBRE_TABLA).select("*").eq("nit_exportador", nit_busqueda).execute()

            if respuesta.data:
                formatear_y_mostrar_tabla(respuesta.data)
            else:
                st.warning(f"No hay registros en la nube para el NIT {nit_busqueda}.")
        except ValueError:
            st.error("Por favor ingresa un número de NIT válido sin puntos, comas ni letras.")
        except Exception as e:
            st.error(f"Error en la consulta por NIT: {e}")

# 3. BÚSQUEDA POR AGENCIA DE ADUANAS
else:
    agencia_usuario = st.text_input("Escribe el nombre de la Agencia de Aduanas a buscar:",
                                    placeholder="Ej: Fedegal, Elite, Agencome")

    if agencia_usuario:
        st.info("Rastreando operaciones asociadas a la agencia...")
        try:
            termino_agencia = f"%{agencia_usuario.lower().strip()}%"
            # CONSULTA CORREGIDA A MINÚSCULAS: "razon_social_declarante"
            respuesta_agencia = conn.table(NOMBRE_TABLA).select("*").ilike("razon_social_declarante",
                                                                           termino_agencia).execute()

            if respuesta_agencia.data:
                formatear_y_mostrar_tabla(respuesta_agencia.data)
            else:
                st.warning(
                    f"No se encontraron operaciones registradas para la agencia o declarante '{agencia_usuario}'.")
        except Exception as e:
            st.error(f"Error en la consulta por Agencia de Aduanas: {e}")