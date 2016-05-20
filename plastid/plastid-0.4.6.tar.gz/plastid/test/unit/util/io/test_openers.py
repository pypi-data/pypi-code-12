#!/usr/bin/env python
from plastid.util.io.openers import (get_short_name, pretty_print_dict, multiopen)
from nose.tools import assert_equal
        
# def test_multiopen():
#     fh1 = 
#     fh2 = 
#     tests = [
#         # normalize string to list of strings
#         ("start_str","some_file.txt",["some_file.txt"],None,{}),
#         
#         # leave list of strings alone
#         ("start_list_str",["file_1.txt","file_2.txt"],["file_1.txt","file_2.txt"],None,{})
#         
#         # apply function to string
#         ("func_str","",[],None,{})
#         
#         # apply function to list of strings
#         ("func_list_str",[],[],None,{})
# 
#         # apply function to list of with kwargs
#         ("func_list_kwargs",[],[],None,{})
#         
#         # convert single open filehandle to list of filehandles
#         ("start_fh",,[],None,{}),
#         
#         # leave list of open filehandles alone
#         ("start_list_fh",,[],None,{}),
# 
#         # leave list of open filehandles alone, with func given
#         ("func_list_fh",,[],None,{}),
#          ]
#     for name, inp, expected, fn, kwargs in tests:
#         found = multiopen(inp,fn,**kwargs)
#         msg = "test_multiopen failed test '%s'" % name
#         assert_equal(expected,found,msg)
# 
#     fh1.close()
#     fh2.close()
    
def test_get_short_name():
    tests = [("test","test",{}),
             ("test.py","test",dict(terminator=".py")),
             ("/home/jdoe/test.py","test",dict(terminator=".py")),
             ("/home/jdoe/test.py.py","test.py",dict(terminator=".py")),
             ("/home/jdoe/test.py.2","test.py.2",{}),
             ("/home/jdoe/test.py.2","test.py.2",dict(terminator=".py")),
             ("plastid.bin.test","test",dict(separator="\.",terminator=""))
             ]
    for inp, expected, kwargs in tests:
        found = get_short_name(inp,**kwargs)
        msg = "test_get_short_name(): failed on input '%s'. Expected '%s'. Got '%s'" % (inp,expected,found)
        yield assert_equal, expected, found, msg

    
def test_pretty_print_dict():
    dtmp = { "a" : 1,
             "b" : 2.3,
             "c" : "some string",
             "d" : "some string with 'subquotes' inside",
             "e" : (3,4,5),
             "somereallyreallylongname" : "short val",
            }
    expected = """{
          'a'                        : 1,
          'b'                        : 2.3,
          'c'                        : 'some string',
          'd'                        : 'some string with 'subquotes' inside',
          'e'                        : (3, 4, 5),
          'somereallyreallylongname' : 'short val',
}
"""
    found = pretty_print_dict(dtmp)
    assert_equal(expected,found,"Dictionary did not pretty-print!\nExpected:\n%s\n\nFound:\n%s\n\n" % (expected,found)) 