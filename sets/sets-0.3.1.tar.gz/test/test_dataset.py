import pytest
import sets


@pytest.mark.skip
def test_semeval():
    dataset = sets.SemEvalRelation()
    dataset = sets.Tokenize()(dataset)
    dataset = sets.OneHot(dataset.target)(dataset, columns=['target'])
    dataset = sets.WordDistance('<e1>', '<e2>', depth=2)(
        dataset, column='data')
    dataset = sets.Glove(100, depth=2)(dataset, columns=['data'])
    dataset = sets.Concat(2, 'data')(
        dataset, columns=('data', 'word_distance'))


def test_ocr():
    dataset = sets.Ocr()
    dataset = sets.OneHot(dataset.target)(dataset, columns=['target'])
