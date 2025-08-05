from flask import Flask, request, jsonify
import re
from datetime import datetime
from config import COMPANY_NAME, BOT_NAME, PORT
from database import verify_employee_identity, get_employee_data
from data_processor import search_similar_chunks
from utils import user_sessions, log_request

# Importaciones para el modelo LLM local
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

# --- Local LLM Configuration and Loading ---
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
device = 0 if torch.cuda.is_available() else -1

llm_tokenizer = None
llm_model = None
text_generator = None

try:
    print(f"Cargando el tokenizador y modelo LLM: {MODEL_NAME}...")
    llm_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    llm_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, 
        torch_dtype=torch.float16 if device != -1 else None,
        low_cpu_mem_usage=True
    )
    if device != -1:
        llm_model.to(f"cuda:{device}")
    
    text_generator = pipeline(
        "text-generation",
        model=llm_model,
        tokenizer=llm_tokenizer,
        device=device,
        max_new_tokens=250,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95
    )
    print(f"Modelo LLM '{MODEL_NAME}' cargado para generación de texto.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el modelo LLM '{MODEL_NAME}'. Detalles: {e}")
    text_generator = None

# --- Flask Routes ---
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    q = data.get("question", "")
    sender_id = data.get("sender", "unknown_sender")

    if not q:
        return jsonify({"answer": "Please ask a question."}), 400

    employee_id = user_sessions.get(sender_id, {}).get('employee_id')
    is_verified = user_sessions.get(sender_id, {}).get('verified', False)
    
    lower_q = q.lower().strip()
    response_text = ""
    category = "General"

    # --- Identity Verification Flow ---
    if not is_verified:
        if ("id number" in lower_q or "employee id" in lower_q) and ("employee code" in lower_q):
            id_match = re.search(r"(?:my id number is|id number|mi número de identificación es|mi id es)\s*(\S+)", lower_q)
            code_match = re.search(r"(?:my employee code is|employee code|mi código de empleado es|mi código es)\s*(\d+)", lower_q)

            if id_match and code_match:
                id_number = id_match.group(1).strip()
                employee_code = code_match.group(1).strip()
                
                verified_id = verify_employee_identity(id_number, employee_code)
                if verified_id:
                    user_sessions[sender_id] = {'employee_id': verified_id, 'verified': True}
                    response_text = f"¡Bienvenido! Su identidad ha sido verificada. ¿En qué puedo asistirte hoy?"
                    category = "Identity Verification Success"
                else:
                    response_text = "Lo siento, no pude verificar su identidad. Por favor, asegúrese de que su número de identificación y su código de empleado sean correctos y vuelva a intentarlo."
                    category = "Identity Verification Failed"
            else:
                response_text = f"Para poder ayudarle, por favor, comparta su número de identificación completo y su código de empleado. Por ejemplo: 'Mi número de identificación es XXXXXXXXXX y mi código de empleado es 12345'."
                category = "Identity Verification Prompt"
        else:
            response_text = f"Hola, soy tu asistente virtual, {BOT_NAME}. Para poder asistirte, primero necesito verificar tu identidad. Por favor, comparte tu número de identificación y tu código de empleado."
            category = "Welcome/Identity Prompt"
        
        log_request(sender_id, q, response_text, category, employee_id)
        return jsonify({"answer": response_text})

    # --- If identity is verified, proceed with other requests ---
    if "hello" in lower_q or "hi" in lower_q:
        response_text = f"Hola, soy tu asistente virtual, {BOT_NAME}. ¿En qué puedo ayudarte hoy?"
        category = "Welcome"
    elif "work letter" in lower_q or "carta de trabajo" in lower_q:
        response_text = "Para solicitar tu carta de trabajo, puedes hacerlo directamente desde el portal de empleados (enlace al portal) siguiendo estos pasos: 1. Inicia sesión con tu usuario y contraseña. 2. Selecciona la opción 'Solicitudes Internas'. 3. Elige 'Carta de Trabajo' y completa la información solicitada."
        category = "Work Letter"
    elif "vacation" in lower_q or "vacaciones" in lower_q:
        if "pay" in lower_q or "pago de vacaciones" in lower_q:
            response_text = "El pago de vacaciones se procesa anualmente basado en tu fecha de contratación. Puedes verificar tus pagos en el portal de empleados > Mis Pagos. Si no aparece, por favor, responde con 'RECLAMO PAGO DE VACACIONES'."
            category = "Vacation - Pay"
        else:
            employee_data = get_employee_data(employee_id)
            hire_date_info = ""
            if employee_data and employee_data.get('hire_date'):
                try:
                    fecha_obj = datetime.strptime(employee_data['hire_date'], "%Y-%m-%d")
                    hire_date_info = f" el {fecha_obj.strftime('%d de %B de %Y')}"
                except ValueError:
                    hire_date_info = f" el {employee_data['hire_date']}"
            
            response_text = f"Tienes derecho a vacaciones{hire_date_info}. Tienes 14 días para disfrutar cada año. Después de 5 años, aumenta a 18 días pagados + 14 días de disfrute. Para solicitar tus vacaciones, puedes hacerlo directamente desde el portal de empleados (enlace al portal) seleccionando 'Solicitud de Vacaciones'."
            category = "Vacation"
    elif "loan" in lower_q or "prestamo" in lower_q:
        response_text = "Para solicitar un préstamo personal, debes ser empleado permanente y tener al menos 6 meses en la institución. Puedes iniciar la solicitud en el portal de empleados > 'Solicitudes Financieras'."
        category = "Loan"
    elif "bono" in lower_q or "bonus" in lower_q:
        response_text = "El bono de rendimiento se calcula anualmente en base a los objetivos del banco y tu desempeño individual. Se distribuye en el segundo trimestre de cada año fiscal."
        category = "Bonus"

    else:
        # Fallback to Local LLM if no specific intent is found
        context = search_similar_chunks(q)
        
        if text_generator:
            try:
                messages = [
                    {"role": "system", "content": f"Eres un asistente virtual útil para los empleados de {COMPANY_NAME}, respondiendo preguntas estrictamente basadas en la información proporcionada del manual. Si la información no está en el manual, sugiere agendar una llamada."},
                    {"role": "user", "content": f"Basado en la siguiente información del manual:\n\nContexto del Manual:\n{context}\n\nPregunta del Empleado: {q}\n\nRespuesta clara y concisa:"}
                ]
                
                prompt_text = llm_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                outputs = text_generator(prompt_text)
                response_full_text = outputs[0]['generated_text']
                response_text = response_full_text.split(prompt_text)[-1].strip()

                if response_text.lower().startswith("response:"):
                    response_text = response_text[len("response:"):].strip()
                
                if len(response_text) < 30 or any(phrase in response_text.lower() for phrase in ["no puedo responder", "no tengo información", "disculpa"]):
                    response_text = "Lo siento, no tengo suficiente información para responder a esa pregunta basada en el manual. Si necesitas más ayuda, puedo agendar una llamada con un representante de Recursos Humanos."
                    category = "LLM Local - Referral"
                else:
                    category = "LLM Local - General"

            except Exception as e:
                print(f"Error al generar respuesta con el modelo LLM local: {e}")
                response_text = "Disculpa, no pude obtener una respuesta en este momento con el modelo local. Por favor, intenta de nuevo o agenda una llamada con un representante."
                category = "LLM Local - Error"
        else:
            response_text = "Lo siento, el modelo de lenguaje para generar respuestas no está disponible en este momento. Por favor, contacte a soporte."
            category = "LLM Local - Unavailable"
        
    log_request(sender_id, q, response_text, category, employee_id)
    return jsonify({"answer": response_text})

if __name__ == "__main__":
    app.run(port=PORT, debug=True)