import os

# Fictitious company name
COMPANY_NAME = "Aetheria Bank"
BOT_NAME = "Asistente Virtual de Aetheria Bank"

# OpenAI API Key (using environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
PDF_PATH = "docs/manual_empleados_aetheria.pdf"
LOG_FILE = "request_log.json"
PORT = 5000

# SQL Server Database Configuration
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'aetheria-db-server',  # Fictitious server name
    'database': 'Aetheria_Employee_DB',  # Fictitious database name
    'uid': 'ChatBotUser',              # Fictitious user
    'pwd': 'FictionalPassword123'      # Fictitious password
}