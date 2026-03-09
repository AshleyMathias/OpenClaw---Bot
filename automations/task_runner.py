import random

quotes = [
    "Success is built on consistency",
    "Small progress every day adds up to big results",
    "The only way to do great work is to love what you do",
    "Your time is limited, don't waste it living someone else's life",
    "The best way to predict the future is to invent it",
    "Great things take time",
    "Keep Learning, Keep building"
]


def send_motivation_quote():
    """
    Sends a motivation quote reminder.
    """

    quote = random.choice(quotes)

    print("OpenClaw Automation Triggered")
    print("Motivation Quote:", quote)