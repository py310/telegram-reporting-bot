import time
import logging
import schedule
from telebot import TeleBot
from threading import Thread
import helpers

# Define constants
LOG_FILE = 'report.log'

# Set up logger
logging.basicConfig(filename=LOG_FILE,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)

# Create telegram bot
bot = TeleBot(helpers.bot_token)

# Listen to channel and chat for manual request for the report
@bot.channel_post_handler(commands=["report"])
@bot.channel_post_handler(regexp='report')
@bot.message_handler(commands=["report"])
@bot.message_handler(regexp='report')
def send_report(message):
    if message.chat.id == helpers.channel or message.chat.id == helpers.user:
        bot.send_document(message.chat.id, helpers.create_report())
        logging.info(f'Manual request report has been sent, id: {message.chat.id}')
    else:
        bot.send_message(message.chat.id, 'No permissions')
        logging.warning(f'Unauthorized request attempt, id: {message.chat.id}')

# Send report to channel on schedule
def send_by_scheduler():
    id = helpers.channel
    bot.send_document(id, helpers.create_report())
    logging.info(f'Schedule report has been sent, id: {id}')

# Launch the telegram bot in polling mode
def run_bot_polling():
    bot.infinity_polling(logger_level=logging.DEBUG)

# Launch scheduled reports
def run_schedulers():
    schedule.every().tuesday.at('11:00').do(send_by_scheduler)
    schedule.every().wednesday.at('11:00').do(send_by_scheduler)
    schedule.every().thursday.at('11:00').do(send_by_scheduler)
    schedule.every().friday.at('11:00').do(send_by_scheduler)
    schedule.every().saturday.at('11:00').do(send_by_scheduler)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    logging.info('Reporter script started.')

    # Creating threads
    bot_thread = Thread(target=run_bot_polling)
    scheduler_thread = Thread(target=run_schedulers)

    # Start threads
    bot_thread.start()
    scheduler_thread.start()

    # Join threads to the main thread
    bot_thread.join()
    scheduler_thread.join()