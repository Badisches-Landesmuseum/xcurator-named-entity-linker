from spacy.language import Language

from regex_extractors.money import GermanEuros
from regex_extractors.regex_matcher import RegexpBasedMatcher


@Language.factory("regexp_euro_extractor")
class RegEexEuroExtractor(RegexpBasedMatcher):
    def __init__(self, nlp: Language, name: str):
        super(RegEexEuroExtractor, self).__init__(nlp, "MONEY", GermanEuros())
