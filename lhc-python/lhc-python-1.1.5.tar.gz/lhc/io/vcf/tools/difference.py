import argparse
import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet
from lhc.io.vcf.iterator import VcfLineIterator


def difference(left_iterator, right_set):
    for left in left_iterator:
        rights = right_set.fetch(left.chr, left.pos, left.pos + len(left.ref))
        matching = len(rights)
        for right in rights:
            if left.pos == right.pos and left.alt == right.alt:
                matching -= 1
        if len(rights) == 0:
            yield left


def main():
    args = get_parser().parse_args()
    args.func(args)

    
def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('left', nargs='?',
                        help='left side (default: stdin)')
    parser.add_argument('right',
                        help='right side')
    parser.add_argument('-o', '--output', nargs='?',
                        help='output file (default: stdout)')
    parser.set_defaults(func=init_difference)
    return parser


def init_difference(args):
    import sys
    left = sys.stdin if args.left is None else\
        gzip.open(args.left) if args.left.endswith('.gz') else\
        open(args.left)
    right = gzip.open(args.right) if args.right.endswith('.gz') else\
        open(args.right)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    left_iterator = VcfLineIterator(left)
    right_set = InOrderAccessSet(VcfLineIterator(right), key=lambda x: (x[0], x[1]))

    for k, vs in left_iterator.hdrs.iteritems():
        for v in vs:
            output.write('{}={}\n'.format(k, v))
    output.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(left_iterator.samples) + '\n')
    for line in difference(left_iterator, right_set):
        output.write(line)
    left.close()
    right.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
