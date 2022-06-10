import typing as t
import string
import json
import re

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import nltk

from ..utilities import LazyLoader


def load_stopwords() -> t.Dict[str, t.Set[str]]:
    nltk.download('stopwords', download_dir='volume/nltk')
    # TODO: investigate if this is needed.
    nltk.download('averaged_perceptron_tagger', download_dir='volume/nltk')
    # Get stopwords for each supported language.
    return {
        lang: set(stopwords.words(lang))
        for lang in stopwords.fileids()
    }


def load_contractions() -> t.Dict[str, str]:
    with open('volume/contractions.json', 'r', encoding='utf-8') as contractions_file:
        return json.load(contractions_file)


STOPWORDS = LazyLoader(load_stopwords)
CONTRACTIONS = LazyLoader(load_contractions)


class TextSpan(t.NamedTuple):
    text: str
    span: t.Tuple[int, int]

    @property
    def length(self):
        return len(self.text)

    @property
    def span_start(self):
        return self.span[0]

    @property
    def span_end(self):
        return self.span[1]


def remove_punctuations(text: str):
    return text.translate(str.maketrans('', '', string.punctuation))


def expand_contractions(
    text: str,
    contractions: t.Dict[str, str] = None,
    ignore_case: bool = True
):
    if contractions is None:
        contractions = CONTRACTIONS.lazy_load()
    pattern = (
        r'(?:(?<=^)|(?<= ))'
        + f"({'|'.join(map(re.escape, contractions.keys()))})"
        + r'(?:(?=$)|(?= )|(?=\.))'
    )
    flags = re.MULTILINE
    if ignore_case:
        flags |= re.IGNORECASE
        contractions = {
            contraction.lower(): expansion
            for contraction, expansion in contractions.items()
        }

    def expand_contraction(match: re.Match):
        contraction: str = match.group()
        contraction = contraction.lower() if ignore_case else contraction
        expansion = contractions[contraction]
        if contraction[0].isupper() and expansion[1].islower():
            expansion = expansion[0].upper() + expansion[1:]
        return expansion

    return re.compile(pattern, flags).sub(expand_contraction, text)


def strip_html_tags(text: str):
    return BeautifulSoup(text, 'html.parser').get_text()


def remove_non_ascii_chars(text: str):
    """Remove non-ascii characters from text."""
    return text.encode('ascii', 'ignore').decode()


def get_language(text: str):
    """Detect language based on the presence of stop words."""
    words = set(nltk.wordpunct_tokenize(text.lower()))
    lang_stopword_counts = {
        lang: len(words & stopwords)
        for lang, stopwords in STOPWORDS.lazy_load().items()
    }
    return max(lang_stopword_counts.items(), key=lambda item: item[1])[0]


def replace_emails(text: str, replacement: str = 'email'):
    # NOTE: https://www.w3resource.com/javascript/form/email-validation.php
    return re.sub(r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*", replacement, text)


def replace_urls(text: str, replacement: str = 'url'):
    return re.sub(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", replacement, text)


def replace_newlines(text: str, replacement: str = ' '):
    return re.sub(r'[\r|\n|\r\n]+', replacement, text)


def replace_excessive_spaces(text: str):
    return re.sub(r'[ ]{2,}', ' ', text)


def replace_brackets(text: str, replacement: str = ''):
    return re.sub(r'( )?[\(\[].*?[\)\]]', replacement, text)


def replace_special_chars(text: str, replacement: str = ''):
    return re.sub(r'[^a-zA-Z0-9.,!?/:;\"\'\s]', replacement, text)