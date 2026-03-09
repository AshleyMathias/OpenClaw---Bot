from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
from config.settings import DATABASE_URL
from automations.task_runner import send_motivation_quote    




scheduler = BackgroundScheduler()

def load_automations():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automations (
            id SERIAL PRIMARY KEY,
            task_name VARCHAR(255) NOT NULL,
            schedule_type VARCHAR(50) NOT NULL DEFAULT 'daily',
            schedule_time VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("SELECT task_name, schedule_time FROM automations")

    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    for task_name, schedule_time in tasks:

        hour, minute = schedule_time.split(":")

        if task_name == "send_motivation_quote":
            scheduler.add_job(
                send_motivation_quote,
                trigger="cron",
                hour = int(hour),
                minute = int(minute),
                timezone="Asia/Kolkata"
            )


def start_scheduler():

    load_automations()

    scheduler.start()

    print("OpenCLaw automations scheduler running...")