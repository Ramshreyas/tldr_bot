from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from db.db import get_db
from db.models import Subscriber
from tldr.tldr import fetch_latest_tldr, format_tldr

# Function to send TLDRs to all subscribers
async def send_daily_tldr(context):
    latest_tldr = fetch_latest_tldr()
    formatted_tldr = format_tldr(latest_tldr)
    
    with next(get_db()) as session:
        subscribers = session.query(Subscriber).all()
        for subscriber in subscribers:
            try:
                await context.bot.send_message(chat_id=subscriber.user_id, text=formatted_tldr)
            except Exception as e:
                print(f"Error sending message to {subscriber.user_id}: {e}")

# Setup the scheduler
def setup_scheduler(bot: Bot):
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(send_daily_tldr, CronTrigger(hour=9, minute=15), args=[bot])
    scheduler.start()
