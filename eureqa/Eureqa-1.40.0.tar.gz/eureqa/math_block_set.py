# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from .math_block import MathBlock
import copy

class MathBlockSet(object):
    """
    Tracks which known MathBlock objects are currently available in the system

    Usage:

    >>> # enable the pow building block and set its complexity to 3
    >>> math_blocks.pow.enable(complexity=3)
    >>> # disable the pow building block in searches
    >>> math_blocks.pow.disable()
    >>> # set the complexity of log to 5 (do not change enabled or disabled)
    >>> math_blocks.log.complexity = 5
    >>>
    >>> # enable a list of blocks
    >>> for block in [settings.math_blocks.pow, settings.math_blocks.exp]:
    >>>     block.enable(complexity=3)
    >>>
    >>> # Get a list of enabled blocks w/ complexity
    >>> for block in settings.math_blocks:
    >>>     if block.enabled:
    >>>          print block.complexity
    """

    def __init__(self):
        self._blocks = copy.deepcopy(self._all_blocks)

    def __iter__(self):
        return (block for block in self._blocks.itervalues() if block.enabled)

    def _to_json(self):
        return [block._to_json() for block in self]

    def __str__(self):
        from json import dumps
        return dumps(self._to_json(), indent=4, sort_keys=True)

    def __repr__(self):
        return "MathBlockSet(%s)" % repr(list(self))

    @classmethod
    def from_json(cls, blocks):
        math_blocks = MathBlockSet()
        math_blocks._from_json(blocks)
        return math_blocks

    def _from_json(self, blocks_list):
        for jsonblock in blocks_list:
            block = MathBlock.from_json(jsonblock)
            block._default_complexity = self._all_blocks[block.name]._complexity
            block._enabled = True
            self._blocks[block.name] = block

    def __eq__(self, other):
        ## Two MathBlockSets are equal if they have the same enabled MathBlocks.
        ## "set()" takes an iterable as an argument and calls its __iter__ method
        ## to get the elements to put into the set.
        ## Our __iter__ method filters out disabled MathBlocks; see above.
        ## Note that MathBlock implements all the methods required in order to
        ## be an element in a set(), so this is safe.
        return set(self) == set(other)

    def _get_block(self, name):
        block = self._blocks[name]
        assert name == block.name, "Internal inconsistency:  Index entry for '%s' found block of type '%s'" % (name, block.name)
        return block

    @property
    def const(self):
        """Returns math block for Constant

        :rtype: MathBlock
        """
        return self._get_block('Constant')

    @property
    def int_const(self):
        """Integer Constant math block

        :rtype: MathBlock
        """
        return self._get_block('Integer Constant')


    @property
    def var(self):
        """Input Variable math block

        :rtype: MathBlock
        """
        return self._get_block('Input Variable')

    @property
    def add(self):
        """Addition math block

        :rtype: MathBlock
        """
        return self._get_block('Addition')

    @property
    def sub(self):
        """Subtraction math block

        :rtype: MathBlock
        """
        return self._get_block('Subtraction')

    @property
    def mult(self):
        """Multiplication math block

        :rtype: MathBlock
        """
        return self._get_block('Multiplication')

    @property
    def div(self):
        """Division math block

        :rtype: MathBlock
        """
        return self._get_block('Division')


    @property
    def sin(self):
        """Sine math block

        :rtype: MathBlock
        """
        return self._get_block('Sine')


    @property
    def cos(self):
        """Cosine math block

        :rtype: MathBlock
        """
        return self._get_block('Cosine')

    @property
    def neg(self):
        """Negation math block

        :rtype: MathBlock
        """
        return self._get_block('Negation')

    @property
    def fact(self):

        """Factorial math block

        :rtype: MathBlock
        """
        return self._get_block('Factorial')

    @property
    def pow(self):
        """Power math block

        :rtype: MathBlock
        """
        return self._get_block('Power')

    @property
    def exp(self):
        """Exponential math block

        :rtype: MathBlock
        """
        return self._get_block('Exponential')

    @property
    def log(self):
        """Natural Logarithm math block

        :rtype: MathBlock
        """
        return self._get_block('Natural Logarithm')

    @property
    def abs(self):
        """Absolute Value math block

        :rtype: MathBlock
        """
        return self._get_block('Absolute Value')

    @property
    def if_op(self):
        """If-Then-Else math block

        :rtype: MathBlock
        """
        return self._get_block('If-Then-Else')

    @property
    def logistic(self):
        """Logistic Function math block

        :rtype: MathBlock
        """
        return self._get_block('Logistic Function')

    @property
    def step(self):
        """Step Function math block

        :rtype: MathBlock
        """
        return self._get_block('Step Function')

    @property
    def sign(self):
        """Sign Function math block

        :rtype: MathBlock
        """
        return self._get_block('Sign Function')

    @property
    def gauss(self):
        """Gaussian Function math block

        :rtype: MathBlock
        """
        return self._get_block('Gaussian Function')

    @property
    def min(self):
        """Minimum math block

        :rtype: MathBlock
        """
        return self._get_block('Minimum')

    @property
    def max(self):
        """Maximum math block

        :rtype: MathBlock
        """
        return self._get_block('Maximum')

    @property
    def mod(self):
        """Modulo math block

        :rtype: MathBlock
        """
        return self._get_block('Modulo')

    @property
    def floor(self):
        """Floor math block

        :rtype: MathBlock
        """
        return self._get_block('Floor')

    @property
    def ceiling(self):
        """Ceiling math block

        :rtype: MathBlock
        """
        return self._get_block('Ceiling')

    @property
    def round(self):
        """Round math block

        :rtype: MathBlock
        """
        return self._get_block('Round')

    @property
    def tan(self):
        """Tangent math block

        :rtype: MathBlock
        """
        return self._get_block('Tangent')

    @property
    def equal(self):
        """Equal-To math block

        :rtype: MathBlock
        """
        return self._get_block('Equal-To')

    @property
    def less(self):
        """Less-Than math block

        :rtype: MathBlock
        """
        return self._get_block('Less-Than')

    @property
    def less_equal(self):
        """Less-Than-Or-Equal math block

        :rtype: MathBlock
        """
        return self._get_block('Less-Than-Or-Equal')

    @property
    def greater(self):
        """Greater-Than math block

        :rtype: MathBlock
        """
        return self._get_block('Greater-Than')

    @property
    def greater_equal(self):
        """Greater-Than-Or-Equal math block

        :rtype: MathBlock
        """
        return self._get_block('Greater-Than-Or-Equal')

    @property
    def and_op(self):
        """Logical And math block

        :rtype: MathBlock
        """
        return self._get_block('Logical And')

    @property
    def or_op(self):
        """Logical Or math block

        :rtype: MathBlock
        """
        return self._get_block('Logical Or')

    @property
    def xor(self):
        """Logical Xor math block

        :rtype: MathBlock
        """
        return self._get_block('Logical Xor')

    @property
    def not_op(self):
        """Logical Not math block

        :rtype: MathBlock
        """
        return self._get_block('Logical Not')

    @property
    def tanh(self):
        """Hyperbolic Tangent math block

        :rtype: MathBlock
        """
        return self._get_block('Hyperbolic Tangent')

    @property
    def sqrt(self):
        """Square Root math block

        :rtype: MathBlock
        """
        return self._get_block('Square Root')

    @property
    def delay(self):
        """Delayed Variable math block

        :rtype: MathBlock
        """
        return self._get_block('Delayed Variable')

    @property
    def simple_moving_average(self):
        """Simple Moving Average math block

        :rtype: MathBlock
        """
        return self._get_block('Simple Moving Average')

    @property
    def asin(self):
        """Arcsine math block

        :rtype: MathBlock
        """
        return self._get_block('Arcsine')

    @property
    def acos(self):
        """Arccosine math block

        :rtype: MathBlock
        """
        return self._get_block('Arccosine')

    @property
    def atan(self):
        """Arctangent math block

        :rtype: MathBlock
        """
        return self._get_block('Arctangent')

    @property
    def two_args_atan(self):
        """Two-Argument Arctangent math block

        :rtype: MathBlock
        """
        return self._get_block('Two-Argument Arctangent')

    @property
    def error(self):
        """Error Function math block

        :rtype: MathBlock
        """
        return self._get_block('Error Function')

    @property
    def complementary_error(self):
        """Complementary Error Function math block

        :rtype: MathBlock
        """
        return self._get_block('Complementary Error Function')

    @property
    def weighted_moving_average(self):
        """Weighted Moving Average math block

        :rtype: MathBlock
        """
        return self._get_block('Weighted Moving Average')

    @property
    def _modified_moving_average(self):
        """Modified Moving Average math block

        :rtype: MathBlock
        """
        return self._get_block('Modified Moving Average')

    @property
    def simple_moving_median(self):
        """Simple Moving Median math block

        :rtype: MathBlock
        """
        return self._get_block('Simple Moving Median')

    @property
    def sinh(self):
        """Hyperbolic Sine math block

        :rtype: MathBlock
        """
        return self._get_block('Hyperbolic Sine')

    @property
    def cosh(self):
        """Hyperbolic Cosine math block

        :rtype: MathBlock
        """
        return self._get_block('Hyperbolic Cosine')

    @property
    def asinh(self):
        """Inverse Hyperbolic Sine math block

        :rtype: MathBlock
        """
        return self._get_block('Inverse Hyperbolic Sine')

    @property
    def acosh(self):
        """Inverse Hyperbolic Cosine math block

        :rtype: MathBlock
        """
        return self._get_block('Inverse Hyperbolic Cosine')

    @property
    def atanh(self):
        """Inverse Hyperbolic Tangent math block

        :rtype: MathBlock
        """
        return self._get_block('Inverse Hyperbolic Tangent')


