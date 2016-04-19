def tagger(*tags):

    def running_test_case(*args):
        test_method = args[0]
        test_method.tags = list(tags)
        return test_method

    return running_test_case
