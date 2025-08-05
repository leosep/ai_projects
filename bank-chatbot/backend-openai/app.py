from flask import Flask, request, jsonify
import openai
import re
from datetime import datetime
from config import OPENAI_API_KEY, COMPANY_NAME, BOT_NAME, PORT
from database import verify_employee_identity, get_employee_data
from data_processor import search_similar_chunks
from utils import user_sessions, log_request

app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

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
        # Fallback to OpenAI if no specific intent is found
        context = search_similar_chunks(q)
        prompt = f"Basado en la siguiente información del manual de empleados de {COMPANY_NAME}:\n\n{context}\n\nPregunta: {q}\n\nRespuesta:"
        try:
            chat_completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            response_text = chat_completion.choices[0].message.content.strip()
            category = "OpenAI - General"
            
            if "no puedo responder" in response_text.lower() or "no tengo información" in response_text.lower():
                response_text = "Lo siento, no tengo suficiente información para responder a esa pregunta. Si necesitas más ayuda, puedo agendar una llamada con un representante."
                category = "OpenAI - Referral"
        except Exception as e:
            print(f"Error con la API de OpenAI: {e}")
            response_text = "Lo siento, no pude obtener una respuesta en este momento. Por favor, intenta de nuevo o agenda una llamada con un representante."
            category = "OpenAI - Error"
        
    log_request(sender_id, q, response_text, category, employee_id)
    return jsonify({"answer": response_text})

if __name__ == "__main__":
    app.run(port=PORT, debug=True)