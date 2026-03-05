import psycopg2
from config.settings import DATABASE_URL
from langchain_community.tools import tool
from llm.openai_client import generate_response


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@tool

def get_employee_details(employee_id: str) -> str:
    """
    Use this tool when user wants to retrieve employee details
    from the company database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, department, role FROM employees WHERE id = %s",
        (employee_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        name, department, role = result
        return f"Employee Name: {name}, Department: {department}, Role: {role}"

    return "Employee not found"


@tool
def query_company_database(question: str) -> str:
    """
    Use this tool to answer questions about company data stored inn the postgreSQL database.
    The database contains an employees table with columns:
    id, name, department, role.
    """

    schema = """
    Table: employees
    columns:
    id(integer)
    name(text)
    department(text)
    role(text)
    """

    prompt = [
        {
            "role":"system",
        "content": f"""
        You are an expert SQL generator.

        Generate ONLY a valida PostgreSQL SQL query.

        Database Schema:
        {schema}

        Rules:
        - Only generate SELECT queries.
        - Donot modify data.
        - Return only SQL.
        """},
        {
            "role":"user",
                "content": question,
        }
    ]

    response = generate_response(prompt)

    # Convert generator to string
    if hasattr(response, "__iter__") and not isinstance(response, str):
        sql_query = "".join(list(response))
    else:
        sql_query = str(response)

    sql_query = sql_query.strip()

    print("Generated SQL Query:", sql_query)

    if not sql_query.lower().startswith("select"):
        return "Only SELECT queries are allowed."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql_query)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return str(results)

database_tools_list = [get_employee_details, query_company_database]