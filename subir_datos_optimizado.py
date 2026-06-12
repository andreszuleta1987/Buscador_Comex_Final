import pandas as pd
from supabase import create_client

url = "https://xboomdhllvqfzroppjql.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhib29tZGhsbHZxZnpyb3BwanFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMTY2ODcsImV4cCI6MjA5NjY5MjY4N30.0onDaMrNpnjCjFG9t8VlqO9uIyXzIDbVP7op931K03Q"
supabase = create_client(url, key)

print("Cargando archivos...")
# Cargamos con encoding latin-1 y el separador correcto (punto y coma)
df_comex = pd.read_csv("todo_comex_consolidado.csv", encoding='latin-1')
df_arancel = pd.read_csv("arancel_convertido.csv", encoding='latin-1', sep=';')

# Limpiamos el nombre de la columna basura 'ï»¿FECHA_PROCESO'
df_comex = df_comex.rename(columns={'ï»¿FECHA_PROCESO': 'FECHA_PROCESO'})

# Aseguramos que SUBPARTIDA sea string para el merge
df_comex['SUBPARTIDA'] = df_comex['SUBPARTIDA'].astype(str)
df_arancel['SUBPARTIDA'] = df_arancel['SUBPARTIDA'].astype(str)

# Hacemos el merge
print("Realizando merge...")
df_final = df_comex.merge(df_arancel, on="SUBPARTIDA", how="left")

# Aseguramos que la columna se llame correctamente
df_final = df_final.rename(columns={'DESCRIPCION': 'DESCRIPCION_SUBPARTIDA'})

# Subir por paquetes (5000 registros para ser muy rápidos y seguros)
batch_size = 5000
total_rows = len(df_final)

print(f"Iniciando subida de {total_rows} registros...")

for i in range(0, total_rows, batch_size):
    batch = df_final[i:i + batch_size]

    # 1. Convertimos a diccionario ignorando los NaN (esto los transforma a None automáticamente)
    data_to_insert = batch.where(pd.notnull(batch), None).to_dict(orient="records")

    # 2. Limpieza extra para asegurar que no pase ningún float 'nan' extraño
    for record in data_to_insert:
        for key, value in record.items():
            if isinstance(value, float) and pd.isna(value):
                record[key] = None

    try:
        supabase.table("todo_comex_consolidado").insert(data_to_insert).execute()
        print(f"Progreso: {min(i + batch_size, total_rows)} / {total_rows} registros subidos.")
    except Exception as e:
        print(f"Error en bloque {i}: {e}")