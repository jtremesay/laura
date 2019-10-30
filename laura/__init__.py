import abc
import logging
import os
import subprocess
from telegram.ext import CommandHandler, Updater


def ping(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="@{} pong".format(update.effective_user.first_name),
    )


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    try:
        token = os.environ["LAURA_ACCESS_TOKEN"]
    except KeyError:
        logging.fatal("Access token not defined")
        return

    logging.debug("Access token is XXXX")


    logging.info("Creating updater...")
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # Ping command
    logging.info("Registering command ping...")
    dispatcher.add_handler(CommandHandler("ping", ping))

    # Start the bot
    logging.info("Starting polling...")
    updater.start_polling()


if __name__ == "__main__":
    main()
