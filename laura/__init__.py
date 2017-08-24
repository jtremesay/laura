import bs4
import fredirc
import logging
import re
import requests


REGEX_URL = re.compile("https?://\S+")


def extract_url(message):
    result = REGEX_URL.search(message)
    if result is None:
        raise ValueError

    url = result.group(0)

    return url


class Laura(fredirc.BaseIRCHandler):
    def __init__(self, channel):
        self.channel = channel

    def handle_register(self):
        self.client.join(self.channel)

    def handle_channel_message(self, channel, message, sender):
        try:
            url = extract_url(message)
        except ValueError:
            return

        r = requests.get(url)
        if r.status_code != 200:
            return

        if not r.headers['content-type'].startswith('text/html'):
            return

        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string

        self.client.send_message(channel, title)


def main():
    irc_server = "irc.zcraft.fr"
    irc_nick = "laura"
    irc_channel = "#sandbot"
    irc_channel = "#kamoulox"

    client = fredirc.IRCClient(Laura(irc_channel), irc_nick, irc_server)
    client.run()


if __name__ == "__main__":
    main()
