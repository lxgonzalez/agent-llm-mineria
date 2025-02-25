import asyncpg
from typing import Dict, Any
from config import DATABASE_URL

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

async def execute_query(sql: str) -> Dict[str, Any]:
    conn = None
    try:
        conn = await get_db_connection()
        result = await conn.fetch(sql)
        return {"data": [dict(record) for record in result], "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
    finally:
        if conn:
            await conn.close()
