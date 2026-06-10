import os
import pandas as pd

CARPETA_EXCEL = "archivos_excel"
ARCHIVO_SALIDA_CSV = "todo_comex_consolidado.csv"

# Diccionario estricto priorizando las columnas con descripciones de texto de la DIAN
PALABRAS_CLAVE = {
    'FECHA_PROCESO': ['fecha_pr', 'fecha_proceso', 'fech_dec', 'periodo'],
    'SUBPARTIDA': ['subparti', 'subpartida', 'arancel'],
    'NIT_EXPORTADOR': ['nit_expo', 'nit_exportador'],
    'RAZON_SOCIAL_EXPORTADOR': ['razon_social_exportador', 'exportador'],
    'RAZON_SOCIAL_DESTINATARIO': ['razon_social_destinatario', 'razon_social_dest'],
    'PAIS_DESTINO_FINAL': ['pais_dest', 'pais_destino_final'],  # Buscará el texto largo primero
    'MODO_TRANSPORTE': ['modo_transporte', 'modo_tr'],  # Obligado a buscar el texto "Marítimo"/"Aéreo"
    'VALOR_FOB_USD': ['valor_fob_usd', 'valor_fob', 'vlr_fob'],
    'RAZON_SOCIAL_DECLARANTE': ['razon_social_declarante', 'razon_social_decla']
}

COLUMNAS_FINALES_DESEADAS = [
    'FECHA_PROCESO', 'SUBPARTIDA', 'NIT_EXPORTADOR', 'RAZON_SOCIAL_EXPORTADOR',
    'RAZON_SOCIAL_DESTINATARIO', 'PAIS_DESTINO_FINAL', 'MODO_TRANSPORTE',
    'VALOR_FOB_USD', 'RAZON_SOCIAL_DECLARANTE'
]


def encontrar_columna_exacta_o_flexible(columnas_excel, palabras_clave_buscadas):
    columnas_limpias = [str(c).lower().strip() for c in columnas_excel]

    # Intento 1: Buscar coincidencia exacta del nombre completo para evitar confundir códigos con textos
    for palabra in palabras_clave_buscadas:
        if palabra in columnas_limpias:
            i = columnas_limpias.index(palabra)
            return columnas_excel[i]

    # Intento 2: Si no hay exacta, buscar por aproximación (búsqueda flexible)
    for palabra in palabras_clave_buscadas:
        for i, col_limpia in enumerate(columnas_limpias):
            if palabra in col_limpia:
                return columnas_excel[i]
    return None


def consolidar_localmente():
    print("⏳ Iniciando consolidación estricta de columnas de texto...")
    if not os.path.exists(CARPETA_EXCEL):
        print(f"❌ La carpeta '{CARPETA_EXCEL}' no existe.")
        return

    archivos = [f for f in os.listdir(CARPETA_EXCEL) if f.endswith('.xlsx') and not f.startswith('~$')]
    if not archivos:
        print("❌ No hay archivos Excel en la carpeta.")
        return

    lista_dataframes = []
    for archivo in archivos:
        ruta_completa = os.path.join(CARPETA_EXCEL, archivo)
        try:
            df_original = pd.read_excel(ruta_completa)
            df_temporal = pd.DataFrame()

            for col_final, palabras in PALABRAS_CLAVE.items():
                col_encontrada = encontrar_columna_exacta_o_flexible(df_original.columns, palabras)
                if col_encontrada:
                    df_temporal[col_final] = df_original[col_encontrada]
                else:
                    df_temporal[col_final] = ""

            # Limpieza y estandarización de códigos clave
            if 'SUBPARTIDA' in df_temporal.columns:
                df_temporal['SUBPARTIDA'] = df_temporal['SUBPARTIDA'].astype(str).str.split('.').str[0].str.strip()
            if 'NIT_EXPORTADOR' in df_temporal.columns:
                df_temporal['NIT_EXPORTADOR'] = df_temporal['NIT_EXPORTADOR'].astype(str).str.split('.').str[
                    0].str.strip()

            df_temporal = df_temporal[COLUMNAS_FINALES_DESEADAS]
            lista_dataframes.append(df_temporal)
        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
            continue

    if lista_dataframes:
        df_consolidado_total = pd.concat(lista_dataframes, ignore_index=True).dropna(how='all')
        df_consolidado_total.to_csv(ARCHIVO_SALIDA_CSV, index=False, encoding='utf-8-sig')
        print(f"🎉 ¡PROCESO COMPLETADO! Se generó '{ARCHIVO_SALIDA_CSV}' con texto real en Transporte y País.")


if __name__ == "__main__":
    consolidar_localmente()