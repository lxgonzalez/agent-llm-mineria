import asyncpg
import os

async def get_postgres_schema():
    """Obtiene el esquema actual de la base de datos"""
    conn = None
    try:
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        
        query = """
        SELECT 
            table_name, 
            column_name, 
            data_type 
        FROM information_schema.columns 
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        and table_name in ('qty_semanal')
        """
        
        result = await conn.fetch(query)
        return format_schema(result)
    
    except Exception as e:
        return f"Error obteniendo esquema: {str(e)}"
    finally:
        if conn: await conn.close()

def format_schema(data):
    """Formatea los datos del esquema para el prompt"""
    schema = {}
    for row in data:
        table = row['table_name']
        if table not in schema:
            schema[table] = []
        schema[table].append(f"{row['column_name']} ({row['data_type']})")
    
    schema_str = "\n\n".join(
        [f"**Tabla: {table}**\n" + "\n".join([f"- {col}" for col in cols]) 
         for table, cols in schema.items()]
    )
    
    return f"Esquema de la base de datos:\n\n{schema_str}"