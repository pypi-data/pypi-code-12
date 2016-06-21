import pickle
import os
import numpy as np
from flask_restful import Resource, request
from flask import url_for, current_app
from .errors import NoPredictMethod
import cf_predict


def get_db():
    """Fetch Redis client."""
    return current_app.extensions["redis"]


class Catalogue(Resource):
    def get(self):
        """Show a catalogue of available endpoints."""
        return {
            "predict_url": url_for("api.predict", _external=True),
            "api_version": cf_predict.__version__
        }


class Predict(Resource):
    def __init__(self):
        self.r = get_db()
        self.version = os.getenv("MODEL_VERSION") or "latest"
        if self.version == "latest":
            try:
                self.version = self.find_latest_version(self.version)
                self.model = self.load_model(self.version)
            except (TypeError, ValueError) as e:
                current_app.logger.error("No model {} found".format(self.version))
                raise e
            except (pickle.UnpicklingError, IOError, AttributeError, EOFError, ImportError, IndexError) as e:
                current_app.logger.error("Model {} could not be unpickled".format(self.version))
                raise e
            if not hasattr(self.model, 'predict'):
                current_app.logger.error("Model {} has no predict method".format(self.version))
                raise NoPredictMethod

    def find_latest_version(self, version):
        """Find model with the highest version number in Redis."""
        keys = [key.decode("utf-8") for key in self.r.scan_iter()]
        latest_version = max(keys)
        return latest_version

    def load_model(self, version):
        """Deserialize and load model."""
        return pickle.loads(self.r.get(version))

    def get(self):
        """Get current model version."""
        return {"model_version": self.version}

    def post(self):
        """Get prediction from model.

        Input: Feature array
        """
        try:
            raw_features = request.get_json()["features"]
            features = np.array(raw_features)
            if len(features.shape) == 1:
                features.reshape(1, -1)
            prediction = self.model.predict(features)
            return {
                "model_version": self.version,
                "prediction": list(prediction)
            }
        except KeyError:
            return {"message": "Features not found in {}".format(request.get_json())}, 400
        except ValueError:
            return {"message": "Features {} do not match expected input for model version {}".format(raw_features, self.version)}, 400
