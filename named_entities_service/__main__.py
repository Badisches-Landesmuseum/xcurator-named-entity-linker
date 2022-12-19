"""
 App includes all the code regarding our Rest Controller with the help of flask
"""
import logging

import spacy
from ariadne.asgi import GraphQL
from py_config.application_config import YamlConfig
from rabbitmq_proto_lib.manager import RabbitManager

from infrastructure.fastapi import FastAPIServer
from infrastructure.graphql import GraphQLConfiguration
from messaging.html_text_listener import HtmlTextListener
from messaging.plain_text_listener import PlainTextListener
from nlp.ned_analyser import NamedEntitiesAnalyser
from resolver.named_entities_resolver import NamedEntitiesResolver
from resources_manager import ResourcesManager

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d infunction %(funcName)s] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG
)


class NamedEntitiesService:
    logging.info(
        'Named Entities Service is starting with spaCy v' + spacy.__version__)
    spacy.prefer_gpu()

    ResourcesManager.print_banner()
    app_config = YamlConfig.load()
    text_analyser = NamedEntitiesAnalyser()

    # Web Server
    webserver = FastAPIServer(app_config['server'])

    # GraphQL
    named_entities_resolver = NamedEntitiesResolver(text_analyser)
    schema = GraphQLConfiguration(named_entities_resolver).schema()

    webserver.register_endpoint("/graphql",
                                GraphQL(schema, error_formatter=GraphQLConfiguration.dreipc_error_formatter))

    # RabbitMQ | Messaging
    rabbitmq = RabbitManager(app_config['rabbitmq'], app_name="named-entities-service")

    html_text_listener = HtmlTextListener(text_analyser)
    rabbitmq.register(html_text_listener)

    plain_text_listener = PlainTextListener(text_analyser)
    rabbitmq.register(plain_text_listener)

    # Web Server
    webserver.startup_event(rabbitmq.start)
    webserver.shutdown_event(rabbitmq.stop)
    # TODO: Remove mongodb
    # webserver.shutdown_event(mongodb.disconnect())
    webserver.start()
