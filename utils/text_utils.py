import unicodedata
import re

from Clip import Clip

def find_link_in_message(message):
    words = message.split()

    for word in words:
        if 'medal.tv' in word:
            return word
    return None

# Removes '?invite=...' tracking from urls
def sanitize_link(link):
    if '?invite' in link:
        return link[0:link.index('?invite')]
    return link

# Formats placeholder string as specified in config by inserting clip information
def format_placeholder_by_clip(placeholder: str, clip: Clip):
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