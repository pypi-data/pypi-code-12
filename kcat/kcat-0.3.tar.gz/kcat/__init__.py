# -*- coding: utf-8 -*-

import sys
import os
import re
import operator as op

import getopt


VERSION = '0.3'


EXIT_OK = 0
EXIT_UNKNOW_OPT = 1
EXIT_KB_INT = 130
EXIT_BROKEN_PIPE = 129


class Kcat(object):
    do_pretty = None
    out_file = None

    processor_maps = dict(
        J='do_json_d',
        M='do_msgpack_d',
        N='do_netcdf_load',
        P='do_pickle_d',
        R='do_eval',
        Y='do_yaml_d',
        Z='do_zlib_decompress',

        j='do_json_e',
        m='do_msgpack_e',
        n='do_netcdf_save',
        p='do_pickle_e',
        r='do_repr',
        y='do_yaml_e',
        z='do_zlib_compress',
    )

    def __init__(self, args):
        self.args = args

    def run(self):
        processors, fnames = self.parse_opt()

        for fname in fnames:
            if fname == '-':
                try:
                    self.process(sys.stdin, processors)
                except KeyboardInterrupt:
                    sys.exit(EXIT_KB_INT)  # from cat
            else:
                if not os.path.exists(fname):
                    continue

                with open(fname, 'rb') as f:
                    self.process(f, processors)

    def get_opt(self, args, short_opt, long_opt):
        return getopt.getopt(args, short_opt, long_opt)

    def parse_opt(self):
        args = self.args

        short_opt = ''.join(self.processor_maps.keys())
        short_opt = short_opt + 'h'
        long_opt = [
            'exp=',
            'str',

            'pretty',

            'if=',
            'of=',

            'help',
        ]
        opts, args = self.get_opt(args, short_opt, long_opt)

        processors = []
        in_files = []
        out_file = None
        for opt, arg in opts:
            if opt[1:] in self.processor_maps:    # -j / -J / ...
                processors.append(getattr(self, self.processor_maps[opt[1:]]))
            elif opt == '--exp':
                processors.append(self.make_exp(arg))
            elif opt == '--str':
                processors.append(self.do_str)
            elif opt == '--pretty':
                self.do_pretty = True
            elif opt == '--if':
                in_files.append(arg)
            elif opt == '--of':
                out_file = arg
            elif opt == '-h' or opt == '--help':
                usage()
                sys.exit(EXIT_OK)
            else:
                print 'Unknow option: %s' % opt
                usage()
                sys.exit(EXIT_UNKNOW_OPT)

        if out_file:
            self.out_file = out_file

        args = in_files + args
        if not args:
            args = ['-']

        return processors, args

    def do_str(self, buf):
        return str(buf)

    def do_repr(self, buf):
        return repr(buf)

    def do_eval(self, buf):
        globals_ = {}
        return eval(buf, globals_)

    def do_zlib_compress(self, buf):
        import zlib
        return zlib.compress(buf)

    def do_zlib_decompress(self, buf):
        import zlib
        return zlib.decompress(buf)

    def do_pickle_e(self, buf):
        import cPickle
        return cPickle.dumps(buf)

    def do_pickle_d(self, buf):
        import cPickle
        return cPickle.loads(buf)

    def do_yaml_e(self, buf):
        import yaml
        return yaml.dump(buf, indent=2 if self.do_pretty else None)

    def do_yaml_d(self, buf):
        import yaml
        return yaml.load(buf)

    def do_json_e(self, buf):
        import json
        return json.dumps(buf, indent=2 if self.do_pretty else None)

    def do_json_d(self, buf):
        import json
        return json.loads(buf)

    def do_msgpack_e(self, buf):
        import msgpack
        return msgpack.packb(buf)

    def do_msgpack_d(self, buf):
        import msgpack
        return msgpack.unpackb(buf)

    def do_netcdf_save(self, buf):
        import tempfile
        import xray

        assert isinstance(buf, xray.Dataset)

        with tempfile.NamedTemporaryFile('w+') as f:
            fname = f.name
            buf.to_netcdf(fname)

            return f.read()

    def do_netcdf_load(self, buf):
        from cStringIO import StringIO
        import xray

        f = StringIO(buf)

        return xray.open_dataset(f)

    _default_globals = None

    @property
    def default_globals(self):
        if self._default_globals is None:
            self._default_globals = {
                'op': op,
                're': re,
            }

            try:
                import numpy as np
                import pandas as pd
                try:
                    import xarray as xray
                except ImportError:
                    import xray as xray

                self._default_globals.update({
                    'np': np,
                    'pd': pd,
                    'xr': xray,
                })
            except ImportError:
                pass

        return self._default_globals

    def make_globals(self, **kwargs):
        globals_ = {}
        globals_.update(self.default_globals)
        globals_.update(kwargs)

        return globals_

    def make_exp(self, exp):
        code = compile(exp, '<--exp>{}'.format(exp), 'eval', 0, True)

        def exp_fn(buf):
            # print 'run exp:', exp

            buf = eval(code, self.make_globals(buf=buf))

            return buf

        return exp_fn

    def process(self, f, processors):
        buf = f.read()
        for p in processors:
            buf = p(buf)

        try:
            if self.out_file:
                with open(self.out_file, 'wb') as f:
                    f.write(buf)
            else:
                sys.stdout.write(buf)
        except IOError as ex:
            if ex.errno == 32:  # IOError: [Errno 32] Broken pipe
                sys.exit(EXIT_BROKEN_PIPE)
            else:
                raise


def usage(cmd=None):
    if not cmd:
        cmd = sys.argv[0]

    print r"""
kcat v{1:s}
usage: {0:s} [<options>] [<filename>...]

  options:
    -h
    --help  - this help

    -J      - json decode
    -M      - msgpack decode
    -N      - netcdf load
    -P      - py unpickle
    -R      - eval()
    -Y      - yaml decode
    -Z      - zlib decompress

    -j      - json encode
    -m      - msgpack encode
    -n      - netcdf save
    -p      - py pickle
    -r      - repr()
    -y      - yaml encode
    -z      - zlib compress

    --exp=  - run custom expression on buf
              we can use those modules:
                * re - py regexp
                * op - py operator
                * np - numpy
                * pd - pandas
                * xr - xarray (xray)
    --str   - convert with str()
              equall to --exp='str(buf)'

    --pretty - encode in pretty format

    --if=   - input file (instead of args)
    --of=   - out file (be careful with multiple --if, last output will be saved)

  filename:
    filename
    -
""".format(cmd, VERSION).lstrip()
