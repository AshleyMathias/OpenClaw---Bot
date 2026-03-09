from langchain.tools import tool
import re
import psycopg2
from config.settings import DATABASE_URL



@tool
def create_support_ticket(issue: str):
    """
    Creates a support ticket for technical issues. Use this tool when a user wants to create a ticket for:
    - Laptop/computer problems (not working, broken, slow, etc.)
    - Software bugs or errors
    - Login or access problems
    - System failures or outages
    - Any technical support request
    
    The issue parameter should contain a description of the problem (e.g., "laptop is not working", "cannot login to system").
    """
    # Simulating a support ticket creation process
    import random
    ticket_id = f"TICK{random.randint(1000, 9999)}"

    return f"Support ticket created successfully with ID: {ticket_id}. Issue reported: {issue}"



@tool
def send_notification(message: str) -> str:
    """
    Use this tool when a user wants to send a notfication
    or alert to a team or employee.
    """
    return f"Notification sent sucessfully: {message}"

@tool
def generate_report(topic: str) -> str:
    """
    Use this tool when a user ask to generate a report
    about a specific topic such as sales, performance, or analytics.
    """

    return f"Report generated successfully for topic:m {topic}"

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def _normalize_schedule_time(schedule_time: str) -> str:
    """Convert '3:50pm' / '3:50 PM' / '9:00 AM' to 24h 'HH:MM' for the scheduler."""
    s = schedule_time.strip().upper().replace(" ", "")
    match = re.match(r"^(\d{1,2}):(\d{2})(AM|PM)?$", s)
    if not match:
        return schedule_time[:20]  # fallback: truncate for storage
    hour, minute, ampm = int(match.group(1)), int(match.group(2)), (match.group(3) or "").upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def _ensure_automations_table(cursor):
    """Create the automations table if it does not exist; widen schedule_time if needed."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automations (
            id SERIAL PRIMARY KEY,
            task_name VARCHAR(255) NOT NULL,
            schedule_type VARCHAR(50) NOT NULL DEFAULT 'daily',
            schedule_time VARCHAR(20) NOT NULL
        )
    """)
    cursor.execute("""
        ALTER TABLE automations
        ALTER COLUMN schedule_time TYPE VARCHAR(20)
    """)


@tool
def create_automation(task_name:str, schedule_time:str) -> str:
    """
    Creates a scheduled automation task.
    Use this tool when the user asks to schedule something.
    """

    conn = get_connection()
    cursor = conn.cursor()

    _ensure_automations_table(cursor)

    stored_time = _normalize_schedule_time(schedule_time)
    cursor.execute(
        """
        INSERT INTO automations (task_name, schedule_type, schedule_time)
        VALUES (%s, 'daily', %s)
        """,
        (task_name, stored_time)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return f"Automation scheduled for {task_name} at {schedule_time}"


tools_list=[
    create_support_ticket,
    send_notification,
    generate_report,
    create_automation,
]

