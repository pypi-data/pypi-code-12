import sets


def ignore_test_semeval():
    dataset = sets.SemEvalRelation()()
    dataset = sets.Tokenize()(dataset)
    dataset = sets.OneHot(dataset.target, embed_target=True)(dataset)
    indices = sets.TagDistance('<e1>', '<e2>')(dataset)
    dataset = sets.Glove(100, embed_data=True)(dataset)
    dataset = sets.Concat(target_from=0)(indices, dataset)
    assert (dataset.data[:, :, :2] == indices.data[:, :]).all()
