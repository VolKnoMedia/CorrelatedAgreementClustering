import pytest
import config
from src.data.meta import Meta


@pytest.fixture
def meta():
    connector = {"host": config.host,
                "user":config.user,
                "password":config.password }
    id = 897
    return Meta(id, connector)

def test_id(meta):
    assert meta.id == 897

def test_genre(meta):
    assert meta.getGenre() == ['Action', 'Adventure', 'Comedy']

def test_falseId():
    connector = {"host": config.host,
                "user":config.user,
                "password":config.password }
    id = -1
    assert Meta(id, connector).getGenre() == []

def test_performance(meta):
    assert len(meta.getPerformance()[0]) == 6