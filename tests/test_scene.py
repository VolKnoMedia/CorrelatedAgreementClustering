import pytest
from src.filtering.scene import SceneHueristic
from src.data.content import Content
import numpy as np
import config



@pytest.fixture
def scene():
    connector = {"host": config.host,
                "user":config.user,
                "password":config.password }
    id = 800
    c = Content(id, connector)
    c.getScenes()
    results = c.getResults()
    return SceneHueristic(results)


def test_probs(scene):
    responses = scene.getProb()
    for k in responses:
        for x in k:
            if x > 1:
                pytest.fail("Probability error")
    assert True


def test_variances(scene):
    responses = scene.getStandardVariances()
    assert True

def test_maxVariance(scene):
    responses = scene.getMaxVariances()
    for ix, i in enumerate(responses):
        if ix == 0:
            pass
        elif i[1] > responses[ix - 1][1]:
            pytest.fail("Variances are not sorted")

            
def test_top(scene):
    n = 5
    responses = scene.getTopScenes(n)
    assert len(responses) == n

def test_topTooMany(scene):
    n = 200
    responses = scene.getTopScenes(n)
    assert len(responses) == 34


