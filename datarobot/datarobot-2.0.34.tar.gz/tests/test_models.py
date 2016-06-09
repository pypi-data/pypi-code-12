# -*- encoding: utf-8 -*-
import json

import responses
import mock

from datarobot import Project, Model, Featurelist, Blueprint
from datarobot.errors import AppPlatformError
from .utils import SDKTestcase


class ModelTestCase(SDKTestcase):

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.model_data = {
            'id': 'l-id',
            'project_id': 'p-id',
            'blueprint_id': 'b_id',
            'featurelist_id': 'd-id',
            'model_type': 'Reg Name'
        }

    @classmethod
    def setUpClass(cls):
        super(ModelTestCase, cls).setUpClass()
        cls.project = Project('p-id')

    def test_instantiation(self):
        """
        Test Model instanctiation
        """
        l_item = Model(('p-id', 'l-id'))
        self.assertIsInstance(l_item.project, Project)
        self.assertEqual(l_item.project.id, 'p-id')
        self.assertEqual(l_item.id, 'l-id')
        with self.assertRaises(ValueError):
            Model(['list'])

    @responses.activate
    def test_model_item_get(self):
        """
        Test Model.get(project_instance, 'l-id')
        """
        raw = """
{
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "556cdfbb100d2b0e88585195",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9657"
}
        """

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/l-id/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        l_item = Model.get(self.project, 'l-id')
        self.assertIsInstance(l_item, Model)
        self.assertIsInstance(l_item.project, Project)
        self.assertIsInstance(l_item.featurelist, Featurelist)
        self.assertIsInstance(l_item.blueprint, Blueprint)

        self.assertEqual(l_item.project.id, self.project.id)
        self.assertEqual(l_item.featurelist.id, '556cdfbd100d2b10048c7941')
        self.assertEqual(l_item.featurelist.name, 'Informative Features')

        self.assertEqual(l_item.blueprint.id,
                         'a4fd9d17a8ca62ee00590dd704dae6a8')
        self.assertEqual(l_item.sample_pct, 64)
        self.assertIsInstance(l_item.metrics, dict)
        self.assertEqual(
            set(l_item.metrics.keys()),
            {
                u'AUC', u'FVE Binomial', u'Gini Norm', u'LogLoss', u'RMSE',
                u'Rate@Top10%', u'Rate@Top5%', u'Rate@TopTenth%'
            }
        )
        self.assertEqual(l_item.processes, ['One', 'Two', 'Three'])
        self.assertEqual(l_item.blueprint.processes, ['One', 'Two', 'Three'])

    @responses.activate
    def test_model_item_get_with_project_id(self):
        """
        Test Model.get('p-id', 'l-id')
        """
        raw = """
        {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "l-id"
}
        """

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/l-id/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        l_item = Model.get('p-id', 'l-id')
        self.assertIsInstance(l_item, Model)
        self.assertEqual(l_item.featurelist.id, '556cdfbd100d2b10048c7941')
        self.assertEqual(l_item.project.id, 'p-id')

        with self.assertRaises(ValueError):
            Model.get(['list'], 'l-id')

    @responses.activate
    def test_model_features(self):
        """
        Test get names of features used in model
        Model('p-id', 'l-id').get_features_used()
        """
        body = json.dumps(
            {'featureNames': ['apple', 'banana', 'cherry']}
        )

        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/l-id/features/',
            body=body,
            status=200)

        l_item = Model(('p-id', 'l-id'))
        result = l_item.get_features_used()
        self.assertEquals(responses.calls[0].request.method, 'GET')
        self.assertEqual(result, ['apple', 'banana', 'cherry'])

    @responses.activate
    def test_model_features_invalid_model_id(self):
        """
        Test get names of features used in model.

        If an invalid model id is used, the server will return a 404
        """
        body = json.dumps(
            {'Error': 'This resource does not exist.'}
        )

        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/l-id/features/',
            body=body,
            status=404)

        l_item = Model(('p-id', 'l-id'))
        with self.assertRaises(AppPlatformError):
            l_item.get_features_used()
        self.assertEquals(responses.calls[0].request.method, 'GET')

    @responses.activate
    def test_model_delete(self):
        """
        Test delete model
        Model('p-id', 'l-id').delete()
        """
        responses.add(responses.DELETE,
                      'https://host_name.com/projects/p-id/models/l-id/',
                      status=204)

        l_item = Model(('p-id', 'l-id'))
        del_result = l_item.delete()
        self.assertEquals(responses.calls[0].request.method, 'DELETE')
        self.assertIsNone(del_result)

    @responses.activate
    def test_train_model(self):
        """
        Model((p-id, l-id)).train()
        """
        m = Model(self.model_data)
        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            adding_headers={
                'Location': 'https://host_name.com/projects/p-id/models/1'},
            body='',
            status=201
        )
        m.train()
        req_body = json.loads(responses.calls[0].request.body)
        self.assertEqual(req_body['blueprintId'], 'b_id')
        self.assertEqual(req_body['featurelistId'], 'd-id')
        self.assertEqual(req_body['samplePct'], 100)

    def test_get_permalink_for_model(self):
        """
        Model(('p-id', 'l-id')).get_leaderboard_ui_permalink()
        """
        m = Model(self.model_data)
        expected_link = 'https://host_name.com/projects/p-id/models/l-id'
        self.assertEqual(m.get_leaderboard_ui_permalink(), expected_link)

    @mock.patch('webbrowser.open')
    def test_open_model_browser(self, webbrowser_open):
        m = Model(self.model_data)
        m.open_model_browser()
        self.assertTrue(webbrowser_open.called)
