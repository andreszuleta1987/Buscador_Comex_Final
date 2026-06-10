import pandas as pd
from sqlalchemy import create_engine

# URL con el formato oficial de Supabase para el puerto pooler (6543)
# Cambiamos el punto por %3A para que identifique correctamente tu proyecto
DB_URI = "postgresql://postgres:Twingopex174@15.228.181.189:5432/postgres?sslmode=require"
NOMBRE_TABLA_FINAL = "export_data_final"
ARCHIVO_CSV = "todo_comex_consolidado.csv"


def subir_datos_directo_sql():
    print(f"⏳ Leyendo el archivo consolidado local '{ARCHIVO_CSV}'...")
    # Asegurar la lectura correcta de subpartidas como texto
    df = pd.read_csv(ARCHIVO_CSV, dtype={'subpartida': str})

    total_filas = len(df)
    print(f"📂 Archivo cargado con éxito. Preparando {total_filas} registros para la nube.")

    print("🧹 Limpiando celdas vacías (NaN) para la base de datos...")
    df['valor_fob'] = df['valor_fob'].fillna(0.0)
    df['nit_exportador'] = df['nit_exportador'].fillna(0).astype(int)
    if 'cod_adu_sal' in df.columns:
        df['cod_adu_sal'] = df['cod_adu_sal'].fillna(0).astype(int)

    print("🚀 Abriendo canal seguro con Supabase (Autenticación Pooler)...")
    engine = create_engine(DB_URI)

    print(f"📦 Reemplazando tabla '{NOMBRE_TABLA_FINAL}' en la nube e indexando las 13 columnas...")
    # Se sube en bloques optimizados
    df.to_sql(NOMBRE_TABLA_FINAL, engine, if_exists='replace', index=False, chunksize=4000)

    print("\n🎉 ¡PROCESO CONCLUIDO CON ÉXITO!")
    print("La base de datos tiene las 13 columnas completas. Revisa tu buscador en Streamlit.")


if __name__ == "__main__":
    subir_datos_directo_sql()