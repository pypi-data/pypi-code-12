def test_pl():
    'test_pl'.pl()

def test_ppl():
    'test_ppl'.ppl()

def test_flag_test():
    flag_test()

if __name__ == '__main__':
    import sys
    print("sys.version_info:")
    print(sys.version_info)
    # import the minitest
    from minitest import *

    import operator

    # declare a variable for test
    tself = get_test_self()
    # you could put all your test variables on tself
    # just like declare your variables on setup.
    tself.jc = "jc"

    # declare a test
    with test(object.must_equal):
        tself.jc.must_equal('jc')
        None.must_equal(None)

    with test(object.must_true):
        True.must_true()
        1/0
        False.must_true()

    with test(object.must_false):
        True.must_false()
        False.must_false()

    # using a funcation to test equal.
    with test("object.must_equal_with_func"):
        (1).must_equal(1, key=operator.eq)
        (1).must_equal(2, key=operator.eq)

    def div_zero():
        1/0
        
    # test excecption
    with test("test must_raise"):
        if sys.version_info < (3, 0):
            error_msg = "integer division or modulo by zero"
        else:
            error_msg = "division by zero"

        (lambda : div_zero()).must_raise(ZeroDivisionError)
        (lambda : div_zero()).must_raise(ZeroDivisionError, error_msg)
        (lambda : div_zero()).must_raise(ZeroDivisionError, "in")

    # customize your must method 
    with test("inject"):
        def close_one(int1, int2):
            return int1 == int2+1 or int2 == int1+1
        (1).must_equal(2, close_one)
        inject(close_one)
        (1).must_close_one(2)
        inject_customized_must_method(close_one, 'must_close')
        (1).must_close(2)

        # import numpy
        # inject(numpy.allclose, 'must_close')
        # numpy.array([1]).must_close(numpy.array([1.0]))

    with test("test_pl"):
        test_pl()

    with test("test_ppl"):
        test_ppl()

    with test(flag_test):
        import sub_test_module
        sub_test_module.test_flag_test()
        flag_test("for test")

    with test("with failure_msg"):
        the_number = 10
        (the_number % 2).must_equal(1, 
            failure_msg="{0} is the number".format(the_number))
        # it wont show the failure_msg
        (the_number % 2).must_equal(0, 
            failure_msg="{0} is the number".format(the_number))

        (True).must_false(
            failure_msg="{0} is the number".format(the_number))

        (lambda : div_zero()).must_raise(ZeroDivisionError, "in",
            failure_msg="{0} is the number".format(the_number))

    with test("format functions"):
        foo = {'name': 'foo'}
        foo.p_format().must_equal("foo : {'name': 'foo'}")
        foo.pp_format().must_equal("foo :\n{'name': 'foo'}")
        # foo.pl_format().must_equal(
        #     'line info: File "/Users/colin/work/minitest/minitest/with_test.py", line 254, in <module>:\n'+
        #     'foo :\n{\'name\': \'foo\', \'value\': \'bar\'}')
        # foo.ppl_format().must_equal(
        #     'line info: File "/Users/colin/work/minitest/minitest/with_test.py", line 257, in <module>:\n'+
        #     'foo :\n{\'name\': \'foo\', \'value\': \'bar\'}')

    def print_msg_twice(msg):
        print(msg)
        print(msg)
        return msg
        
    with test("capture_output"):
        with capture_output() as output:
            result = print_msg_twice("foobar")
        result.must_equal("foobar")
        output.must_equal(["foobar","foobar"])

    with test("must output"):
        (lambda : print_msg_twice("foobar")).must_output(
                ["foobar","foobar"])
        (lambda : print_msg_twice("foobar")).must_output(
                ["foobar","wrong"])

    value = "Minitest"
    value.p()
    value.p("It is a value:")
    value.p(auto_get_title=False)

    value.pp()
    value.pp("It is a value:")
    value.pp(auto_get_title=False)

    value.pl()
    value.pl("It is a value:")
    value.pl(auto_get_title=False)

    value.ppl()
    value.ppl("It is a value:")
    value.ppl(auto_get_title=False)


    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # foo=dict(name="foo", value="bar")
    # logging.info(foo.p_format())
    # logging.info(foo.pp_format())
    # logging.info(foo.pl_format())
    # logging.info(foo.ppl_format())

    [1, 2].length().pp()
    (1, 2).size().pp()

    # python 2:
    # 13 tests, 23 assertions, 7 failures, 2 errors.
    # python 3:
