import logging

# Rule Spacy Extractor
from spacy.language import Language

from extractors.email_extractor import EmailExtractor
from extractors.regexp_dates_extractor import RegEexDatesExtractor
from extractors.regexp_euro_extractor import RegEexEuroExtractor
from extractors.regexp_percent_extractor import RegexpPercentExtractor
from extractors.url_extractor import UrlExtractor
from models.entity_type import EntityType
from models.named_entity import NamedEntity
from nlp.pipelines.german_tokenizer import german_tokenizer
from nlp.pipelines.text_preprocessing.text_preprocessing import TextPreprocessing


@Language.factory("token_email_extractor", default_config={"case_sensitive": False})
def create_token_email_extractor(nlp: Language, name: str, case_sensitive: bool):
    return EmailExtractor()


@Language.factory("token_url_extractor", default_config={"case_sensitive": False})
def create_token_url_extractor(nlp: Language, name: str, case_sensitive: bool):
    return UrlExtractor()


class EntityRecognizer(object):
    pipes = []

    def __init__(self, nlp):
        logging.info("Initializing Entity Recognizer")

        self.__nlp = nlp
        self.pipes.append('tagger')
        self.pipes.append('parser')

        self.__nlp.tokenizer = german_tokenizer(self.__nlp)

        RegEexDatesExtractor(nlp, name='regexp_dates_extractor')
        self.__nlp.add_pipe("regexp_dates_extractor", name='regexp_dates_extractor', before='ner')
        self.pipes.append('regexp_dates_extractor')

        RegEexEuroExtractor(nlp, name="regexp_euro_extractor")
        self.__nlp.add_pipe("regexp_euro_extractor", name='regexp_euro_extractor', before='ner')
        self.pipes.append('regexp_euro_extractor')

        RegexpPercentExtractor(nlp, name="regexp_percent_extractor")
        self.__nlp.add_pipe("regexp_percent_extractor", name='regexp_percent_extractor', before='ner')
        self.pipes.append('regexp_percent_extractor')

        self.__nlp.add_pipe("token_email_extractor", name='token_email_extractor', before='ner')
        self.pipes.append('token_email_extractor')

        self.__nlp.add_pipe("token_url_extractor", name='token_url_extractor', before='ner')
        self.pipes.append('token_url_extractor')
        self.pipes.append('ner')

    def process(self, contents) -> [NamedEntity]:
        counter = 0
        entities: [NamedEntity] = []
        texts = [text[0] for text in contents]

        pipelines = [pipe[0] for pipe in self.__nlp.pipeline]

        for doc in self.__nlp.pipe(texts, disable=[pipe for pipe in pipelines if pipe not in self.pipes]):
            original_start_pos = contents[counter][1]
            position_map = contents[counter][4]

            for entity in doc.ents:
                if entity.label_ not in EntityType.__members__:
                    continue
                # if entity.start_char > 0:
                #     match = re.match(r"ß",doc.text[:entity.start_char])
                #     if match:
                #         minus_handling = len(match)
                # minus_handling = doc.text[:entity.start_char].count('ß') # ß has a length of 2 in spacy which is not correct
                start_position = TextPreprocessing.orig_text_to_cleaned_text_position(position_map, entity.start_char,
                                                                                 original_start_pos)
                end_position = TextPreprocessing.orig_text_to_cleaned_text_position(position_map, entity.end_char,
                                                                               original_start_pos)

                entities.append(
                    NamedEntity(
                        literal=entity.text,
                        type=entity.label_,
                        start_position=start_position,
                        end_position=end_position,
                    ))

            counter += 1

        return entities
