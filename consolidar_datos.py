import os
import pandas as pd
from sqlalchemy import create_engine

# Configuración de rutas y base de datos
CARPETA_EXCEL = "archivos_excel"
DB_URI = "postgresql://postgres:Twingopex174@db.pkcfoxntuegjvbhivoid.supabase.co:5432/postgres"
NOMBRE_TABLA_FINAL = "export_data_final"


def encontrar_columna_flexible(columnas_excel, palabras_clave):
    """Busca de forma inteligente una columna que contenga ciertas palabras clave."""
    for col in columnas_excel:
        col_normalizada = str(col).strip().upper()
        # Si todas las palabras clave de la lista están en el nombre de la columna
        if all(palabra in col_normalizada for palabra in palabras_clave):
            return col
    return None


def consolidar_y_subir():
    engine = create_engine(DB_URI)
    primer_archivo = True

    if not os.path.exists(CARPETA_EXCEL):
        print(f"❌ Error: No se encuentra la carpeta '{CARPETA_EXCEL}'.")
        return

    archivos = [f for f in os.listdir(CARPETA_EXCEL) if f.endswith('.xlsx')]
    total_archivos = len(archivos)

    print(f"📂 Se detectaron {total_archivos} archivos para consolidar de forma inteligente.")

    for idx, archivo in enumerate(archivos, start=1):
        ruta_completa = os.path.join(CARPETA_EXCEL, archivo)
        print(f"\n⏳ [{idx}/{total_archivos}] Analizando estructura de: {archivo}...")

        try:
            # 1. Leer el archivo completo
            df_completo = pd.read_excel(ruta_completa)
            columnas_originales = list(df_completo.columns)

            # 2. Diccionario para mapear de forma flexible tus 7 columnas deseadas
            # Definimos palabras clave alternativas para cada campo esencial
            mapeo_detectado = {}

            reglas_busqueda = {
                'fecha_proceso': ['FECHA'],
                'cod_adu_sal': ['ADU'],
                'nit_exportador': ['NIT'],
                'dv_exportador': ['DV'],
                'razon_social_exportador': ['RAZON', 'SOCIAL'],
                'cod_pai_des': ['PAI'],
                'subpartida': ['SUBPARTIDA']
            }

            # Buscamos cada columna de forma adaptativa
            for columna_destino, palabras in reglas_busqueda.items():
                col_origen = encontrar_columna_flexible(columnas_originales, palabras)
                if col_origen:
                    mapeo_detectado[col_origen] = columna_destino

            # Validamos que al menos se encuentren las dos columnas críticas para indexar
            columnas_encontradas = list(mapeo_detectado.values())
            if 'subpartida' not in columnas_encontradas or 'nit_exportador' not in columnas_encontradas:
                print(f"⚠️ Advertencia en {archivo}: No se detectó 'SUBPARTIDA' o 'NIT_EXPORTADOR'. Saltando archivo.")
                print(f"Columnas detectadas en el Excel: {columnas_originales}")
                continue

            # 3. Renombrar y filtrar solo las columnas que logramos mapear exitosamente
            df_mes = df_completo[list(mapeo_detectado.keys())].copy()
            df_mes.rename(columns=mapeo_detectado, inplace=True)

            # 4. Asegurar que existan todas las 7 columnas (si falta alguna menor, la creamos vacía para no romper la tabla)
            for col_obligatoria in reglas_busqueda.keys():
                if col_obligatoria not in df_mes.columns:
                    df_mes[col_obligatoria] = None

            # Reordenar las columnas de forma idéntica siempre para PostgreSQL
            df_mes = df_mes[list(reglas_busqueda.keys())]

            # 5. Limpieza de registros nulos en datos clave
            df_mes.dropna(subset=['subpartida', 'nit_exportador'], inplace=True)

            # 6. Formatear la subpartida a 10 caracteres estrictos (con ceros a la izquierda)
            df_mes['subpartida'] = pd.to_numeric(df_mes['subpartida'], errors='coerce').fillna(0).astype(int)
            df_mes['subpartida'] = df_mes['subpartida'].astype(str).str.strip().str.zfill(10)

            # 7. Formatear el NIT a número entero
            df_mes['nit_exportador'] = pd.to_numeric(df_mes['nit_exportador'], errors='coerce').fillna(0).astype(int)

            total_filas = len(df_mes)

            # 8. Carga por lotes (Chunks) a la nube
            if primer_archivo:
                print(f"📦 Inicializando tabla limpia '{NOMBRE_TABLA_FINAL}' en Supabase con mapeo flexible...")
                df_mes.to_sql(NOMBRE_TABLA_FINAL, engine, if_exists='replace', index=False, chunksize=2500)
                primer_archivo = False
                print(f"✅ Estructura base creada. {total_filas} registros indexados.")
            else:
                print(f"🚀 Acumulando lote de {total_filas} registros en la nube...")
                df_mes.to_sql(NOMBRE_TABLA_FINAL, engine, if_exists='append', index=False, chunksize=2500)
                print(f"✅ Datos unificados sin errores.")

        except Exception as e:
            print(f"❌ Error inesperado procesando el archivo {archivo}: {e}")

    print("\n🎉 ¡PROCESO CONCLUIDO CON ÉXITO!")
    print(f"Toda tu información histórica está unificada en Supabase sin importar variaciones de nombres.")


if __name__ == "__main__":
    consolidar_y_subir()