## Do some pre-computation; avoid generating this dictionary repeatedly
def _generate_math_blocks_dict():
    blocks = [
        MathBlock(u'Constant',                     0, u'c_'),
        MathBlock(u'Integer Constant',             1, u'n_'),
        MathBlock(u'Input Variable',               1, u'x_'),
        MathBlock(u'Addition',                     0, u' + '),
        MathBlock(u'Subtraction',                  0, u' - '),
        MathBlock(u'Multiplication',               0, u'*'),
        MathBlock(u'Division',                     2, u'/'),
        MathBlock(u'Sine',                         4, u'sin'),
        MathBlock(u'Cosine',                       4, u'cos'),
        MathBlock(u'Negation',                     4, u'-'),
        MathBlock(u'Factorial',                    4, u'factorial'),
        MathBlock(u'Power',                        4, u'^'),
        MathBlock(u'Exponential',                  4, u'exp'),
        MathBlock(u'Natural Logarithm',            2, u'log'),
        MathBlock(u'Absolute Value',               4, u'abs'),
        MathBlock(u'If-Then-Else',                 1, u'if'),
        MathBlock(u'Logistic Function',            4, u'logistic'),
        MathBlock(u'Step Function',                2, u'step'),
        MathBlock(u'Sign Function',                4, u'sgn'),
        MathBlock(u'Gaussian Function',            4, u'gauss'),
        MathBlock(u'Minimum',                      1, u'min'),
        MathBlock(u'Maximum',                      1, u'max'),
        MathBlock(u'Modulo',                       4, u'mod'),
        MathBlock(u'Floor',                        4, u'floor'),
        MathBlock(u'Ceiling',                      4, u'ceil'),
        MathBlock(u'Round',                        4, u'round'),
        MathBlock(u'Tangent',                      4, u'tan'),
        MathBlock(u'Equal-To',                     4, u'equal'),
        MathBlock(u'Less-Than',                    1, u'less'),
        MathBlock(u'Less-Than-Or-Equal',           4, u'less_or_equal'),
        MathBlock(u'Greater-Than',                 4, u'greater'),
        MathBlock(u'Greater-Than-Or-Equal',        4, u'greater_or_equal'),
        MathBlock(u'Logical And',                  4, u'and'),
        MathBlock(u'Logical Or',                   4, u'or'),
        MathBlock(u'Logical Xor',                  4, u'xor'),
        MathBlock(u'Logical Not',                  4, u'not'),
        MathBlock(u'Hyperbolic Tangent',           4, u'tanh'),
        MathBlock(u'Square Root',                  1, u'sqrt'),
        MathBlock(u'Delayed Variable',             4, u'delay'),
        MathBlock(u'Simple Moving Average',        4, u'sma'),
        MathBlock(u'Arcsine',                      4, u'asin'),
        MathBlock(u'Arccosine',                    4, u'acos'),
        MathBlock(u'Arctangent',                   4, u'atan'),
        MathBlock(u'Two-Argument Arctangent',      4, u'atan2'),
        MathBlock(u'Error Function',               4, u'erf'),
        MathBlock(u'Complementary Error Function', 4, u'erfc'),
        MathBlock(u'Weighted Moving Average',      4, u'wma'),
        MathBlock(u'Modified Moving Average',      4, u'mma'),
        MathBlock(u'Simple Moving Median',         4, u'smm'),
        MathBlock(u'Hyperbolic Sine',              4, u'sinh'),
        MathBlock(u'Hyperbolic Cosine',            4, u'cosh'),
        MathBlock(u'Inverse Hyperbolic Sine',      4, u'asinh'),
        MathBlock(u'Inverse Hyperbolic Cosine',    4, u'acosh'),
        MathBlock(u'Inverse Hyperbolic Tangent',   4, u'atanh')
        ]

    return {x.name: x for x in blocks}

if not hasattr(MathBlockSet, '_all_blocks'):
    MathBlockSet._all_blocks = _generate_math_blocks_dict()
