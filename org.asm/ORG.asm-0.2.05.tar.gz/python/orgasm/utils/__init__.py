from ._progress import progressBar

def str2bytes(string):
    """
    Short cut to convert ascii encoded python string (str) to bytes 
    which can be easily converted to C-strings. 
    
        @param string: the python string to be converted.
        @type string: str
        @return a transcoded string
        @rtype: bytes 
    """
    return string.encode('ascii')

def bytes2str( string):
    """
    Short cut to convert bytes (C-strings) to ascii encoded python string (str).
    
        @param string: the binary (C-string) string to be converted.
        @type string: bytes
        @return an ascii transcoded string
        @rtype: str 
    """
    return string.decode('ascii')

def tags2str(taglist):
    return " ".join("%s=%s;" % tuple(v.split(':',1)) 
                    for v in taglist if ':' in v)

