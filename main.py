from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Importa CORSMiddleware
from pydantic import BaseModel
from bot import ChatBot
from tools import tools_schema, run_postgres_query
from utils import get_postgres_schema
import os

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost:3000", 
    "http://sipforecast.s3-website-us-east-1.amazonaws.com",  
    "*", 
]

# Añadir CORSMiddleware al app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class MessageRequest(BaseModel):
    message: str
    session_id: str

sessions = {}

# Función centralizada para crear bot
async def create_chatbot() -> ChatBot:
    """Crea un nuevo ChatBot con el esquema actual de la base de datos"""
    try:
        # Obtener esquema en tiempo real
        schema_info = await get_postgres_schema()
        
        system_prompt = f"""Eres un experto en análisis de datos. Proporcionará información valiosa a los usuarios empresariales en función de su solicitud.
    Antes de responder, se asegurará de que la solicitud del usuario se refiera al análisis de datos en el esquema proporcionado; de lo contrario, la rechazará.
    Si el usuario solicita algunos datos, creará una consulta sql basada en la solicitud del usuario para postgres a partir de los detalles del esquema/tabla proporcionados y llamará a las herramientas query_db para obtener datos de la base de datos con la consulta correcta/relevante que proporcione el resultado correcto.
    Usted tiene acceso a la herramienta para ejecutar la consulta de base de datos y obtener resultados y para trazar los resultados de la consulta.
    Una vez que haya proporcionado los datos, reflexionará para ver si ha proporcionado los datos correctos o no, ya que no conoce los datos de antemano, sino sólo el esquema, por lo que podría descubrir nuevas perspectivas durante la reflexión.

    Siga estas directrices
    - Es muy importante que si usted necesita ciertos datos para proceder o no está seguro de algo, puede hacer preguntas, pero trate de usar su inteligencia para entender la intención del usuario y también dejar que el usuario sepa si usted hace suposiciones.
    - En el mensaje de respuesta no proporcione detalles técnicos como sql, tabla o detalles de la columna, la respuesta será leída por el usuario de negocios no persona técnica.
    - Si se trata de datos de tabla, muéstrelos en formato de tabla markdown.
    - En caso de que se produzca un error en la base de datos, se reflejará e intentará llamar a la consulta sql correcta
    - Limite el número de columnas a 5-8 Elija sabiamente las principales columnas a consultar en las consultas SQL en función de la petición del usuario
    - en las consultas postgresql para obtener datos, debe convertir las columnas de fecha y numéricas a un formato legible (fácil de leer en formato de cadena)
    - Diseñe consultas postgresql robustas que tengan en cuenta mayúsculas, minúsculas o algunas variaciones porque no conoce los datos completos o la lista de valores enumerables en las columnas.
    - Presta mucha atención al esquema y a los detalles de las tablas que he proporcionado a continuación. Utilice únicamente las columnas y tablas mencionadas en los detalles del esquema.
    - El areacity se encuentra siempre en mayúscula
    Aquí están los detalles completos del esquema con los detalles de las columnas:
    {schema_info}"""
        
        print(system_prompt)
        return ChatBot(
            system=system_prompt,
            tools=tools_schema,
            tool_functions={"query_db": run_postgres_query}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inicializando bot: {str(e)}"
        )

@app.post("/chat")
async def chat_endpoint(request: MessageRequest):
    try:
        if request.session_id not in sessions:
            sessions[request.session_id] = {"bot": await create_chatbot()}
        
        bot = sessions[request.session_id]["bot"]
        response = await bot(request.message)
        
        # Manejar respuestas vacías
        final_text = response.content or "Respuesta no disponible"
        
        return JSONResponse({
            "text": final_text,
            "session_id": request.session_id
        })
    
    except Exception as e:
        error_detail = f"Error en chat: {str(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
