from fastapi import FastAPI, HTTPException
from models import QueryRequest
from prompts import generate_sql_prompt
from db import execute_query
from openai_utils import client, generate_natural_response

app = FastAPI()

@app.post("/analyze")
async def analyze_data(request: QueryRequest):
    try:
        sql_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "user", "content": generate_sql_prompt(request.question)}],
            temperature=0
        )
        generated_sql = sql_response.choices[0].message.content.strip()
        
        # Detectar preguntas no relacionadas
        if "NOT_RELATED" in generated_sql:
            return {
                "query": request.question,
                "analysis": ("Lamentablemente, los datos proporcionados no contienen información sobre ese tema. "
                             "Solo puedo responder preguntas relacionadas con: ciudades, cantidades, semanas y meses."),
                "data_insights": []
            }
            
        # Validar SQL
        if not generated_sql.lower().startswith("select"):
            raise HTTPException(400, "Solo se permiten consultas SELECT")

        query_result = await execute_query(generated_sql)
        
        if query_result["error"]:
            raise HTTPException(400, f"Error en SQL: {query_result['error']}")

        analysis = generate_natural_response(request.question, query_result["data"])
        
        return {
            "query": request.question,
            "sql": generated_sql,
            "analysis": analysis,
            "data_insights": query_result["data"][:5]
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
