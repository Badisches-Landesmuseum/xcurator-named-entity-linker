from betterproto import Message

from publisher import RabbitPublisher


class TestProtoPublisher(RabbitPublisher):

    async def publish(self, message: Message):
        try:
            await self.convert_and_send('image.created.proto', message, 'assets')
        except Exception as e:
            print(e)
