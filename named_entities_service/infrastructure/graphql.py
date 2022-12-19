import os
import sys

from ariadne import gql, format_error, snake_case_fallback_resolvers
from ariadne.contrib.federation import make_federated_schema
from graphql import GraphQLError

from resolver.named_entities_resolver import NamedEntitiesResolver
from resolver.resolver import GraphQLResolver


class GraphQLConfiguration:
    SCHEMA_FILE = os.path.join(sys.path[0], 'resources/schema.graphql')
    RESOLVERS = [snake_case_fallback_resolvers]

    def __init__(self, ne_service: NamedEntitiesResolver):
        self.add(ne_service)

    def add(self, resolver: GraphQLResolver):
        self.RESOLVERS.extend(resolver.get_schemas())

    def schema(self):
        with open(self.SCHEMA_FILE, 'r', encoding='utf-8') as schema_file:
            schema_content = schema_file.read()
            type_defs = gql(schema_content)
            # custom_directives = {'auth': AuthDirective, 'hasRole': HasRoleDirective}
            return make_federated_schema(type_defs, self.RESOLVERS)  # , directives=custom_directives)

    @staticmethod
    def dreipc_error_formatter(error: GraphQLError, debug: bool = False) -> dict:
        if debug:
            # If debug is enabled, reuse Ariadne's formatting logic (not required)
            return format_error(error, debug)
        # message = error.message
        # code = error.extensions['code']
        error = {"message": error.message}

        # Create formatted error data
        # formatted = error.formatted
        # Replace original error message with custom one
        # formatted["message"] = "INTERNAL SERVER ERROR"
        return error
