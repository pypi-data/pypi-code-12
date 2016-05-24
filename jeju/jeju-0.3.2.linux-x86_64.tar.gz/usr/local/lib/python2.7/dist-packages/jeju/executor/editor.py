import string
import ConfigParser
import io
import logging

def replaceable(code, kv):
    # change keyword to value
    keys = kv.keys()
    # find keyword which is ${keyword}
    # replace value ${keyword} <- kv[keyword]
    for key in keys:
        nkey = "${%s}" % key
        code = string.replace(code, nkey, kv[key])
    logging.debug("#" * 20 + "\n%s" % code)
    logging.debug("#" * 20)
 
    return code


def find_file_path(lookahead):
    if lookahead == None:
        return None
    ctx = lookahead['text']
    items = ctx.split()
    if items[0] == 'edit':
        return items[1]


def editor_text(**kwargs):
    lookahead = kwargs['lookahead']
    code = kwargs['code']
    kv = kwargs['kv']

    file_path = find_file_path(kwargs['lookahead'])
    if file_path == None:
        msg = "Cannot find content:%s" % lookahead['text']
        logging.error(msg)
        return msg
    fp = open(file_path, 'w')
    rcode = replaceable(code, kv)
    fp.write(rcode)
    fp.close()
    return {'output': rcode}

##############################
# INI editor
#
# INI format (example)
# 
# [section1]
# key1 = value1
# key2 = value2
# [section2]
# key3 = value3
# 
##############################
def editor_ini(**kwargs):
    lookahead = kwargs['lookahead']
    code = kwargs['code']
    kv = kwargs['kv']

    added = ConfigParser.RawConfigParser(allow_no_value=True)
    rcode = replaceable(code, kv)
    added.readfp(io.BytesIO(rcode))

    file_path = find_file_path(kwargs['lookahead'])
    if file_path == None:
        msg = "Cannot find content path: %s" % lookahead['text']
        logging.error(msg)
        return msg
    orig = ConfigParser.ConfigParser()
    orig.readfp(open(file_path))

    for section in added.sections():
        # There is no section
        if orig.has_section(section) == False:
            msg = "Add new section"
            logging.debug(msg)
            orig.add_section(section)
        # Add item = value in section
        for (item,value) in added.items(section):
            if item == "...":
                msg = "abbreviation"
            else:
                orig.set(section, item, value)

    # Write to file
    fp = open(file_path, 'w')
    orig.write(fp)
    new_content = orig.read()
    fp.close()
    return {'output': new_content}
