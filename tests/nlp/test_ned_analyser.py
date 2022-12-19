import pytest

from nlp.ned_analyser import NamedEntitiesAnalyser


@pytest.fixture(scope='session')
def namedEntitiesAnalyser() -> NamedEntitiesAnalyser:
    return NamedEntitiesAnalyser()


def test_analyse_html(namedEntitiesAnalyser: NamedEntitiesAnalyser):
    html_text = "<div> Die ganze Stadt ist ein Startup: Shenzhen ist das Silicon Valley für Hardware-Firmen <div>"
    result = namedEntitiesAnalyser.analyse_html(html_text)
    assert not result == []


def test_analyse_plan_text(namedEntitiesAnalyser: NamedEntitiesAnalyser):
    text = "Die ganze Stadt ist ein Startup: Shenzhen ist das Silicon Valley für Hardware-Firmen"
    result = namedEntitiesAnalyser.analyse_text(text)
    assert not result == []
