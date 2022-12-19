"""
 Text Analyser is responsible for NLP Model and the pipelines of our service.
"""

from models.named_entity import NamedEntity
from models.ned_analyser_interface import NamedEntitiesAnalyserInterface
# Pipelines
from nlp.nlp_manager import NLPManager
from nlp.pipelines.entity_linker.entity_linker import EntityLinker
# Helpers
from nlp.pipelines.text_preprocessing.text_preprocessing import TextPreprocessing


class NamedEntitiesAnalyser(NamedEntitiesAnalyserInterface):
    __DE_MODEL_NAME = "de_core_news_lg"

    def __init__(self):
        nlp = NLPManager.load_language_model(self.__DE_MODEL_NAME)
        self.nel = EntityLinker(nlp)

    def analyse_html(self, html_text) -> [NamedEntity]:
        named_entity_contents, sentiments = TextPreprocessing.preprocess_text(html_text)
        return self.nel.process(named_entity_contents)
        # return self.ner.ner_new(ner_text)

    def analyse_text(self, plain_text) -> [NamedEntity]:
        return self.nel.process_plain_text(plain_text)
    # return self.ner.ner_new(ner_text)
