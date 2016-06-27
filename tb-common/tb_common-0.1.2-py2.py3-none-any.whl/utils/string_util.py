__author__ = 'hiepsimu'


def substring_by_space(text, size):
    text_len = len(text)
    while (size >= 0) and (text_len > size) and text[size] != ' ':
        size -= 1

    if size < 0:
        return None

    if len(text) <= size:
        return text

    return text[:size]