import argparse
import bs4
import fredirc
import logging
import random
import re
import requests
import sys


# Regex for matching HTTP(S) URLs
REGEX_HTTP_URL = re.compile("https?://\S+")


def debug(msg, *args, **kwargs):
    """Log a message with debug level
    :param msg: the message
    :param args: positional args
    :param kwargs: keyword args
    """
    logger = logging.getLogger('laura')
    logger.debug(msg, *args, **kwargs)


def extract_http_urls_from_message(message):
    """Extract HTTP(S) URLs from a message
    :param message: the message
    :return: iterator to found HTTP(s) URLs in the message
    """
    # Use a regex for searching the URLs
    debug('searching HTTP(s) urls in message "%s"', message)
    urls = REGEX_HTTP_URL.findall(message)

    # Yield the urls
    for url in urls:
        yield url


def get_title_from_url(url):
    """Get the title from an HTTP(S) URL
    :param url: the URL
    :return: the title or None
    """
    # Get the resource
    debug('getting the resource from url "%s"', url)
    with requests.get(url, stream=True) as r:
        if r.status_code != 200:
            # Cannot get the resource, abort
            debug('invalid status_code %i', r.status_code)

            return None

        # Checks if the ressource is an HTML document
        if not r.headers['content-type'].startswith('text/html'):
            # Not the good type, abort
            debug('invalid resource type "%s"', r.headers['content-type'])
            return None

        # Read 1M characters from the document
        document = ''
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            document += chunk
            if len(document) > 1000000:
                break

    # Parse the HTML document and get the title
    debug('parsing the document')
    soup = bs4.BeautifulSoup(document, 'html.parser')
    if not soup.title or not soup.title.string:
        # title not found, abort
        debug('no title found')
        return None
    title = soup.title.string
    debug('title found "%s"', title)

    return title


def cleanup_title(title):
    """Cleanup a title
    :param title: the title
    :return: the cleaned up title
    """
    # Strip the title
    title = title.strip()

    return title


def get_titles_from_message(message, clean_title=True):
    """Get titles of HTTP(S) URLs presents in the message
    :param message: the message
    :return: Iterator to found title
    """
    # Extract URLs from the message
    urls = extract_http_urls_from_message(message)

    # Get titles
    titles = map(get_title_from_url, urls)

    # Remove None results
    titles = filter(lambda title: title is not None, titles)

    # Clean titles
    if clean_title:
        # Clean titles
        titles = map(cleanup_title, titles)

        # Remove empty titles
        titles = filter(lambda title: title, titles)

    # Yield titles
    for title in titles:
        yield title


def title_displayer(channel, message, client):
    """Send the title of a link present in the message
    :param channel: the channel name
    :param message: the received message
    :param client: the IRC client
    """
    # Get titles from message
    titles = get_titles_from_message(message)

    # Get the first title
    try:
        title = next(titles)
    except StopIteration:
        # No title found, abort
        return

    # Send the title to the channel
    client.send_message(channel, title)


class Laura(fredirc.BaseIRCHandler):
    """Main class"""
    def __init__(self, channel, nick):
        """Constructor
        :param channel: channel to join when connection is made
        :param nick: Nick of the bot
        """
        self.channel = channel
        self.nick = nick
        self.real_nick = None

    def handle_channel_message(self, channel, message, sender):
        """Received a message from a channel.
        :param channel: the channel name
        :param message: the received message
        :param sender: sender of the message
        """
        # Display the title of an url present in the message
        title_displayer(channel, message, self.client)

    def handle_error(self, error, **params):
        """Handle an error
        :param error: 3-digit error code (between 400 and 599)
        :params  params: Parameters of the error message, each consisting of
                a parameter name and a value.
        """
        debug('handling error %i', error)
        if error == fredirc.Err.NICKNAMEINUSE:
            # Pseudo already in use, generate a new nick
            debug('nick "%s" already in use', params['nick'])
            nick = '{}{}'.format(self.nick, random.randint(0, 100))
            debug('changing nick to "%s"', nick)
            self.client.change_nick(nick)
            return

    def handle_own_nick_change(self, old_nick, new_nick):
        """ The IRCCLient's nick name changed.
        :param old_nick: the old nick name.
        :param new_nick: the new nick name.
        """
        # Register the new nick
        debug('new nick is "%s"', new_nick)
        self.real_nick = new_nick

    def handle_register(self):
        """The client successfully registered to the server."""
        # Join the specified channel
        self.client.join(self.channel)


def main(args=None):
    """Main function
    :param args: args of the program. Use sys.argv if None
    """
    # Parse args
    parser = argparse.ArgumentParser(prog='laura')
    parser.add_argument('-s', '--server', default='irc.zcraft.fr', help='server to join')
    parser.add_argument('-n', '--nick', default='laura-dev', help='nick of the bot')
    parser.add_argument('-c', '--channel', default='#sandbot', help='channel to join')
    if args is None:
        args = sys.argv[1:]
    parsed_args = parser.parse_args(args)

    # Configure the logger
    logger = logging.getLogger('laura')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
            '%(asctime)s %(name)s (%(levelname)s): %(message)s')

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    stream_handler.setFormatter(formatter)

    # Configuration
    irc_server = parsed_args.server
    irc_nick = parsed_args.nick
    irc_channel = parsed_args.channel

    # Create a Laura instance
    laura = Laura(irc_channel, irc_nick)

    # Create a client and start it
    client = fredirc.IRCClient(laura, irc_nick, irc_server)
    client.enable_logging(True)
    client.set_log_level(logging.DEBUG)
    client.run()


if __name__ == "__main__":
    main()
