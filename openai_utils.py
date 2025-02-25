from openai import OpenAI
from config import OPENAI_API_KEY

# Configura el cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_natural_response(question: str, data: list) -> str:
    # Nueva condición para preguntas no relacionadas
    if isinstance(data, str) and data.startswith("NOT_RELATED"):
        return ("Lamentablemente, los datos proporcionados no contienen información sobre ese tema. "
                "Solo puedo responder preguntas relacionadas con: ciudades, cantidades, semanas y meses.")
    
    prompt = f"""
    Actúa como un analista de datos senior. Transforma estos datos en una respuesta profesional en español:

    Pregunta: {question}
    Resultados: {data}

    Instrucciones:
    1. Usa formato claro con viñetas
    2. Todas las unidades son en cantidad
    3. Si hay fechas, menciónalas claramente de lo contrario no las incluya
    4. Si no hay datos, ofrece una alternativa
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "Eres un asistente analítico experto en explicar datos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"
