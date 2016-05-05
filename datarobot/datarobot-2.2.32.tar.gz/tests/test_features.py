import json
import responses
from datarobot import Feature, Project

data = {
    'id': 34,
    'name': 'Claim_Amount',
    'featureType': 'Numeric',
    'importance': 1,
    'lowInformation': False,
    'uniqueCount': 200,
    'naCount': 0,
}


@responses.activate
def test_features(client):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/',
                  body=json.dumps([data]))
    feature, = Project({'id': 'p-id'}).get_features()
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == 'Claim_Amount'
    assert feature.feature_type == 'Numeric'
    assert feature.importance == 1
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0


@responses.activate
def test_feature(client):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/f-id/',
                  body=json.dumps(dict(data, importance=None)))
    feature = Feature.get('p-id', 'f-id')
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == 'Claim_Amount'
    assert feature.feature_type == 'Numeric'
    assert feature.importance is None
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0
