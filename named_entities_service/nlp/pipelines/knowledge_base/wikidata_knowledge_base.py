import logging
from pathlib import Path

from tqdm import tqdm

from nlp.nlp_manager import NLPManager
from resources.resources_manager import ResourcesManager
from wikipedia import kb_creator
from wikipedia import wiki_io as io
from wikipedia import wikipedia_processor as wp, wikidata_processor as wd
from wikipedia.wikidata_query_service import WikidataQueryService


class WikidataKnowledgeBase(object):
    # Wiki resources for knowledge base
    nlp_model_name = "wiki_kb"
    # Loaded if trained model not found, Path to the downloaded Wikipedia XML dump.
    wd_json = None
    # Loaded if trained model not found, Path to the downloaded Wikipedia XML dump.
    wp_xml = None

    # Configuration

    # Limitations
    # Threshold to limit lines read from WD (no limit: None)
    limit_wd: int = None
    # Threshold to limit lines read from WP for prior probabilities (no limit: None)
    limit_prior: int = None
    # "Threshold to limit articles lines read from WP for training set (no limit: None)
    limit_train: int = None
    max_per_alias: int = 10  # Maximum entities per alias (default 10)
    min_pair: int = 3  # "Min. count of entity-alias pairs (default 5)
    # Min. count of an entity in the corpus (default 20 , -1 to ignore frequencies.)
    min_freq: int = 20
    entity_vector_length: int = 64  # Length of entity vectors (default 64)[[
    # Optional language for which to get Wikidata titles. Set none for defaults 'en'
    lang: str = 'de'
    # "Flag for using descriptions from Wikipedia instead of WikiData
    descr_from_wp: bool = False

    # List with Qxxxx To specify which entities to download.(default None)
    entities_to_download: [] = None

    def __init__(self, nlp, resources_manager: ResourcesManager):
        self.__nlp = nlp
        self.resources_manager = resources_manager
        self.wd_qs = WikidataQueryService()

        self.entities_to_download_file_path = resources_manager.get_wikidata_entities_to_download_file()
        # Wiki created model paths6
        self.entity_defs_path = resources_manager.get_wiki_training_path(
            "wiki_entity_titles")
        self.entity_alias_path = resources_manager.get_wiki_training_path(
            "wiki_entity_alias")
        self.entity_descr_path = resources_manager.get_wiki_training_path(
            "wiki_entity_description")
        self.entity_freq_path = resources_manager.get_wiki_training_path(
            "wiki_entity_frequencies")
        self.prior_prob_path = resources_manager.get_wiki_training_path(
            "wiki_prior_probability")
        self.training_entities_path = resources_manager.get_wiki_training_path(
            "wiki_training_entities")
        self.kb_path = resources_manager.get_model_path(self.nlp_model_name)
        self.nlp_manager = NLPManager(resources_manager)

        # self.nlp_manager.check_pretrained_word_vectors(self.__nlp)
        # pipelines

        try:
            self.load_nlp_model()
        except FileNotFoundError:
            self.progress_bar: tqdm = self.create_progress_bar(5)
            self.load_dependent_models()
            self.create_prior_probabilities()  # 1.Step
            self.calculate_entity_frequencies()  # 2.Step
            self.parse_and_write_entities()  # 3.Step
            self.create_training()  # 4.Step
            self.create_kb()  # 5.Step

    def load_dependent_models(self):
        self.print_progress_bar(
            "Wiki KB model was not found -> Loading dependent models", False)
        self.wd_json = self.get_wikidata_resource("latest-all.json.bz2",
                                                  "entities")  # "Path to the downloaded WikiData JSON dump
        self.wp_xml = self.get_wikidata_resource("dewiki-latest-pages-articles.xml.bz2",
                                                 "articles")  # Path to the downloaded Wikipedia XML dump.

    def download_custom_entities_from_wiki(self, knowledge_base_ids: []):
        self.print_progress_bar(
            "Adding entities from file for downloading", False)
        if knowledge_base_ids:
            logging.info("Adding to the list {}".format(knowledge_base_ids))
            self.entities_to_download += knowledge_base_ids

        try:
            with self.entities_to_download_file_path.open("r", encoding="utf8") as _file:
                line = _file.readline()
                while line:
                    self.entities_to_download.append(line.strip())
                    line = _file.readline()
        except FileNotFoundError:
            logging.info("No entities to download")

    def create_prior_probabilities(self):
        # Read the XML wikipedia data and parse out intra-wiki links to estimate prior probabilities.
        self.print_progress_bar(
            "Creating prior probabilities from Wikipedia", True)

        if not self.prior_prob_path.exists():
            if self.limit_prior is not None:
                logging.warning(
                    "Warning: reading only {} lines of Wikipedia dump".format(self.limit_prior))
            logging.info("Creating prior probabilities from WP")
            wp.read_prior_probs(
                self.wp_xml, self.prior_prob_path, limit=self.limit_prior)
        else:
            logging.info("Reading prior probabilities from {}".format(
                self.prior_prob_path))

    def calculate_entity_frequencies(self):
        self.print_progress_bar(
            "Calculating and writing entity frequencies", True)

        if not self.entity_freq_path.exists():
            logging.info("Calculating and writing entity frequencies to {}".format(
                self.entity_freq_path))
            io.write_entity_to_count(
                self.prior_prob_path, self.entity_freq_path)
        else:
            logging.info("Reading entity frequencies from {}".format(
                self.entity_freq_path))

    def parse_and_write_entities(self):
        self.print_progress_bar(
            "Reading definitions and (possibly) descriptions from WikiData or from file", True)

        # It takes about 10h to process 55M lines of Wikidata JSON dump
        if (not self.entity_defs_path.exists()) or (not self.descr_from_wp and not self.entity_descr_path.exists()):

            # reading definitions and (possibly) descriptions from WikiData or from file
            if self.limit_wd is not None:
                logging.warning(
                    "Warning: reading only {} lines of Wikipedia dump".format(self.limit_wd))

            title_to_id, id_to_descr, id_to_alias = wd.read_wikidata_entities_json(
                self.wd_json,
                self.limit_wd,
                to_print=False,
                lang=self.lang,
                parse_descr=(not self.descr_from_wp),
            )

            if self.entities_to_download is not None:
                self.download_custom_entities_from_wiki(
                    self.entities_to_download)

                logging.warning("Info: reading  {} entities of Wikipedia Server".format(
                    self.entities_to_download))

                query_title_to_id, query_id_to_descr, query_id_to_alias = self.wd_qs.get_parsed_entities(
                    self.entities_to_download)

                title_to_id.update(query_title_to_id)
                id_to_descr.update(query_id_to_descr)
                id_to_alias.update(query_id_to_alias)

            io.write_title_to_id(self.entity_defs_path, title_to_id)
            logging.info("Writing Wikidata entity aliases to {}".format(
                self.entity_alias_path))
            io.write_id_to_alias(self.entity_alias_path, id_to_alias)

            if not self.descr_from_wp:
                logging.info("Writing Wikidata entity descriptions to {}".format(
                    self.entity_descr_path))
                io.write_id_to_descr(self.entity_descr_path, id_to_descr)

        else:
            logging.info("Reading entity definitions from {}".format(
                self.entity_defs_path))
            logging.info("Reading entity aliases from {}".format(
                self.entity_alias_path))
            if not self.descr_from_wp:
                logging.info("Reading entity descriptions from {}".format(
                    self.entity_descr_path))

    def create_training(self):
        self.print_progress_bar(
            "Wikipedia Parsing and writing gold entities", True)

        if (not self.training_entities_path.exists()) or (self.descr_from_wp and not self.entity_descr_path.exists()):
            logging.info("Parsing and writing Wikipedia gold entities to {}".format(
                self.training_entities_path))
            if self.limit_train is not None:
                logging.warning(
                    "Warning: reading only {} lines of Wikipedia dump".format(self.limit_train))
            wp.create_training_and_desc(self.wp_xml, self.entity_defs_path, self.entity_descr_path,
                                        self.training_entities_path, self.descr_from_wp, self.limit_train)
            if self.descr_from_wp:
                logging.info("Parsing and writing Wikipedia descriptions to {}".format(
                    self.entity_descr_path))
        else:
            logging.info("Reading gold entities from {}".format(
                self.training_entities_path))
            if self.descr_from_wp:
                logging.info("Reading entity descriptions from {}".format(
                    self.entity_descr_path))

    def create_kb(self):
        self.print_progress_bar("Wikipedia Creating the KB", True)

        if not self.kb_path.exists():
            logging.info("Creating the KB at {}".format(self.kb_path))
            kb = kb_creator.create_kb(
                nlp=self.__nlp,
                max_entities_per_alias=self.max_per_alias,
                min_entity_freq=self.min_freq,
                min_occ=self.min_pair,
                entity_def_path=self.entity_defs_path,
                entity_descr_path=self.entity_descr_path,
                entity_alias_path=self.entity_alias_path,
                entity_freq_path=self.entity_freq_path,
                prior_prob_path=self.prior_prob_path,
                entity_vector_length=self.entity_vector_length,
            )
            # Save the current state of the knowledge base to a directory.
            kb.dump(self.kb_path)
            logging.info("wiki_kb entities: {}".format(kb.get_size_entities()))
            logging.info("wiki_kb aliases: {}".format(kb.get_size_aliases()))
            self.print_progress_bar(
                "Step 5: Saving Wikidata Knowledge Base nlp Model", False)
            self.nlp_manager.save_nlp_model(self.__nlp, self.nlp_model_name)
        else:
            logging.info("KB already exists at {}".format(self.kb_path))
            self.load_nlp_model()

    @staticmethod
    def create_progress_bar(steps: int):
        return tqdm(total=steps, desc="Initializing Wikidata Knowledge Base",
                    bar_format='{l_bar}{bar}{n_fmt}/{total_fmt}')

    def print_progress_bar(self, description, increase_level: bool = False):
        self.progress_bar.set_description(desc=description)
        if increase_level:
            self.progress_bar.update()

    def load_nlp_model(self):
        self.__nlp = self.nlp_manager.load_saved_nlp_model(
            self.__nlp, self.nlp_model_name)

    def get_wikidata_resource(self, file_name, source_type: str):
        file_path = self.resources_manager.get_wiki_resources(file_name)
        if not Path(file_path).exists():
            switcher = {
                'entities': 'https://dumps.wikimedia.org/wikidatawiki/entities/',
                'articles': 'https://dumps.wikimedia.org/dewiki/latest/',
            }
            url = switcher.get(source_type) + file_name
            ResourcesManager.download_file(url, str(file_path), file_name)
        return str(file_path)
