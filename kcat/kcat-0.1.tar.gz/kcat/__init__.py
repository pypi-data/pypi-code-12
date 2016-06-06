# -*- coding: utf-8 -*-

import sys
import os
import getopt


class Kcat(object):
    do_pretty = None

    def __init__(self, args):
        self.args = args

    def run(self):
        processors, fnames = self.parse_opt()

        for fname in fnames:
            if fname == '-':
                try:
                    self.process(sys.stdin, processors)
                except KeyboardInterrupt:
                    sys.exit(130)  # from cat
            else:
                if not os.path.exists(fname):
                    continue

                with open(fname, 'rb') as f:
                    self.process(f, processors)

    def get_opt(self, args, short_opt, long_opt):
        return getopt.getopt(args, short_opt, long_opt)

    def parse_opt(self):
        args = self.args

        processor_maps = dict(
            z='do_compress',
            Z='do_decompress',
            j='do_json_e',
            J='do_json_d',
            y='do_yaml_e',
            Y='do_yaml_d',
            p='do_pickle_e',
            P='do_pickle_d',
            m='do_msgpack_e',
            M='do_msgpack_d',
            r='do_repr_e',
            n='do_netcdf_save',
            N='do_netcdf_load',
        )

        short_opt = ''.join(processor_maps.keys())
        short_opt = short_opt + 'h'
        opts, args = self.get_opt(args, short_opt, [
            'pretty',
            'str',
            'exp=',
            'help',
            'if=',
        ])

        processors = []
        in_files = []
        for opt, arg in opts:
            if opt in ('--pretty',):
                self.do_pretty = True
            elif opt[1:] in processor_maps:
                processors.append(getattr(self, processor_maps[opt[1:]]))
            elif opt == '--exp':
                processors.append(self.make_exp(arg))
            elif opt == '--str':
                processors.append(self.do_str)
            elif opt == '--if':
                in_files.append(arg)
            elif opt in ('-h', '--help',):
                usage()
                sys.exit(0)
            else:
                print 'Unknow opt for v: %s' % opt
                usage()
                sys.exit(1)

        args = in_files + args
        if not args:
            args = ['-']

        return processors, args

    def do_str(self, buf):
        return str(buf)

    def do_repr_e(self, buf):
        return repr(buf)

    def do_compress(self, buf):
        import zlib
        return zlib.compress(buf)

    def do_decompress(self, buf):
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

    def make_exp(self, exp):
        code = compile(exp, '<--exp>{}'.format(exp), 'eval', 0, True)

        def exp_fn(buf):
            # print 'run exp:', exp
            globs = {
                'buf': buf,
            }
            buf = eval(code, globs)

            return buf

        return exp_fn

    def process(self, f, processors):
        buf = f.read()
        for p in processors:
            buf = p(buf)

        try:
            sys.stdout.write(buf)
        except IOError as ex:
            if ex.errno == 32:  # IOError: [Errno 32] Broken pipe
                sys.exit(129)

            raise
            # sys.stderr.write(repr(dir(ex)))


def usage(cmd=None):
    if not cmd:
        cmd = sys.argv[0]

    print r"""
    {0:s} [<options>] [<filename>...]
      options:
        -Z      - zlib decompress
        -z      - zlib compress
        -j      - json encode
        -J      - json decode
        -y      - yaml encode
        -Y      - yaml decode
        -m      - msgpack encode
        -M      - msgpack decode
        -r      - repr
        -R      - HOLD
        -N      - netcdf load
        -n      - netcdf save
        --if=   - input file (instead of args)
        --exp=  - run custom expression on buf
        --str   - convert with str()
                  equall to --exp='str(buf)'
        --pretty - encode in pretty format
      filename:
        filename
        -
""".format(cmd)
