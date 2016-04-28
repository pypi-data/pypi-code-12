from collections import namedtuple
from lxml import objectify
from pyskillkeeper.matches import Match, Tournament

Player = namedtuple('Player', ['name', 'team', 'invisible', 'characters'])
Settings = namedtuple('Settings', ['multiplier', 'min_matches', 'decay', 'decay_value'])


def load_realm(file_path):
    return Realm.from_xml(open(file_path, 'rb'))



class Realm(object):

    def __init__(self, players, matches, settings):
        self.players = players
        self.matches = matches
        self.settings = settings
        self.tournaments = {}
        self.create_tournaments(matches)

    def create_tournaments(self, matches):
        for match in matches:
            if match.tournament not in self.tournaments:
                self.tournaments[match.tournament] = Tournament(match.tournament)
            self.tournaments[match.tournament].matches.append(match)

    @classmethod
    def from_xml(cls, xml_file):
        """
        Creates a Realm object from a SkillKeeper XML file.

        :param xml_file Either an XML file object or XML string data.
        """
        if not isinstance(xml_file, str):
            xml_file = xml_file.read()
        xml_file = objectify.fromstring(xml_file)
        return Realm([Player(name=player.attrib['Name'], team=player.attrib['Team'],
                             invisible=player.attrib['Invisible'], characters=player.attrib['Characters'])
                      for player in xml_file.Players.Player],
                     [Match(id=match.attrib['ID'], time=match.attrib['Timestamp'],
                            order=int(match.attrib['Order']), tournament=match.attrib['Description'],
                            player1=match.attrib['Player1'], player2=match.attrib['Player2'],
                            winner=int(match.attrib['Winner'])) for match in xml_file.Matches.Match],
                     Settings(multiplier=int(xml_file.Settings.attrib['Multiplier']),
                              min_matches=int(xml_file.Settings.attrib['MinMatches']),
                              decay=int(xml_file.Settings.attrib['Decay']),
                              decay_value=int(xml_file.Settings.attrib['DecayValue'])))
