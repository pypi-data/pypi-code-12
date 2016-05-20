# http://stackoverflow.com/a/1119769/192092
PRONOUNCEABLE_ALPHABET = '23456789abcdefghijkmnpqrstuvwxyz'


def encode_number(non_negative_integer, alphabet=PRONOUNCEABLE_ALPHABET):
    if non_negative_integer < 0:
        raise ValueError
    if non_negative_integer == 0:
        return alphabet[0]
    characters = []
    base = len(alphabet)
    while non_negative_integer:
        remainder = non_negative_integer % base
        non_negative_integer = non_negative_integer // base
        characters.append(alphabet[remainder])
    characters.reverse()
    return ''.join(characters)


def decode_number(string, alphabet=PRONOUNCEABLE_ALPHABET):
    base = len(alphabet)
    string_length = len(string)
    number = 0
    try:
        for character_number, character in enumerate(string, 1):
            power = string_length - character_number
            number += alphabet.index(character) * (base ** power)
    except ValueError:
        number = -1
    return number
