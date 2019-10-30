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
    args_parser.add_argument("-v", "--verbose", action="store_true")
    args_parser.add_argument(
        "--use-webhook", action="store_true", help="Use webhook instead of polling"
    )
    args_parser.add_argument("--webhook-host", default="0.0.0.0", help="Webhook host")
    args_parser.add_argument(
        "--webhook-port", type=int, default=80, help="Webhook port"
    )
    args_parser.add_argument("--webhook-url", help="Webhook url")
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
    if parsed_args.use_webhook:
        logging.info(
            "Starting webhook on %s:%i",
            parsed_args.webhook_host,
            parsed_args.webhook_port,
        )
        updater.start_webhook(
            listen=parsed_args.webhook_host,
            port=parsed_args.webhook_port,
            url_path=token,
        )
        updater.bot.set_webhook(parsed_args.webhook_url + "/" + token)
        updater.idle()
    else:
        logging.info("Starting polling...")
        updater.start_polling()


if __name__ == "__main__":
    main()
