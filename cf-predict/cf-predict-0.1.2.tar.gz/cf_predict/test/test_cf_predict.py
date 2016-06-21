"""Unit test cf_predict"""
import json
import pickle

import numpy as np
import pytest

from mockredis import MockRedis
from .conftest import models
from cf_predict import __version__
from cf_predict.resources import get_db
from cf_predict.errors import NoPredictMethod


@pytest.mark.usefixtures("client_class")
class TestCf_predict:
    def test_catalogue(self):
        rv = self.client.get("/")
        assert rv.status_code == 200
        assert rv.json == {
            "predict_url": "http://localhost/predict",
            "api_version": __version__
        }

    def test_get_db(self):
        r = get_db()
        r.set("test", 5)
        assert int(r.get("test")) == 5

    def test_no_model_in_db(self, monkeypatch, caplog):
        monkeypatch.setattr("cf_predict.resources.get_db", MockRedis)
        pytest.raises(ValueError, self.client.get, "/predict")
        assert "No model" in caplog.text()

    def test_model_pickle_error(self, monkeypatch, caplog):
        def broken_pickle(anything):
            raise IOError
        monkeypatch.setattr("pickle.loads", broken_pickle)
        pytest.raises(IOError, self.client.get, "/predict")
        assert "could not be unpickled" in caplog.text()

    def test_model_no_predict_error(self, monkeypatch, caplog, broken_model):
        monkeypatch.setattr("cf_predict.resources.get_db", broken_model)
        pytest.raises(NoPredictMethod, self.client.get, "/predict")
        assert "has no predict method" in caplog.text()

    def test_get_version(self):
        rv = self.client.get("/predict")
        assert rv.status_code == 200
        assert rv.json == {
            "model_version": "1.2.0"
        }

    def test_post_prediction_valid_features_one_record(self):
        features = {"features": [1, 2, 3, 4, 5]}
        model = pickle.loads(models().get("1.2.0"))
        rv = self.client.post("/predict",
                              data=json.dumps(features),
                              content_type="application/json")
        assert rv.status_code == 200
        assert rv.json == {
            "model_version": "1.2.0",
            "prediction": list(model.predict(np.array(features["features"]).reshape(1, -1)))
        }

    def test_post_prediction_valid_features_multiple_records(self):
        features = {"features": [[1, 2, 3, 4, 5],
                                 [6, 7, 8, 9, 1],
                                 [2, 3, 4, 5, 6]]}
        model = pickle.loads(models().get("1.2.0"))
        rv = self.client.post("/predict",
                              data=json.dumps(features),
                              content_type="application/json")
        assert rv.status_code == 200
        assert rv.json == {
            "model_version": "1.2.0",
            "prediction": list(model.predict(np.array(features["features"])))
        }

    def test_post_prediction_invalid_features(self):
        features = {"features": [1, 2, "lol", 4, 5]}
        rv = self.client.post("/predict",
                              data=json.dumps(features),
                              content_type="application/json")
        assert rv.status_code == 400
        assert rv.json == {
            "message": "Features [1, 2, 'lol', 4, 5] do not match expected input for model version 1.2.0"
        }

    def test_post_prediction_invalid_json(self):
        features = '{"features: [1, 2, 3, 4, 5]'
        rv = self.client.post("/predict",
                              data=features,
                              content_type="application/json")
        assert rv.status_code == 400
        assert rv.json == {
            "message": "Failed to decode JSON object: Unterminated string starting at: line 1 column 2 (char 1)"
        }

    def test_post_prediction_wrong_key(self):
        features = {"lol": [1, 2, 3, 4, 5]}
        rv = self.client.post("/predict",
                              data=json.dumps(features),
                              content_type="application/json")
        assert rv.status_code == 400
        assert rv.json == {
            "message": "Features not found in {'lol': [1, 2, 3, 4, 5]}"
        }
