# -*- coding: utf-8 -*-
from __future__ import print_function
from . import exception
from .basexml import BaseXML
from .keycombo import KeyCombo
from .fucking_string import u


class KeyToKeyBase(BaseXML):
    """A object represent `autogen` XML node in Karabiner.
    For example, the following XML is a typical `autogen`.

        <autogen> __KeyToKey__
            KeyCode::E, ModifierFlag::OPTION_L, ModifierFlag::NONE,
            KeyCode::E, ModifierFlag::COMMAND_L
        </autogen>
    """
    MULTI_KEYS_FMT = u('@begin\n{key}\n@end')
    AUTOGEN_FMT = u(' {type}\n{keys_str}\n')

    def __init__(self, *keycombos, **kwargs):
        self.keys_str = self.parse(*keycombos, **kwargs)

    def parse(self, *keycombos, **kwargs):
        """
        :param keycombos: List[List[str]]
        :param kwargs: Dict
        :return: str
        """
        raise exception.NeedOverrideError()

    def get_type(self):
        return '__%s__' % self.get_class_name()

    def to_xml(self):
        text = self.AUTOGEN_FMT.format(type=self.get_type(),
                                       keys_str=self.keys_str)
        return self.create_tag('autogen', text)


class UniversalKeyToKey(KeyToKeyBase):
    def __init__(self, type, *keycombos, **kwargs):
        self.type = type
        super(UniversalKeyToKey, self).__init__(*keycombos, **kwargs)

    def get_type(self):
        return self.type

    def parse(self, *keycombos, **kwargs):
        keys = [KeyCombo(k, keep_first_keycode=True, has_modifier_none=False) for k in keycombos]
        return ',\n'.join(str(k) for k in keys)


class _KeyToMultiKeys(KeyToKeyBase):
    KEYS_FMT = u('{from_key},\n'
                 '@begin\n'
                 '{to_key}\n'
                 '@end\n'
                 '@begin\n'
                 '{additional_key}\n'
                 '@end')

    def parse(self, from_key, to_key, additional_key, has_modifier_none=True):
        from_key = KeyCombo(from_key, has_modifier_none)
        to_key = KeyCombo(to_key)
        additional_key = KeyCombo(additional_key)

        return self.KEYS_FMT.format(from_key=from_key.to_str(),
                                    to_key=to_key.to_str(),
                                    additional_key=additional_key.to_str())


class _KeyToAdditionalKey(_KeyToMultiKeys):
    def parse(self, from_key, to_key=None, additional_key=None, has_modifier_none=True):
        if to_key is None and additional_key is None:
            raise exception.InvalidKeymapException(from_key)
        elif to_key and additional_key is None:
            additional_key = to_key
            to_key = from_key

        return super(_KeyToAdditionalKey, self).parse(from_key,
                                                      to_key,
                                                      additional_key,
                                                      has_modifier_none)


class _OneKeyEvent(KeyToKeyBase):
    def parse(self, key, has_modifier_none=False):
        return KeyCombo(key, has_modifier_none).to_str()


class _ZeroKeyEvent(KeyToKeyBase):
    def parse(self):
        return ''


class _MultiKeys(UniversalKeyToKey):
    def __init__(self, *keys, **kwargs):
        super(_MultiKeys, self).__init__(self.get_type(), *keys, **kwargs)

    def get_type(self):
        return '__%s__' % self.get_class_name()


class KeyToKey(KeyToKeyBase):
    """
    >>> keymap = KeyToKey(['ModifierFlag::OPTION_L', 'KeyCode::E'],
    ...                   ['ModifierFlag::COMMAND_L', 'KeyCode::E'])
    >>> s = '''
    ...     <autogen> __KeyToKey__
    ...         KeyCode::E, ModifierFlag::OPTION_L, ModifierFlag::NONE,
    ...         KeyCode::E, ModifierFlag::COMMAND_L
    ...     </autogen>
    ...     '''
    >>> util.assert_xml_equal(keymap, s)
    """
    KEYS_FMT = u('{from_key},\n{to_key}')

    def parse(self, from_key, to_key, has_modifier_none=True):
        from_key = KeyCombo(from_key, has_modifier_none=has_modifier_none).to_str()
        to_key = KeyCombo(to_key).to_str()

        return self.KEYS_FMT.format(from_key=from_key, to_key=to_key)


class DropAllKeys(KeyToKeyBase):
    KEYS_FMT = u('{from_key},\n{options}')

    def parse(self, from_modifier, options=None):
        from_key = KeyCombo(from_modifier, keep_first_keycode=True)

        if options is None:
            return from_key.to_str()
        else:
            options = KeyCombo(options, keep_first_keycode=True)
            return self.KEYS_FMT.format(from_key=from_key.to_str(),
                                        options=options.to_str())


class SimultaneousKeyPresses(KeyToKeyBase):
    KEYS_FMT = u('@begin\n'
                 '{from_key}\n'
                 '@end\n'
                 '@begin\n'
                 '{to_key}\n'
                 '@end')

    def parse(self, from_key, to_key):
        from_key = KeyCombo(from_key, False)
        to_key = KeyCombo(to_key, False)

        return self.KEYS_FMT.format(from_key=from_key.to_str(),
                                    to_key=to_key.to_str())


class DoublePressModifier(_KeyToAdditionalKey):
    pass


class HoldingKeyToKey(_KeyToAdditionalKey):
    pass


class KeyOverlaidModifier(_KeyToAdditionalKey):
    pass


class KeyDownUpToKey(_KeyToMultiKeys):
    def parse(self, from_key, immediately_key, interrupted_key=None, has_modifier_none=True):
        return super(KeyDownUpToKey, self).parse(from_key,
                                                 immediately_key,
                                                 interrupted_key or from_key,
                                                 has_modifier_none)


class BlockUntilKeyUp(_OneKeyEvent):
    pass


class DropKeyAfterRemap(_OneKeyEvent):
    pass


class PassThrough(_ZeroKeyEvent):
    pass


class DropPointingRelativeCursorMove(_ZeroKeyEvent):
    pass


# NOTICE: because below `autogen` command not yet documented,
#         so those implements maybe changed in future
class DropScrollWheel(_MultiKeys):
    pass


class FlipPointingRelative(_MultiKeys):
    pass


class FlipScrollWheel(_MultiKeys):
    pass


class IgnoreMultipleSameKeyPress(_MultiKeys):
    pass


class StripModifierFromScrollWheel(_MultiKeys):
    pass


class ScrollWheelToScrollWheel(_MultiKeys):
    pass


class ScrollWheelToKey(_MultiKeys):
    pass


class PointingRelativeToScroll(_MultiKeys):
    pass


class PointingRelativeToKey(_MultiKeys):
    pass


class ForceNumLockOn(_MultiKeys):
    pass


class ShowStatusMessage(KeyToKeyBase):
    def parse(self, *keys, **kwargs):
        return ' '.join(keys)


class SetKeyboardType(_OneKeyEvent):
    pass


if __name__ == "__main__":
    import doctest
    from . import util
    doctest.testmod(extraglobs={'util': util})
