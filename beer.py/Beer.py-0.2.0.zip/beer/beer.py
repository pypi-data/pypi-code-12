#!/usr/bin/python
# -*- coding: utf-8 -*-


class Beer:
    LETTERS = ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'y', 'x',
               'c', 'v', 'b', 'n', 'm']

    @staticmethod
    def serialize_beer(text):
        text = text.replace(".", "BEER-BEER∫")
        text = text.replace(",", "BEER_BEER∫")

        for i in range(0, len(Beer.LETTERS)):
            if Beer.LETTERS[i] not in ['b', 'e', 'r']:
                text = text.replace(Beer.LETTERS[i].upper(), Beer.repeat_string('∫', 'µ', i))

            text = text.replace(Beer.LETTERS[i], Beer.repeat_string('∫', 'BEER', i))

        return text

    @staticmethod
    def deserialize_beer(text):
        text = text.replace("BEER-BEER∫", ".")
        text = text.replace("BEER_BEER∫", ",")

        for i in range(len(Beer.LETTERS) - 1, -1, -1):
            if Beer.LETTERS[i] not in ['b', 'e', 'r']:
                text = text.replace(Beer.repeat_string('∫', 'µ', i), Beer.LETTERS[i].upper())

            text = text.replace(Beer.repeat_string('∫', 'BEER', i), Beer.LETTERS[i])

        return text

    @staticmethod
    def repeat_string(final_character, string_to_repeat, count):
        result = string_to_repeat

        for i in range(0, count):
            result += string_to_repeat

        return result + final_character


if __name__ == '__main__':
    print("Nothing to do here...")
