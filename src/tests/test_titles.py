import pytest
import config
from src.data.titles import Titles



@pytest.fixture
def titles():
    connector = {"host": config.host,
                "user":config.user,
                "password":config.password }
    return Titles(connector,"movie")


def test_titlelist(titles):
    assert type(titles.titles) is list

def test_responses(titles):
    titles.titles = [500, 600]
    titles.getResponses()
    assert type(titles.content) is dict

def test_responsesID(titles):
    titles.titles = [500, 600]
    titles.getResponses()
    assert titles.content[500].id == 500

def test_responsesID(titles):
    titles.titles = [500, 600]
    titles.getResponses()
    titles.content[500].getScenes()
    assert type(titles.content[500].getResults()) is list