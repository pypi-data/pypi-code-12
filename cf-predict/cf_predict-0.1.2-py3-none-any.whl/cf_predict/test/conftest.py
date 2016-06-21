"""Unit tests configuration file."""
import pickle

import numpy as np
import pytest
from sklearn import linear_model, tree, svm
from mockredis import MockRedis

from cf_predict import create_app


def pytest_configure(config):
    """Disable verbose output when running tests."""
    terminal = config.pluginmanager.getplugin('terminal')
    base = terminal.TerminalReporter

    class QuietReporter(base):
        """A py.test reporting that only shows dots when running tests."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


def models():
    """Create some sample machine learning models."""
    rng = np.random.RandomState(42)
    X = rng.random_sample((20, 5))
    y = rng.random_sample(20)
    lm = linear_model.LinearRegression()
    dt = tree.DecisionTreeRegressor()
    svr = svm.SVR()
    lm.fit(X, y)
    dt.fit(X, y)
    svr.fit(X, y)
    r = MockRedis()
    r.set("1.0.0", pickle.dumps(lm))
    r.set("1.1.0", pickle.dumps(dt))
    r.set("1.2.0", pickle.dumps(svr))
    return r


@pytest.fixture
def broken_model():
    """Create a non-functional model object."""
    r = MockRedis()
    r.set("1.2.0", pickle.dumps("lol"))
    return lambda: r


@pytest.fixture
def app(monkeypatch):
    """Create a Flask test client."""
    monkeypatch.setattr("cf_predict.resources.get_db", models)
    app = create_app("unit_testing")
    return app
