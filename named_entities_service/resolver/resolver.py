from typing import List

'''
GraphQL Resolver Interface used for clean schema stiching
'''


class GraphQLResolver:

    def get_schemas(self) -> List:
        raise NotImplementedError("get_schemas is not implemented!")
