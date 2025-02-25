from config import DATABASE_SCHEMA

def generate_sql_prompt(question: str) -> str:
    return f"""
    Eres un experto en análisis de datos. Primero verifica si la pregunta está relacionada con el siguiente esquema:

    {DATABASE_SCHEMA}

    Reglas estrictas:
    1. Si la pregunta NO menciona ciudades, cantidades, semanas o meses → Respuesta: 'NOT_RELATED'
    2. Si pregunta sobre recetas, temas no cuantitativos o fuera del contexto de datos → Respuesta: 'NOT_RELATED'
    3. Si es relevante → Generar SQL sin comentarios
    4. Los datos se encuentra siempre en mayúscula
    5. Diseñe consultas postgresql robustas que tengan en cuenta mayúsculas, minúsculas o algunas variaciones porque no conoce los datos completos o la lista de valores enumerables en las columnas
    6. Si se trata de datos de tabla, muéstrelos en formato de tabla markdown.
    7. Si se trata de datos de una sola columna, muestrelos en formato de tabla markdown.

    Pregunta actual: {question}
    Respuesta (SOLO SQL o 'NOT_RELATED'):
    """
