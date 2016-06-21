import os

from fennec import Workspace


def pytest_generate_tests(metafunc):
    if "valid_names" in metafunc.funcargnames:
        metafunc.parametrize("valid_names", [
            ["sample", "", "sample"],
            ["category/sample", "category", "sample"],
            ["nested/category/sample", "nested/category", "sample"],
            ["/sample", "/", "sample"],
            ["category/", "category", "experiment"],
        ])


def pytest_funcarg__workspace(request):
    return Workspace("category/sample")


def test_valid_name(valid_names):
    w = Workspace(valid_names[0])
    assert w.category == valid_names[1] and w.name == valid_names[2]


def test_logfile_naming(workspace):
    workspace.log("hello world")
    assert os.path.exists(workspace("result.log"))
