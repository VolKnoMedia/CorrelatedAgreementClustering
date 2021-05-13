import pytest
import config

from src.data import db 


@pytest.fixture
def dbItem():
    return db.DB(config.host, config.user, config.password)


def test_wrongType():
    with pytest.raises(Exception):
        aa = db.DB(1, 2, 3)

def test_wrongInfo():
    host = config.host
    user = ""
    password = ""
    with pytest.raises(Exception):
        aa = db.DB(host, user, password)

def test_CorrectInfo():

    aa = db.DB(config.host, config.user, config.password) 
    assert True

def test_run(dbItem):
    assert  dbItem.run(f"""SHOW tables""") != None 

def test_Incorrect(dbItem):
    with pytest.raises(Exception):
        dbItem.run(f"""fdsakj""") 