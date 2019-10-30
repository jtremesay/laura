import abc
import argparse
import logging
import os
import subprocess
from telegram.ext import CommandHandler, Updater


def ping(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="@{} pong".format(update.effective_user.first_name),
    )


def main(args=None):
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-p", "--port", type=int, help="Port used for the webhook")
    args_parser.add_argument("-v", "--verbose", action="store_true")
    parsed_args = args_parser.parse_args(args)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO if not parsed_args.verbose else logging.DEBUG,
    )

    # Get the access token
    try:
        token = os.environ["LAURA_ACCESS_TOKEN"]
    except KeyError:
        logging.fatal("Access token not defined")
        return

    # Create the updater
    logging.info("Creating updater...")
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # Ping command
    logging.info("Registering command ping...")
    dispatcher.add_handler(CommandHandler("ping", ping))

    # Start the bot
    if parsed_args.port:
        logging.info("Starting webhook on port %i...", parsed_args.port)
        updater.start_webhook(listen="0.0.0.0", port=parsed_args.port)
    else:
        logging.info("Starting polling...")
        updater.start_polling()


if __name__ == "__main__":
    main()
