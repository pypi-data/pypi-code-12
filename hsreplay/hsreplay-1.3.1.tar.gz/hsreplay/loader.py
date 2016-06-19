from xml.etree import ElementTree
from hsreplay.elements import GameNode
# from hsreplay.loader import create_document
# from hearthstone.hslog import packets


class HSReplayLoader:
	def __init__(self):
		self.games = []

	def load_xml(self, xml):
		for element in xml.findall("Game"):
			pass
			# game = GameNode.from_xml(element)

	def create_game(self, element):
		pass
		# game = packets.Game()
		# game = elements.GameNode.from_xml()


def xml_to_packet_tree(xml):
	games = []
	for element in xml.findall("Game"):

		if element.tag == "Game":
			print("game: %r" % (element))
			# e = GameNode.from_xml()  # Implement from_xml as an alternate constructor
		elif ...:
			pass  # use a dict lookup instead?

		# recursive stuff

	return games


def main():
	print("testing")
	with open("Power.log.xml", "rb") as f:
		xml = ElementTree.parse(f)

	print(ElementTree.tostring(xml.getroot())[:100])

	# xml = create_document()

	for element in xml.findall("Game"):
		game = GameNode.from_xml(element)
		xml = game.xml()
		print(ElementTree.tostring(xml))


main()
