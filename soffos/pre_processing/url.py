import re

from .text import TextSpan


URL_PATTERN = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


class Url(TextSpan):
    @classmethod
    def from_text(cls, text: str):
        matches = re.finditer(URL_PATTERN, text)
        return cls.from_matches(matches)


def replace_urls(text: str, replacement: str = 'url'):
    return re.sub(URL_PATTERN, replacement, text)
