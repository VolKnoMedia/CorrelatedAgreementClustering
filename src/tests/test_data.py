import pytest
import config

from src.data.db import DB 


@pytest.fixture
def dbItem():
    return DB(config.host, config.user, config.password)


def test_wrongType():
    with pytest.raises(Exception):
        aa = DB(1, 2, 3)

def test_wrongInfo():
    host = config.host
    user = ""
    password = ""
    with pytest.raises(Exception):
        aa = DB(host, user, password)

def test_CorrectInfo():

    aa = DB(config.host, config.user, config.password) 
    assert True

def test_run(dbItem):
    assert  dbItem.run(f"""SHOW tables""") != None 

def test_Incorrect(dbItem):
    with pytest.raises(Exception):
        dbItem.run(f"""fdsakj""") 