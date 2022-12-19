from spacy.language import Language

from regex_extractors.percent import GermanPercentages
from regex_extractors.regex_matcher import RegexpBasedMatcher


@Language.factory("regexp_percent_extractor")
class RegexpPercentExtractor(RegexpBasedMatcher):
    def __init__(self, nlp: Language, name: str):
        super(RegexpPercentExtractor, self).__init__(nlp, "PERCENT", GermanPercentages())
