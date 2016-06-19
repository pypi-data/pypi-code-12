"""
Inspired by 'import this' and The Trashmen
Answering the eterinal question of "What is the word?"
"""

import json
import webbrowser

# Show console users that the bird is the word
# Just like `import this`

print """_Surfin' Bird_, by The Trashmen

A well a everybody's heard about the bird
Bird, bird, bird, b-bird's the word
A well a bird, bird, bird, b-bird's the word
A well a bird, bird, bird, b-bird's the word
A well a bird, bird, b-bird's the word
"""


class TheWord(object):
	"""
	The Word
	"""

	def __init__(self):
		self.id = None  # `is` is keyword
		self.question = "What's the word?"

	def __str__(self):
		return self.id if self.id else self.question


class TheBird(TheWord):
	"""
	[E]verybody knows that the bird is the word! 
	"Sir, our math shows that the Bird is greater than or equal to the Word" 
	"""

	def __init__(self):
		super(TheBird, self).__init__()
		self.answer = "[E]verybody knows that the bird is the word!"
		self.id = "The Bird"


	def __str__(self):
		return json.dumps(self.__dict__) # Fast way to show all attributes 


	def play(self):
		"""
		Play _Surfin' Bird_ by The Trashmen
		"""
		self.title = "Surfin' Bird"
		self.artist = "The Trashmen"
		self.released = 1964

		print self.__dict__
		webbrowser.open('https://www.youtube.com/watch?v=aPrtFxd9u9Y')
		
		return 


	def celebrate(self):
		"""
		See Seth MacFarlane celebrate the bird
		"""
		self.celebrated_by = "Seth MacFarlane"
		self.celebrated_on = "FOX's The Family Guy"

		print self.__dict__
		webbrowser.open('https://www.youtube.com/watch?v=2WNrx2jq184')
		
		return


def what_is_the_word():
	"""
	When asked what the word is, return TheBird()

	Some uses:
	>>> print what_is_the_word()
	>>> what_is_the_word().answer
	>>> what_is_the_word().id
	>>> type(what_is_the_word())
	>>> what_is_the_word().play()

	"""
	return TheBird()
