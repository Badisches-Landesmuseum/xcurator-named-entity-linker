import re
from html.parser import HTMLParser

from scispacy.abbreviation import AbbreviationDetector

from models.abbreviation_entity import AbbreviationEntity
from nlp.pipelines.german_tokenizer import german_tokenizer
from nlp.pipelines.text_preprocessing.text_preprocessing import TextPreprocessing


class DreiPcAbbreviationDetector(HTMLParser):
    abbreviation_regex_pattern = re.compile(
        r"\b(?:[A-ZÖÄÜa-züöäß]*){1,}|([a-züöäßA-ZÜÖÄ]+\.+)+|\b(?:[A-ZÜÖÄa-züöäß-]*){1,}")

    def __init__(self, nlp, *args, **kwargs):
        super(DreiPcAbbreviationDetector, self).__init__(*args, **kwargs)
        self._nlp = nlp
        self._nlp.tokenizer = german_tokenizer(self._nlp)
        self.abbreviation_detector = AbbreviationDetector(self._nlp)
        self._nlp.add_pipe(self.abbreviation_detector)
        self.long_form = ""
        self.abbreviations = dict()
        self.is_body = False

    def is_abbreviation(self, short_form: str, long_form: str):
        return len(short_form) < len(long_form) \
               and re.match(self.abbreviation_regex_pattern, short_form)

    def store(self, short_form: str, long_form: str):
        if short_form not in self.abbreviations:
            self.abbreviations[short_form] = set()
        self.abbreviations[short_form].add(long_form)

    def abbreviation_detection(self, text: str):
        pipelines = [pipe[0] for pipe in self._nlp.pipeline]
        for doc in self._nlp.pipe(text.split("\n"), disable=[pipe for pipe in pipelines if
                                                             pipe not in ['tagger', 'AbbreviationDetector']]):
            for abbr_span in doc._.abbreviations:
                abbr_short_form = str(abbr_span)
                abbr_long_form = str(abbr_span._.long_form)

                if self.is_abbreviation(abbr_short_form, abbr_long_form):
                    if abbr_short_form not in self.abbreviations:
                        self.abbreviations[abbr_short_form] = set()
                    self.abbreviations[abbr_short_form].add(abbr_long_form)

        result = []
        for short_form, long_forms in self.abbreviations.items():
            result.append(AbbreviationEntity(short_form, long_forms))

        return result

    def html(self, html_content: str, contents):
        self.long_form = ""
        self.abbreviations = dict()
        self.is_body = not "<head>" in html_content
        self.feed(html_content)

        texts = [text[0] for text in contents]
        text = "\n".join(texts)
        text = TextPreprocessing.replace_with_whitespace(text, r'[^a-zA-züöäÖÄÜß0-9\s\-\&\/\(\)\.]')
        text = TextPreprocessing.remove_multi_whitespace(text)

        return self.abbreviation_detection(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.is_body = True
        elif tag == 'footer':
            self.is_body = False
        if tag == 'abbr':
            for name, value in attrs:
                if name == 'title':
                    self.long_form = value

    def handle_data(self, data):
        if data.strip() and self.lasttag in ['abbr']:
            if self.long_form:
                if data not in self.abbreviations:
                    self.abbreviations[data] = set()
                if len(self.long_form) > len(data):
                    self.abbreviations[data].add(self.long_form)
                    self.long_form = ""
