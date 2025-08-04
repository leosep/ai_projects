import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_ad(prompt_result: str, image_summary: dict):
    desc = f"La imagen fue clasificada como: {prompt_result}.\n"
    for label, score in image_summary.items():
        desc += f"- {label}: {score*100:.2f}%\n"

    prompt = f"""
Un publicista está evaluando una imagen publicitaria.

{desc}

Con base en lo anterior, ¿cómo evalúas la efectividad publicitaria de esta imagen? 
Dame una puntuación del 0 al 100 y una breve recomendación de mejora.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
