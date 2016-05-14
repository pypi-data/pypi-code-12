# -*- coding: utf-8 -*-
from __future__ import print_function


class KeyCombo(object):
    """Convert key list to Karabiner's favorite format

    >>> print(KeyCombo(['ModifierFlag::SHIFT_L', 'ModifierFlag::COMMAND_L']))
    KeyCode::SHIFT_L, ModifierFlag::COMMAND_L

    >>> print(KeyCombo(['ModifierFlag::SHIFT_L', 'ModifierFlag::COMMAND_L', 'KeyCode::K'], has_modifier_none=True))
    KeyCode::K, ModifierFlag::SHIFT_L, ModifierFlag::COMMAND_L, ModifierFlag::NONE
    """

    def __init__(self, keys=None, has_modifier_none=False, keep_first_keycode=False):
        self.has_modifier_none = has_modifier_none
        self.keep_first_keycode = keep_first_keycode
        self.keys = self.parse(keys or [])

    def parse(self, keys):
        """
        :param keys: List[str]
        :return: List[str]
        """
        # we need adjust position of keys, because the first key cannot be modifier key in most case
        keys = self.rearrange_keys(keys)

        if len(keys) > 0:
            if not self.keep_first_keycode and self.is_modifier_key(keys[0]):
                # change the header of first key to `KeyCode`
                keys = self.regularize_first_key(keys)
            if self.has_modifier_none and self.is_modifier_key(keys[-1]):
                keys = self.add_modifier_none(keys)

        return keys

    def rearrange_keys(self, keys):
        tmp = []
        last = 0

        for i in range(len(keys)):
            if not self.is_modifier_key(keys[i]):
                tmp.append(keys[i])
                while last < i:
                    tmp.append(keys[last])
                    last += 1
                last = i + 1

        tmp.extend(keys[last:])
        return tmp

    @classmethod
    def is_modifier_key(cls, key):
        return key.lower().startswith('modifier')

    @classmethod
    def regularize_first_key(cls, keys):
        parts = keys[0].split('::', 1)
        keys[0] = 'KeyCode::' + parts[-1]
        return keys

    # Append 'ModifierFlag::NONE' if you want to change from this key
    # For more information about 'ModifierFlag::NONE', see https://pqrs.org/osx/karabiner/xml.html.en
    @classmethod
    def add_modifier_none(cls, keys):
        keys.append('ModifierFlag::NONE')
        return keys

    def to_str(self):
        return ', '.join(self.keys)

    def __add__(self, another):
        res = KeyCombo()
        res.keys = self.keys + another.keys
        res.has_modifier_none = self.has_modifier_none or another.has_modifier_none
        res.keep_first_keycode = self.keep_first_keycode or another.keep_first_keycode
        return res

    def __str__(self):
        return self.to_str()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
