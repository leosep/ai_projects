import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_marketing_content(idea: str):
    prompt = f"""
Eres un experto en marketing digital. A partir de la siguiente idea de producto o servicio:

"{idea}"

Genera lo siguiente:
1. Un pitch breve (2-3 líneas).
2. Un correo promocional (formal).
3. Un post para Instagram/Facebook.
4. Un slogan llamativo.
5. Preguntas frecuentes con respuestas (3).

Responde en formato organizado.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
