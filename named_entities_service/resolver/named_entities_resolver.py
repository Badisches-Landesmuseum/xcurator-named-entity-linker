import logging
from typing import List

from ariadne import QueryType
from ariadne import ScalarType
from ariadne.contrib.federation import FederatedObjectType

from nlp.ned_analyser import NamedEntitiesAnalyser
from resolver.resolver import GraphQLResolver


class NamedEntitiesResolver(GraphQLResolver):
    entity_type = FederatedObjectType("NamedEntity")
    document_type = FederatedObjectType("Document")
    page_type = FederatedObjectType("Page")
    entities_query = QueryType()
    datetime_scalar = ScalarType("DateTime")

    @datetime_scalar.serializer
    def serialize_datetime(value):
        return value.isoformat()

    service = None

    def __init__(self, _service: NamedEntitiesAnalyser):
        super(NamedEntitiesResolver, self).__init__()
        NamedEntitiesResolver.service = _service

    @entities_query.field('entities')
    def detect_entities(self, info, **kwargs):
        print('graphql received')
        text = kwargs.get("text")
        # html_text = unicode(text, "utf8")
        named_entities = NamedEntitiesResolver.service.analyse_html(text)

        return named_entities

    def get_schemas(self) -> List:
        return [
            self.entity_type,
            self.datetime_scalar,
            self.entities_query,
        ]
