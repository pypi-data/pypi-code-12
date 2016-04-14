from .. import primitives
from ..ifuzzable import IFuzzable


class Size(IFuzzable):
    """
    This block type is kind of special in that it is a hybrid between a block and a primitive (it can be fuzzed). The
    user does not need to be wary of this fact.
    """

    def __init__(self, block_name, request, offset=0, length=4, endian="<", output_format="binary", inclusive=False,
                 signed=False, math=None, fuzzable=False, name=None):
        """
        Create a sizer block bound to the block with the specified name. You *can not* create a sizer for any
        currently open blocks.

        @type  block_name:    str
        @param block_name:    Name of block to apply sizer to
        @type  request:       s_request
        @param request:       Request this block belongs to
        @type  length:        int
        @param length:        (Optional, def=4) Length of sizer
        @type  offset:        int
        @param offset:        (Optional, def=0) Offset for calculated size value
        @type  endian:        chr
        @param endian:        (Optional, def=LITTLE_ENDIAN) Endianess of the bit field (LITTLE_ENDIAN: <, BIG_ENDIAN: >)
        @type  output_format: str
        @param output_format: (Optional, def=binary) Output format, "binary" or "ascii"
        @type  inclusive:     bool
        @param inclusive:     (Optional, def=False) Should the sizer count its own length?
        @type  signed:        bool
        @param signed:        (Optional, def=False) Make size signed vs. unsigned (applicable only with format="ascii")
        @type  math:          def
        @param math:          (Optional, def=None) Apply the mathematical op defined in this function to the size
        @type  fuzzable:      bool
        @param fuzzable:      (Optional, def=False) Enable/disable fuzzing of this sizer
        @type  name:          str
        @param name:          Name of this sizer field
        """

        self.block_name = block_name
        self.request = request
        self.offset = offset
        self.length = length
        self.endian = endian
        self.format = output_format
        self.inclusive = inclusive
        self.signed = signed
        self.math = math
        self._fuzzable = fuzzable
        self._name = name

        self._original_value = "N/A"  # for get_primitive
        self.bit_field = primitives.BitField(
                0,
                self.length * 8,
                endian=self.endian,
                output_format=self.format,
                signed=self.signed
        )
        self._rendered = ""
        self._fuzz_complete = False
        self._mutant_index = self.bit_field.mutant_index

        if not self.math:
            self.math = lambda (x): x

    @property
    def name(self):
        return self._name

    @property
    def mutant_index(self):
        return self._mutant_index

    @property
    def fuzzable(self):
        return self._fuzzable

    @property
    def original_value(self):
        return self._original_value

    def exhaust(self):
        """
        Exhaust the possible mutations for this primitive.

        @rtype:  int
        @return: The number of mutations to reach exhaustion
        """

        num = self.num_mutations() - self._mutant_index

        self._fuzz_complete = True
        self._mutant_index = self.num_mutations()
        self.bit_field._mutant_index = self.num_mutations()

        return num

    def mutate(self):
        """
        Wrap the mutation routine of the internal bit_field primitive.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """

        self._mutant_index += 1

        not_finished_yet = self.bit_field.mutate()

        self._fuzz_complete = not not_finished_yet  # double negatives for the win

        return not_finished_yet

    def num_mutations(self):
        """
        Wrap the num_mutations routine of the internal bit_field primitive.

        @rtype:  int
        @return: Number of mutated forms this primitive can take.
        """

        return self.bit_field.num_mutations()

    def render(self):
        """
        Render the sizer.

        :return Rendered value.
        """
        # if the sizer is fuzzable and we have not yet exhausted the the possible bit field values, use the fuzz value.
        if self._fuzzable and self.bit_field.mutant_index and not self._fuzz_complete:
            self._rendered = self.bit_field.render()
        else:
            length = self.offset
            if self.inclusive:
                length += self.length
            length += len(self.request.names[self.block_name])

            self.bit_field._value = self.math(length)

            self._rendered = self.bit_field.render()

        return self._rendered

    def reset(self):
        """
        Wrap the reset routine of the internal bit_field primitive.
        """

        self.bit_field.reset()

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self._name)

    def __len__(self):
        return self.length

    def __nonzero__(self):
        """
        Make sure instances evaluate to True even if __len__ is zero.

        :return: True
        """
        return True
