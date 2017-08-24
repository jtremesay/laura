import bs4
import fredirc
import logging
import re
import requests

# Regex for matching HTTP(S) URLs
REGEX_HTTP_URL = re.compile("https?://\S+")


def extract_http_url(str_):
    """Extract a HTTP(S) URL from a string
    :param str_: the string
    :return: the first HTTP(s) URL found or None otherwise
    """
    # Use a regex for searching a URL
    result = REGEX_HTTP_URL.search(str_)
    if result is None:
        # No URL found, return None
        return None

    # Get the URL from the match result
    url = result.group(0)

    return url


class Laura(fredirc.BaseIRCHandler):
    """Main class"""
    def __init__(self, channel):
        """Constructor
        :param channel: channel to join when connection is made
        """
        self.channel = channel

    def handle_channel_message(self, channel, message, sender):
        """Received a message to a channel.
        :param channel: the channel name
        :param message: the received message
        :param sender: sender of the message
        """
        # Search an HTTP(S) URL in the message
        url = extract_http_url(message)
        if url is None:
            # URL not found, abort
            return

        # Get the resource
        r = requests.get(url)
        if r.status_code != 200:
            # Cannot get the resource, abort
            return

        # Checks if the ressource is an HTML docu;ent
        if not r.headers['content-type'].startswith('text/html'):
            # Not the good type, abort
            return

        # Parse the HTML document and get the title
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string

        # Clean up the title
        title = title.strip()

        # Check if the title is not empty
        # This test must be done after cleanup because the cleanup
        # step can generate an empty title from a non-empty title
        if not title:
            # The title is empty, abort
            return

        # Send the title in the channel
        self.client.send_message(channel, title)

    def handle_register(self):
        """The client successfully registered to the server."""
        # Join the specified channel
        self.client.join(self.channel)


def main():
    """Main function"""

    # Configuration
    irc_server = "irc.zcraft.fr"
    irc_nick = "laura"
    irc_channel = "#sandbot"
    irc_channel = "#kamoulox"

    # Create a Laura instance, a client and start the client
    laura = Laura(irc_channel)
    client = fredirc.IRCClient(laura, irc_nick, irc_server)
    client.run()


if __name__ == "__main__":
    main()
