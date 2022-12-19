import logging
import os
import subprocess
import sys
from pathlib import Path

import spacy

from resources_manager import ResourcesManager


class NLPManager:
    nlp_model_path: Path

    def __init__(self, resources_manager: ResourcesManager):
        self.resources_manager = resources_manager
        self.create_nlp_model_directory()

    @staticmethod
    def load_blank_model(model_language: str):
        return spacy.blank(model_language)

    def create_nlp_model_directory(self):
        self.nlp_model_path = os.path.join(self.resources_manager.get_model_path('nlp_models'))
        self.resources_manager.create_folder_if_none(self.nlp_model_path)

    @staticmethod
    def load_language_model(model_name: str):
        logging.info("Loading `nlp` model: {} from spacy ".format(model_name))
        try:
            nlp = spacy.load(model_name)
            nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
            return nlp
        except OSError:
            cmd_download = [sys.executable, "-m", "spacy", "download", model_name]
            subprocess.call(cmd_download, env=os.environ.copy())
            nlp = spacy.load(model_name)
            nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
            return nlp

    @staticmethod
    def check_pretrained_word_vectors(nlp):
        if "vectors" not in nlp.meta or not nlp.vocab.vectors.size:
            raise ValueError(
                "The `nlp` object should have access to pretrained word vectors, "
                " cf. https://spacy.io/usage/models#languages.")

    @staticmethod
    def check_pretrained_ner(nlp):
        if "ner" not in nlp.pipe_names:
            raise ValueError("The `nlp` object should have a pretrained `ner` component.")

    def save_nlp_model(self, nlp, model_name):
        # write the NLP pipeline (now including an EL model) to file

        model_path = os.path.join(self.nlp_model_path, model_name)

        logging.info(
            "Final NLP pipeline has following pipeline components: {}".format(
                nlp.pipe_names
            )
        )
        logging.info("Saving trained {} nlp model nlp to {}".format(model_name, model_path))
        nlp.to_disk(model_path)

    def load_saved_nlp_model(self, nlp, model_name: str):
        """
        this method will return the extended nlp model
        :param nlp: nlp model to extend the model on.
        :param model_name: trained nlp models pipelines
        :return extended_model_name: full nlp model with extended trained pipelines.
        """
        model_path = os.path.join(self.nlp_model_path, model_name)
        logging.info(
            "Loading saved {} nlp model from {}".format(model_name, model_path))
        try:
            return nlp.from_disk(model_path)
        except(ValueError, FileNotFoundError) as e:
            logging.warning("The {} nlp model was not found in path: {}".format(model_name, model_path))
            raise FileNotFoundError
