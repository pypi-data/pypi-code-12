

def xml_to_packet_tree(xml):
	games = []
	for element in xml:
		if element.name == "Game":
			e = GameNode.from_xml()  # Implement from_xml as an alternate constructor
		elif ...:
			pass  # use a dict lookup instead?

		# recursive stuff

	return games
