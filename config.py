import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATABASE_SCHEMA = """
Tablas disponibles:
1. qty_semanal
   - ciudad varchar(20)
   - month Integer
   - cantidad Integer
   - year Integer
   - numero_semana Integer
"""
