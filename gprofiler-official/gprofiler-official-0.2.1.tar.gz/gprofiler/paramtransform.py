
import copy
import re

class ParamTransformer:

    """
    An auxiliary class for mapping between parameter spaces. Likely not of interest 
    for users wishing to integrate g:Profiler queries into their codebase, but possibly 
    useful in other contexts.
    """

    TF_LIST         = 1
    TF_FILE         = 2
    TF_BOOL         = 3
    TF_SRCFILTER    = 4
    TF_MAP          = 5

    def __init__(self):
        pass

    def transform(self, in_params, transform_map, passthrough=False):
        
        """
        Takes a dict of input parameters (``in_params``) and maps them to
        the output parameter space using a transformation map
        (``transform_map``). The transformation map's keys are input parameter
        names. The value is either:
        
        * a string, then keep argument value, but transform argument name
        * a list specifying a built-in transformation for the argument. The
          first element of the list must be one of the ``TF_*`` constants, the
          rest are arguments to the specified transformer.
        * a function, then it is expected to return either
        
          - a list containing the output argument name-value pair
          - a list of lists containing such pairs
          
        If ``passthrough`` is true, all ``in_params`` entries without a
        transformation are passed to the output verbatim.       
        """
        
        out_params = {}

        if (passthrough):
            out_params = copy.deepcopy(in_params)

        for in_param, v in transform_map.iteritems():

            # Skip nonexistent parameters

            if (\
                in_params[in_param] is None \
                or (type(in_params[in_param]) is list and len(in_params[in_param]) == 0) \
            ):
                continue

            # Transform parameters, map entry is a string: only
            # transform the name

            if (type(v) is str):
                out_params[v] = in_params[in_param]

            # Transform parameters, map entry either a provided
            # transformation function (list) or a custom function

            else:
                if (type(v) is list):
                    tf_method_id = v[0]
                    out_param = v[1]
                    tf_method = self._get_tf_method(tf_method_id)
                    r = tf_method(*([in_params, in_param, out_param] + v[2:]))
                elif (hasattr(v, "__call__")):
                    r = v(in_params, in_param)

                if (type(r) is list and type(r[0]) is list):
                    for to_arg in r:
                        out_params[to_arg[0]] = to_arg[1]
                elif (type(r) is list):
                    out_params[r[0]] = r[1]

        return out_params

    def _get_tf_method(self, tfid):
        if (tfid == self.TF_LIST):
            return self._transform_list
        elif (tfid == self.TF_FILE):
            return self._transform_file
        elif (tfid == self.TF_BOOL):
            return self._transform_boolean
        elif (tfid == self.TF_SRCFILTER):
            return self._transform_srcfilter
        elif (tfid == self.TF_MAP):
            return self._transform_map
        raise KeyError("No transformation with ID " + str(tfid) + " found")

    def _transform_list(self, args, from_arg, to_arg):
        
        """
        Transforms a list to a string or passes a string through verbatim.
        """
        
        in_arg = args[from_arg]
        out_arg = None

        if (type(in_arg) is str):
            out_arg = in_arg
        else:
            out_arg = " ".join(in_arg)
        return [to_arg, out_arg]

    def _transform_file(self, args, from_arg, to_arg):
        
        """
        Opens a file, reads its contents and saves it as a string.
        """
        
        return [to_arg, re.sub(r"\s+", " ", open(args[from_arg], "r").read())]

    def _transform_boolean(self, args, from_arg, to_arg, *extra):
        
        """
        Transforms a boolean into a string. If the extra argument is true,
        returns "0" for a true value and "1" for a false value.
        """
        
        trueval = "1"
        falseval = "0"

        if (len(extra) and extra[0]): # reverse boolean interpretation
            trueval = "0"
            falseval = "1"
        return [to_arg, trueval if args[from_arg] else falseval]

    def _transform_map(self, args, from_arg, to_arg, *extra):
        
        """
        Transforms values of the input to values of the output according to
        a dict passed as the extra argument
        """
        
        tmap = extra[0]

        if (type(tmap) is not dict):
            raise TypeError("_transform_map requires a dict as the extra argument")
        return [to_arg, tmap[args[from_arg]]]

    def _transform_srcfilter(self, args, from_arg, to_arg, *extra):
        
        """
        Transforms a list or space-separated string of source IDs to HTTP
        parameters expected by g:Profiler
        """
        
        r = []
        source_ids = args[from_arg]

        if (type(source_ids) is list):
            source_ids = " ".join(source_ids)
        if (source_ids == ""):
            return None

        for src in re.split(r"\s+", source_ids.strip()):
            r.append(["sf_" + src, "1"])
        return r
