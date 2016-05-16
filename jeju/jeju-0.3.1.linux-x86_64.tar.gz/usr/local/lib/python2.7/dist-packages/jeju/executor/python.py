###########################################
# This is very naive replacement algorithm
# TODO
############################################
import string
import uuid

# TODO: configurable variable
TEMP_DIR = "/tmp"

def replaceable(code, kv):
    # change keyword to value
    keys = kv.keys()
    # find keyword which is ${keyword}
    # replace value ${keyword} <- kv[keyword]
    for key in keys:
        nkey = "${%s}" % key
        code = string.replace(code, nkey, kv[key])
    print '#' * 40
    print code
    print '#' * 40
    return code

def execute_python(**kwargs):
    code = kwargs['code']
    kv = kwargs['kv']

    import os
    # call replaceable
    rcode = replaceable(code, kv)

    temp = uuid.uuid1()
    temp_file = "%s/%s" % (TEMP_DIR, str(temp))

    fp = open(temp_file, 'w')
    fp.write(rcode)
    fp.close()
    os.system("python %s" % temp_file)
    os.remove(temp_file)
    return "Bash executed"

