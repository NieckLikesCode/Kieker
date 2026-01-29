import unicodedata
import re

from Clip import Clip


def find_link_in_message(message):
    """
    Finds and returns the first medal.tv clip link in the message.
    :param message: message you want to filter
    :return: medal.tv clip link if found, else None
    """
    pattern = r"https?://(?:www\.)?medal\.tv/[^\s)]*/clips/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)?"

    match = re.search(pattern, message)
    if match:
        return match.group(0)
    return None

def sanitize_link(link):
    '''
    Removes '?invite=...' tracking parameter from link
    :param link: link to sanitize
    :return: sanitized link
    '''
    if '?invite' in link:
        return link[0:link.index('?invite')]
    return link

def format_placeholder_by_clip(placeholder: str, clip: Clip):
    """
    Formats placeholder string as specified in config by inserting clip information
    :param placeholder: placeholder string
    :param clip: clip object
    :return: formatted placeholder string
    """
    replacements = {
        'title': clip.title,
        'author_name': clip.author.name,
        'author_url': clip.author.link,
        'game': clip.game,
        'time': clip.time,
        'url': clip.url,
        'timestamp': clip.timestamp(),
    }
    return placeholder.format(**replacements)

def slugify(value, allow_unicode=False):
    """
    https://github.com/django/django/blob/main/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")