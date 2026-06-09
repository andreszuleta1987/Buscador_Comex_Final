import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import re

# 1. CONFIGURACIÓN DE LA PÁGINA WEB
st.set_page_config(page_title="Data Comex Pro", layout="wide")
st.title("🇨🇴 Inteligencia Comercial: Exportaciones Colombianas")
st.write("Versión 5.6 - Buscador Basado en Columnas Oficiales")

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


# --- SECCIÓN PRINCIPAL: BUSCADOR ---
st.subheader("🔍 Buscador Comercial Inteligente")
opcion_busqueda = st.radio("Selecciona el método de consulta:",
                           ("Buscar por Producto (Texto)", "Buscar por NIT Empresarial"), horizontal=True)

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

                    # Consulta dirigida a la columna 'subpartida'
                    reporte = conn.table(NOMBRE_TABLA).select("*").eq("subpartida", subpartida_seleccionada).execute()

                    if reporte.data:
                        df_reporte = pd.DataFrame(reporte.data)
                        df_reporte['producto_mapeado'] = descripcion_seleccionada

                        st.balloons()
                        st.success(f"📊 ¡Reporte Comercial Generado! {len(df_reporte)} operaciones halladas.")
                        st.dataframe(df_reporte, use_container_width=True)
                    else:
                        st.warning(
                            f"La subpartida {subpartida_seleccionada} ({descripcion_seleccionada}) no registra transacciones en el histórico cargado.")
            else:
                st.warning(f"No se encontraron coincidencias arancelarias asociadas al término '{producto_usuario}'.")
        except Exception as e:
            st.error(f"Error en la consulta de productos: {e}")

else:
    nit_usuario = st.text_input("Introduce el NIT empresarial a consultar:", placeholder="Ej: 900549654")

    if nit_usuario:
        st.info("Consultando registros consolidados en la nube...")
        try:
            nit_busqueda = int(float(str(nit_usuario).strip()))
            # Consulta dirigida a la columna 'nit_exportador'
            respuesta = conn.table(NOMBRE_TABLA).select("*").eq("nit_exportador", nit_busqueda).execute()

            if respuesta.data:
                df_res = pd.DataFrame(respuesta.data)

                try:
                    codigos_presentes = df_res['subpartida'].tolist()
                    prod_data = conn.table("productos").select("subpartida, descripcion_producto").in_("subpartida",
                                                                                                       codigos_presentes).execute()
                    if prod_data.data:
                        df_res = pd.merge(df_res, pd.DataFrame(prod_data.data), on='subpartida', how='left')
                except:
                    pass

                st.success(f"📊 ¡Datos encontrados! Se recuperaron {len(df_res)} operaciones aduaneras históricas.")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning(f"No hay registros en la nube para el NIT {nit_busqueda}.")
        except ValueError:
            st.error("Por favor ingresa un número de NIT válido sin puntos, comas ni letras.")
        except Exception as e:
            st.error(f"Error en la consulta por NIT: {e}")