from datarobot import Blueprint
from .utils import SDKTestcase


class TestBlueprintModel(SDKTestcase):

    def setUp(self):
        super(TestBlueprintModel, self).setUp()

    def test_instantiation(self):
        model_data = {
            'modelType': 'RandomForest Regressor',
            'processes': ['Missing values imputed'],
            'projectId': '5223deadbeefdeadbeef1234',
            'id': 'e1c7fc29ba2e612a72272324b8a842af'
        }
        bp = Blueprint(model_data)

        self.assertEqual(bp.model_type, 'RandomForest Regressor')
        self.assertEqual(bp.processes, ['Missing values imputed'])
        self.assertEqual(bp.project_id, '5223deadbeefdeadbeef1234')
        self.assertEqual(bp.id, 'e1c7fc29ba2e612a72272324b8a842af')

    def test_instantiation_with_bad_data_raises_error(self):
        model_data = 4
        with self.assertRaises(ValueError):
            Blueprint(model_data)
