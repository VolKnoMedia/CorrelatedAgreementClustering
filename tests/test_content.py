import pytest
import config
from src.data.content import Content
import datetime
import collections
from typing import OrderedDict


@pytest.fixture
def content():
    connector = {"host": config.host,
                "user":config.user,
                "password":config.password }
    id = 800
    return Content(id, connector)

def test_title(content):
    assert content.title == 'Chaos Walking'

def test_scenes(content):
    assert type(content.getScenes()) is collections.OrderedDict

def test_getIdx(content):
    c = content.getScenes()
    assert type(content.getSceneIdx(4.5)) is int

def test_date(content):
    assert type(content.date_added) is datetime.datetime


