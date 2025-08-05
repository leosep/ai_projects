import os
import json
from datetime import datetime
from config import LOG_FILE

user_sessions = {} # For session management (simple dictionary for demo)

def log_request(sender_id, question, answer, category="General", employee_id=None):
    """Logs each request to a JSON file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "sender_id": sender_id,
        "employee_id": employee_id,
        "question": question,
        "answer": answer,
        "category": category
    }

    try:
        data = []
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, 'r+') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Log file '{LOG_FILE}' is empty or corrupt. Initializing with new content.")
                    data = []
        
        if not isinstance(data, list):
            data = []

        data.append(log_entry)
        
        with open(LOG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error logging request: {e}")

def get_request_history(sender_id):
    """Retrieves the request history for a specific sender."""
    history = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
                history = [entry for entry in data if entry["sender_id"] == sender_id]
    except Exception as e:
        print(f"Error reading log file for history: {e}")
    return history

def count_requests_by_category():
    """Counts requests by category."""
    category_counts = {}
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
                for entry in data:
                    category = entry.get("category", "Uncategorized")
                    category_counts[category] = category_counts.get(category, 0) + 1
    except Exception as e:
        print(f"Error counting requests by category: {e}")
    return category_counts