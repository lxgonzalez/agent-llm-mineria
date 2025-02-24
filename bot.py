import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

import os
load_dotenv()

class ChatBot:
    def __init__(self, system, tools, tool_functions):
        self.system = system
        self.tools = tools
        self.tool_functions = tool_functions
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    async def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        initial_response  = await self.execute()
        
        if initial_response.tool_calls:
            # Guardar mensaje del asistente con tool_calls
            self.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": initial_response.tool_calls
            })
            
             # Procesar tool calls y obtener respuestas
            tool_responses = []
            for tool_call in initial_response.tool_calls:
                if tool_call.function.name == "query_db":
                    # Ejecutar consulta y formatear respuesta
                    result = await self.process_query(tool_call)
                    tool_responses.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id  
                    })
            
            # Agregar respuestas de herramientas al historial
            self.messages.extend(tool_responses)
            
            # Obtener respuesta final con contexto completo
            final_response = await self.execute()
            
            if not final_response.content:
                final_response.content = "\n".join([resp["content"] for resp in tool_responses])
            
            return final_response
        
        return initial_response

    async def process_query(self, tool_call):
        try:
            args = json.loads(tool_call.function.arguments)
            sql = args["sql_query"]
            
            # Validar consulta
            if any(cmd in sql.lower() for cmd in ["insert", "update", "delete"]):
                return "Error: Solo se permiten consultas SELECT"
            
            # Ejecutar y formatear
            result = await self.tool_functions["query_db"](sql)
            
            if "error" in result:
                return f"Error en consulta:\n```sql\n{sql}\n```\n{result['error']}"
                
            return self.format_results(result)
            
        except Exception as e:
            return f"Error crítico: {str(e)}"

    def format_results(self, result):
        columns = result.get("columns", [])
        data = result.get("data", [])
        
        if not data:
            return "No se encontraron resultados"
            
        table_header = "| " + " | ".join(columns) + " |\n"
        table_separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"
        table_rows = "\n".join(["| " + " | ".join(map(str, row.values())) + " |" for row in data[:5]])
        
        return f"**Resultados ({len(data)} filas):**\n\n{table_header}{table_separator}{table_rows}"

    async def execute(self):
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.messages,
            tools=self.tools,
            max_tokens=300,
            top_p=0.9
        )
        print(completion.choices[0].message)
        return completion.choices[0].message
