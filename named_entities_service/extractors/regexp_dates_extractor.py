from spacy.language import Language

from regex_extractors.date import GermanDates
from regex_extractors.regex_matcher import RegexpBasedMatcher


@Language.factory("regexp_dates_extractor")
class RegEexDatesExtractor(RegexpBasedMatcher):
    def __init__(self, nlp: Language, name: str):
        super(RegEexDatesExtractor, self).__init__(nlp, "DATE", GermanDates())
