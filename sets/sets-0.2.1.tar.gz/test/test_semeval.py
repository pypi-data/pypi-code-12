import numpy as np
import sets


def test_semeval():
    dataset = sets.SemEvalRelation()()
    dataset = sets.Tokenize()(dataset)
    dataset = sets.OneHot(dataset.target, embed_target=True)(dataset)
    indices = sets.RelativeIndices('<e1>', '<e2>')(dataset)
    dataset = sets.Glove(100, embed_data=True)(dataset)
    dataset = sets.Concat(targets_from=0)(indices, dataset)
    assert np.allclose(dataset.data[:, :, :2], indices.data[:, :])
