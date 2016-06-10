import pyhacrf
from pyhacrf import Hacrf, StringPairFeatureExtractor
from pyhacrf.state_machine import DefaultStateMachine
from pyhacrf.adjacent import forward_predict

import numpy as np

class CRFEditDistance(object) :
    def __init__(self) :
        classes = ['match', 'non-match']
        self.model = Hacrf(l2_regularization=100.0,
                           state_machine=DefaultStateMachine(classes))
        self.model.parameters = np.array(
            [[-0.29211509,  0.57502347], # m 
             [ 0.0116871,  -0.13680756],
             [-0.02586914,  0.16491335], # m match
             [ 0.01418205, -0.0184858 ],
             [ 0.11116342,  0.1672951 ], # m delete
             [-0.09947633, -0.02090108],
             [-0.01060069,  0.18925586], # m insert
             [ 0.02228778, -0.04386152]],
            order='F')
        self.parameters = self.model.parameters.T
        self.model.classes = ['match', 'non-match']

        self.feature_extractor = StringPairFeatureExtractor(match=True,
                                                            numeric=False)


        
    def fast_pair(self, x):
        x_dot_parameters = np.inner(x, self.parameters)

        probs = forward_predict(x_dot_parameters, 2)

        return probs


    def train(self, examples, labels) :
        examples = [(string_2, string_1) 
                    if len(string_1) > len(string_2)
                    else (string_1, string_2)
                    for string_1, string_2
                    in examples]
        print(examples)
        extracted_examples = self.feature_extractor.fit_transform(examples)
        self.model.fit(extracted_examples, labels, verbosity=1)

    def __call__(self, string_1, string_2) :
        if len(string_1) > len(string_2) :
            string_1, string_2 = string_2, string_1
        array1 = np.array(tuple(string_1)).reshape(-1, 1)
        array2 = np.array(tuple(string_2)).reshape(1, -1)
        features = self.feature_extractor._extract_features(array1, array2)
        return self.fast_pair(features)[1]
