from langchain.tools import tool



@tool
def create_support_ticket(issue: str):
    """
    Use this tool when a user wants to create a support ticket for a problem such as laptop issues,
    software bugs, login problems, or system failures.
    """

    # Simulating a support ticket creation process
    ticket_id = "TICK1234"

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

