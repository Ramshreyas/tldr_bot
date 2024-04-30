# telegram.ext
from telegram import Update
from telegram.ext import ContextTypes, ContextTypes


# Handler for /tldr
async def tldr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""
TLDR for 30th April, 2024:
---------------------------------

Topic 1:
 Lorem ipsum dolor sit amet, consectetur adipiscing elit.
 Sed do eiusmod tempor incididunt ut labore et dolore magna 
 aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
 ullamco laboris nisi ut aliquip ex ea commodo consequat.                       
                           
Topic 2:
 Lorem ipsum dolor sit amet, consectetur adipiscing elit.
 Sed do eiusmod tempor incididunt ut labore et dolore magna 
 aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
 ullamco laboris nisi ut aliquip ex ea commodo consequat.
                                   
Topic 3:
 Lorem ipsum dolor sit amet, consectetur adipiscing elit.
 Sed do eiusmod tempor incididunt ut labore et dolore magna 
 aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
 ullamco laboris nisi ut aliquip ex ea commodo consequat.
""")