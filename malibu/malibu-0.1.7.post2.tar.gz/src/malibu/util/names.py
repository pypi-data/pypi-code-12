# -*- coding: utf-8 -*-
import random
import types

_adjectives = []
_nouns = []


def __load_default_wordlists():
    """ Populates the lists with default content.
    """

    wordlists = {
        "nouns": [],
        "adjectives": [],
    }

    wordlists["nouns"].extend([
        "axel", "babbage", "baby", "ballmer", "bay", "bishop", "bulbasaur",
        "charles", "charlie", "charmander", "clarice", "doctor", "doge",
        "drone", "einstein", "failfish" "feynman", "fish", "gates", "grump",
        "horton", "jessica", "jobs", "johnson", "king", "metcalfe", "mew",
        "michael", "nicholas", "pimp", "priest", "roadrunner", "tacocat",
        "transformers", "voltorb", "wayne", "worker", "zuckerberg",
    ])

    wordlists["adjectives"].extend([
        "adorable", "bigoted", "bouncy", "charming", "chipper", "comical",
        "crass", "creepy", "cross", "dangerous", "despressed", "diminished",
        "disfigured", "disturbed", "ecstatic", "electric", "enlightened",
        "excited", "failing", "faithful", "fastidious", "fervent", "firey",
        "flying", "frazzled", "freaky", "friendly", "frustrated", "gloomy",
        "glum", "gnarled", "gross", "hurtful", "immune", "intense", "jealous",
        "likable", "livid", "massive", "nasty", "naughty", "nosey", "offended",
        "overzealous", "peculiar", "perfunctory", "pleasant", "pokey",
        "pontiferous", "ravishing", "resourceful", "ridiculous", "riveting",
        "rowdy", "sad", "smashed", "smelly", "spectacular", "terrified",
        "voltaic",
    ])

    return wordlists


def __load_gfycat_wordlists():
    """ Pulls wordlists from gfycat.
            nouns ~> http://test.gfycat.com/animals
            adjectives ~> http://test.gfycat.com/adjectives
    """

    try:
        import requests
    except ImportError:
        raise ImportError("requests must be installed to pull gfycat wordlist")

    wordlists = {
        "nouns": [],
        "adjectives": [],
    }

    nouns = requests.get('http://test.gfycat.com/animals')
    nouns = nouns.text.split("\n")
    nouns.pop(-1)

    adjectives = requests.get('http://test.gfycat.com/adjectives')
    adjectives = adjectives.text.split("\n")
    adjectives.pop(-1)

    wordlists["nouns"] = nouns
    wordlists["adjectives"] = adjectives

    return wordlists


def load_external_words(source=None, target_list=None):
    """ Loads external wordlists with either data from a file
        or a pre-programmed source.

        target_list should be one of:
            adjectives
            nouns

        Available sources:
           "gfycat" ~> Loads data from test.gfycat.com
           <file object> ~> Loads newline-delimited words from an open handle
                            Requires target_list to be set.
           <function> ~> output like the following:
                {
                   "adjectives": ["words", ...],
                   "nouns": ["words", ...]
                }
    """

    # Pre-programmed sources first
    if source == "gfycat":
        source = __load_gfycat_wordlists
    elif source == "default":
        source = __load_default_wordlists

    if hasattr(source, "read"):  # File-like object
        if not target_list:
            raise ValueError("A target list must be specified when reading "
                             "from a file")

        # Check value of target list
        if target_list not in ["adjectives", "nouns"]:
            raise ValueError("target_list must be one of: adjectives, nouns")

        data = source.read()
        data = data.split("\n")

        if target_list == "adjectives":
            _adjectives.extend(data)
        elif target_list == "nouns":
            _nouns.extend(data)
    elif isinstance(source, types.FunctionType):  # Function or lambda
        w = source()
        if "nouns" not in w:
            raise AttributeError("No 'nouns' list in returned data")

        if "adjectives" not in w:
            raise AttributeError("No 'adjectives' list in returned data")

        if not isinstance(w["nouns"], list):
            raise TypeError("Expected 'nouns' list, got %s" %
                            (type(w["nouns"])))

        if not isinstance(w["adjectives"], list):
            raise TypeError("Expected 'adjectives' list, got %s" %
                            (type(w["adjectives"])))

        _nouns.extend(w["nouns"])
        _adjectives.extend(w["adjectives"])


def get_simple_name(delim='_'):

    if len(_adjectives) == 0 or len(_nouns) == 0:
        load_external_words(source="default")

    adj = random.choice(_adjectives)
    noun = random.choice(_nouns)

    return delim.join([adj, noun])


def get_complex_name(num_adjs=1, num_nouns=1, delim='_'):

    if len(_adjectives) == 0 or len(_nouns) == 0:
        load_external_words(source="default")

    adjs = [random.choice(_adjectives) for i in range(num_adjs)]
    nouns = [random.choice(_nouns) for i in range(num_nouns)]

    adjs.extend(nouns)

    return delim.join(adjs)
