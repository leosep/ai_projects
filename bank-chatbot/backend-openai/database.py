import pyodbc
from config import DB_CONFIG

def get_db_connection():
    """Establishes a connection to the SQL Server database."""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database connection error: {sqlstate} - {ex}")
        return None

def verify_employee_identity(employee_id_number, employee_code):
    """
    Verifies employee identity against the database.
    (Fictitious table and column names)
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT EmployeeID FROM EmployeeTable WHERE IDNumber = ? AND EmployeeCode = ?"
            cursor.execute(query, (employee_id_number, employee_code))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except pyodbc.Error as ex:
            print(f"SQL query error during verification: {ex}")
            return None
        finally:
            conn.close()
    return None

def get_employee_data(employee_id):
    """
    Retrieves specific employee data from the database.
    (Fictitious table and column names)
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT HireDate, Department FROM EmployeeTable WHERE EmployeeID = ?"
            cursor.execute(query, (employee_id,))
            result = cursor.fetchone()
            if result:
                return {"hire_date": result[0].strftime("%Y-%m-%d"), "department": result[1]}
            else:
                return {}
        except pyodbc.Error as ex:
            print(f"SQL query error during data retrieval: {ex}")
            return {}
        finally:
            conn.close()
    return {}