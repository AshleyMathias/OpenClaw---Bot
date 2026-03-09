import os
import psycopg2
# Set matplotlib to use non-interactive backend before importing pyplot
import matplotlib
from sqlalchemy.engine import cursor
matplotlib.use('Agg')  # Use non-interactive backend for web server
import matplotlib.pyplot as plt
from config.settings import DATABASE_URL
from langchain_community.tools import tool
from llm.openai_client import generate_response


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn



@tool
def generate_chart(question: str) -> str:
    """
    Generate charts based on the user's analytics question.
    Supports bar chart, pie chart, line chart, and histogram.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Ask AI what chart to generate
    prompt = [
        {
            "role":"system",
            "content":"""
            You are a data visualization planner.

            Return ONLY one of these chart types:
            bar chart
            pie chart
            line chart
            histogram
            """
        },
        {
            "role":"user",
            "content": question,
        }
    ]   

    chart_type = "".join(generate_response(prompt))

    chart_type = chart_type.strip().lower()

    if chart_type not in ["pie chart", "bar chart", "line chart", "histogram"]:
        return "Unsupported chart type. Please ask for a pie chart, bar chart, line chart, or histogram."

    cursor.execute(
        "SELECT department, COUNT(*) FROM employees GROUP BY department"
    )

    result = cursor.fetchall()

    departments = [row[0] for row in result]
    counts = [row[1] for row in result]

    os.makedirs("charts", exist_ok=True)

    chart_path = f"charts/{chart_type.replace(' ', '_')}.png"

    if chart_type == "pie chart":
        plt.pie(counts, labels=departments, autopct='%1.1f%%')
        plt.title("Employee Share by Department")
    elif chart_type == "bar chart":
        plt.bar(departments, counts)
        plt.title("Employee Distribution by Department")
    elif chart_type == "line chart":
        plt.plot(departments, counts)
        plt.title("Employee Trend by Department")
    else:
        plt.hist(counts)
        plt.title("Employee Distribution by Department")

    plt.savefig(chart_path)

    plt.close()

    return f"Chart generated: [here]({chart_path})"



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
def count_employees() -> str:
    """
    Returns the total number of employees in the company database.
    Use this tool when the user asks about total employees count.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return f"Total employess in the company: {result[0]}"


@tool
def get_employees_by_department(department: str) -> str:
    """
    Retrieves employees working in a specific department.
    Use this tool when the user asks for employees from a department.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, role FROM employees WHERE department = %s", (department,))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    if not result:
        return f"No employees found in this department."
    
    employees = "\n".join(
        [f"{name} - {role}" for name, role in result]
    )

    return employees


@tool
def department_employee_count(department: str) -> str:
    """
    Returns the number of employees in each department.
    Use this tool when the user asks about department statistics.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department")

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    stats = "\n".join(
        [f"{dept}: {count} employees" for dept, count in result]
    )
    return stats

@tool
def query_company_database(question: str) -> str:
    """
    Use this tool to answer questions about company data stored in the postgreSQL database.
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

database_tools_list = [get_employee_details, query_company_database, count_employees, get_employees_by_department, department_employee_count, generate_chart]