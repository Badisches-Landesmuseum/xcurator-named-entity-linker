"""
 To train an entity linking model it's necessary
 to define a knowledge base (KB)
 and construct it first.

 For more details, see the documentation:
 Knowledge base: https://spacy.io/api/kb
"""

import logging

from spacy.kb import KnowledgeBase as Spacy_KnowledgeBase
from spacy.vocab import Vocab

from resources.resources_manager import ResourcesManager
from wikipedia.train_descriptions import EntityEncoder


class CustomKnowledgeBase(object):
    kb: Spacy_KnowledgeBase = None
    ENTITIES = {}

    # Configuration for the Entity Encoder
    INPUT_DIM = 300  # dimension of pretrained input vectors
    DESC_WIDTH = 64  # dimension of output entity vectors
    N_ITER = 50  # Number of training iterations

    def __init__(self, nlp, resources_manager: ResourcesManager):
        logging.info("Initializing Knowledge Base")
        self.__nlp = nlp
        self.kb_path = resources_manager.get_model_path("custom_kb")
        self.vocab_path = resources_manager.get_model_path("vocab")

        try:
            self.load_models()
            self._print_kb()

        except ValueError:
            self.start_training()
            self.__nlp.vocab = self.kb.vocab  # Saving the vocab with knowledge base

    def start_training(self):
        logging.info("Creating Knowledge Base Model")

        self.kb = Spacy_KnowledgeBase(vocab=self.__nlp.vocab)
        self.load_entities()

        # setting up the data
        entity_ids = []
        descriptions = []
        frequencies = []

        for key, value in self.ENTITIES.items():
            desc, freq = value
            entity_ids.append(key)
            descriptions.append(desc)
            frequencies.append(freq)

        # initialization and training the encoder for the embeddings.
        encoder = self.entity_encoder_init()
        encoder.train(descriptions, to_print=True)

        # get the pretraind entity vectors
        embeddings = encoder.apply_encoder(descriptions)

        # setting the entity. Alternative can be use with add entity for one
        self.kb.set_entities(entity_list=entity_ids, freq_list=frequencies, vector_list=embeddings)
        self.add_aliases()
        self.save_model()

    # TODO Global prior probabilities for text.
    def create_prior_probabilities(self):
        logging.info("Writing prior probabilities")

    # TODO Function for loading text in order to create probabilities of word.
    def load_text(self):
        logging.info("Loading text")

    # TODO Calculate entity frequencies
    def create_prior_probabilities(self):
        logging.info("Calculate entity frequencies")

    # TODO working with JSON
    def load_entities(self):
        """
        Defining the full list of entities in the knowledge base:
        a. List of unique entity identifiers
        b. List of entity frequencies,
        c. List of entity vectors
        """

        # Q64      (Berlin): Capital and largest city of Germany
        # Q1569850 (Berlin): city in Green Lake and Waushara Counties, Wisconsin, USA

        self.ENTITIES = {
            "Q64": ("Capital city in Germany", 342),
            "Q1569850": ("City in Green Lake", 17)
        }

    def entity_encoder_init(self):
        # initialisation of the entity encoder
        # training entity description encodings can be repalced with custom encoder
        return EntityEncoder(
            nlp=self.__nlp,
            input_dim=self.INPUT_DIM,
            desc_width=self.DESC_WIDTH,
            epochs=self.N_ITER,
        )

    def add_aliases(self):
        # adding aliases, the entities need to be defined in the KB beforehand
        self.kb.add_alias(
            alias="Berlin",
            entities=["Q64", "Q1569850"],
            probabilities=[0.7, 0.15],  # the sum of these probabilities should not exceed 1
        )

    def _print_kb(self):
        print(self.kb.get_size_entities(), "wiki_kb entities:", self.kb.get_entity_strings())
        print(self.kb.get_size_aliases(), "wiki_kb aliases:", self.kb.get_alias_strings())

    def save_model(self):
        self.kb.dump(self.kb_path)
        self.kb.vocab.to_disk(self.vocab_path)
        print("Saved vocab to", self.vocab_path)

    def load_models(self):
        try:
            # always reload a knowledge base with the same vocab instance

            print("Loading  vocab from", self.vocab_path)
            vocab = Vocab().from_disk(self.vocab_path)

            print("Loading existed KB from", self.kb_path)
            self.kb = Spacy_KnowledgeBase(vocab=vocab)
            self.kb.load_bulk(self.kb_path)

        except:
            logging.warning("Models are missing in: {}, {}".format(self.kb_path, self.vocab_path))
            raise ValueError
