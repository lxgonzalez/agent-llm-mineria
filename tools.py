import os
import asyncpg
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "query_db",
            "description": "Fetch data from postgres database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "complete and correct sql query to fulfil user request.",
                    }
                },
                "required": ["sql_query"],
            },
        }
    }
]


async def run_postgres_query(sql_query: str):
    try:
        # Intentar establecer la conexión
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        
        # Si la conexión es exitosa, imprime un mensaje
        print("Conexión a la base de datos PostgreSQL exitosa!")

        # Ejecutar la consulta
        result = await conn.fetch(sql_query)
        
        # Imprimir el resultado de la consulta
        print(f"Consulta ejecutada: {sql_query}")
        print(f"Resultados: {result}")

        # Retornar los datos
        return {
            "columns": list(result[0].keys()) if result else [],
            "data": [dict(row) for row in result]
        }

    except Exception as e:
        # Si hay un error en la conexión o ejecución, imprimirlo
        print(f"Error en la conexión o ejecución de la consulta: {str(e)}")
        return {"error": str(e)}

    finally:
        # Asegurarse de cerrar la conexión
        await conn.close()
        print("Conexión cerrada.")
