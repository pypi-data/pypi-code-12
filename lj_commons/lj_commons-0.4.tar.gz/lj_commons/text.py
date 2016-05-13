from markdown import markdown


def joke(words):
    return markdown(u'Wenn ist das Nunst\u00fcck git und Slotermeyer? Ja! ... '
                    u'**Beiherhund** das Oder die Flipperwaldt gersput.'
                    u'and he says %s' % words)
