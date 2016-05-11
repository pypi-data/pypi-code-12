import os
from maintain.creators.base import Creator


TEMPLATE = """
# {name}
"""


class ReadmeCreator(Creator):
    name = 'readme'

    def readme(self):
        """
        Weight:
        - 0 (heading, top)
        - 1 badges
        - 2 (description)
        - 3 (installation)
        - 4 (usage)
        - 5
        - 6 (license)
        """
        return (0, '# {}'.format(self.destination))

    def create(self):
        destination = os.path.join(self.destination, 'README.md')

        creators = self.creators + [self]
        readme = lambda creator: getattr(creator, 'readme', None)
        sections = filter(lambda c: c != None, map(readme, creators))
        sections = map(lambda section: section(), sections)
        ordered = map(lambda s: s[1], sorted(sections, key=lambda s: s[0]))
        contents = '\n\n'.join(ordered)

        with open(destination, 'w') as readme:
            readme.write(contents)

