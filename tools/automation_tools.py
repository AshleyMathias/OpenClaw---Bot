from langchain.tools import tool



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



tools_list=[
    create_support_ticket,
    send_notification,
    generate_report,
]

