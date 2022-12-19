"""
 To train an entity linking model it's necessary
 to define a knowledge base (KB)
 and construct it first.

 For more details, see the documentation:
 Entity Linking: https://spacy.io/usage/linguistic-features#entity-linking
"""

from models.entity_type import EntityType
from models.named_entity import NamedEntity
from nlp.pipelines.text_preprocessing.text_preprocessing import TextPreprocessing


class EntityLinker(object):
    pipes = ['tagger', 'parser', 'ner', 'entity_matcher']

    def __init__(self, nlp):
        self.__nlp = nlp
        self.__nlp.add_pipe('opentapioca')

    def process_plain_text(self, text):
        doc = self.__nlp(text)
        entities = []
        for entity in doc.ents:
            entities.append(
                NamedEntity(literal=entity.text,
                            type=entity.label_,
                            start_position=entity.start,
                            end_position=entity.end,
                            knowledge_base_id=entity.kb_id_,
                            knowledge_base_url=(
                                "https://www.wikidata.org/entity/" + entity.kb_id_ if entity.kb_id_ else "")
                            )
            )
        return entities

    def process(self, contents):
        entities = []
        counter = 0

        texts = [text[0] for text in contents]
        for doc in self.__nlp.pipe(texts):  # , disable=[pipe for pipe in pipelines if pipe not in self.pipelines]):
            original_start_pos = contents[counter][1]
            position_map = contents[counter][4]
            # print("Tokens", [(t.text, t.ent_type_, t.ent_kb_id_) for t in doc])
            for entity in doc.ents:
                if entity.label_ not in EntityType.__members__:
                    continue
                start_position = TextPreprocessing.orig_text_to_cleaned_text_position(position_map, entity.start_char,
                                                                                      original_start_pos)
                end_position = TextPreprocessing.orig_text_to_cleaned_text_position(position_map, entity.end_char,
                                                                                    original_start_pos)

                entities.append(
                    NamedEntity(literal=entity.text,
                                type=entity.label_,
                                start_position=start_position,
                                end_position=end_position,
                                knowledge_base_id=entity.kb_id_,
                                knowledge_base_url=(
                                    "https://www.wikidata.org/entity/" + entity.kb_id_ if entity.kb_id_ else "")
                                )
                )

            counter += 1

        return entities
