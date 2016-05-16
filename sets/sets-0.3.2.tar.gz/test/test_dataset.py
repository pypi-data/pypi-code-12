import sets
import pytest


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


@pytest.mark.skip
def test_ocr():
    dataset = sets.Ocr()
    dataset = sets.OneHot(dataset.target, depth=2)(dataset, columns=['target'])


def test_wikipedia():
    url = 'https://dumps.wikimedia.org/enwiki/20160501/' \
          'enwiki-20160501-pages-meta-current1.xml-p000000010p000030303.bz2'
    dataset = sets.Wikipedia(url, 100)
