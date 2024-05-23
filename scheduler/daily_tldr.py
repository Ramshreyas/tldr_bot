from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from db.db import get_db
from db.models import Subscriber
from tldr.tldr import fetch_latest_tldr, format_tldr
import logging


# Function to send TLDRs to all subscribers
async def send_daily_tldr(context):
    latest_tldr = fetch_latest_tldr()
    formatted_tldr = format_tldr(latest_tldr)
    
    async with next(get_db()) as session:
        subscribers = session.query(Subscriber).all()
        for subscriber in subscribers:
            try:
                await context.bot.send_message(chat_id=subscriber.user_id, text=formatted_tldr)
                logging.info(f"Sent TLDR to {subscriber.user_id}")
            except Exception as e:
                logging.error(f"Error sending message to {subscriber.user_id}: {e}")


# Setup the scheduler
def setup_scheduler(application):
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(send_daily_tldr, CronTrigger(hour=9, minute=30), args=[application])
    scheduler.start()
    return scheduler
