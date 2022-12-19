import logging

from rabbitmq_proto_lib.listener import RabbitListener

from nlp.ned_analyser import NamedEntitiesAnalyser

from proto.dreipc.asset.document.namedentities import NamedEntitiesDetectionAction, ModelTypeProto, NamedEntityProto, \
    NamedEntitiesResultEventProto


class HtmlTextListener(RabbitListener):

    def __init__(
            self,
            ned_analyser: NamedEntitiesAnalyser,
    ):
        self.name = "entities.analyser"
        self.exchange_name = 'assets'
        self.routing_keys = ['entities.analyse.html']
        self.dead_letter_exchange = "assets-dlx"
        self.prefetch_count = 1
        self.ned_analyser = ned_analyser

    async def on_message(self, proto: NamedEntitiesDetectionAction, message):

        logging.info("Message Received")
        if isinstance(proto, str):
            return

        entities_protos: [NamedEntityProto] = []
        tags = []

        try:
            entities = self.ned_analyser.analyse_html(proto.content)
            for entity in entities:
                entity.source_id = proto.id
                entities_protos.append(entity.proto())

            if len(entities) == 0:
                raise ValueError('No entities found for following id: ', proto.id)

        except Exception as e:
            logging.error("Error during named entities detection: " + str(e))
            return 

        detection_result = NamedEntitiesResultEventProto(
            source_id=proto.id,
            model=proto.model,
            entities=entities_protos,
            tags=tags
        )
        await self.convert_and_send("entities.html.analysed", detection_result, self.exchange_name)
