import aiormq
import pytest

from messaging.html_text_listener import HtmlTextListener
from models.ned_analyser_interface import NamedEntitiesAnalyserInterface
from proto.dreipc.asset.document.namedentities import NamedEntitiesDetectionAction, ModelTypeProto


@pytest.fixture
def example_detection_proto() -> NamedEntitiesDetectionAction:
    return NamedEntitiesDetectionAction(
        id="43refdsd",
        content="<h1>Jella Haase ist eine deutsche Schauspielerin<h1>",
        model=ModelTypeProto.GENERAL
    )


@pytest.fixture()
def rabbitmq_config():
    return {
        "username": "dreipc",
        "password": "secret",
        "host": "localhost",
        "port": 5672,
        "vhost": "/"
    }


@pytest.fixture
def text_listener() -> HtmlTextListener:
    stub = NamedEntitiesAnalyserInterface()
    return HtmlTextListener(stub, stub)


@pytest.fixture()
def message_properties() -> aiormq.spec.Basic.Properties:
    properties = aiormq.spec.Basic.Properties()
    properties.expiration = 10
    return properties


@pytest.mark.asyncio
async def test_on_message(text_listener, example_detection_proto, message_properties):
    text_listener.add_message_converters({"application/protobuf":None})
    text_listener.s
    await text_listener.on_message(example_detection_proto, [])
    assert 2 == 2
