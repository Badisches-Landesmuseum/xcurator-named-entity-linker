from spacy.language import Language
from spacy.pipeline import EntityRuler

from gazetter.siemens_matcher_dict import SiemensMatcherDirectory


@Language.factory("siemens_ruler")
class SiemensEntityRuler(EntityRuler):
    def __init__(self, nlp: Language, name: str):
        super(SiemensEntityRuler, self).__init__(nlp, name)
        siemens_matcher = SiemensMatcherDirectory()
        self.add_patterns(siemens_matcher.patterns)
