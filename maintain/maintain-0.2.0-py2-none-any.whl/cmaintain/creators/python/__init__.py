import os
from maintain.creators.base import Creator, ValidationError
from maintain.creators.license import LicenseCreator


README_TEMPLATE = """## Installation

```
$ pip install {name}
```"""

class PythonCreator(Creator):
    name = 'python'

    @classmethod
    def dependencies(cls):
        return [LicenseCreator]

    def create(self):
        source = os.path.join(os.path.dirname(__file__), 'setup.py.template')
        destination = os.path.join(self.destination, 'setup.py')

        name = self.destination
        author = str(self.config['user.name'] or 'Unknown')
        email = str(self.config['user.email'] or 'Unknown')
        license = str(self.config['license.type'] or self.config['license'] or 'Unknown')

        with open(source) as fp:
            contents = fp.read()
            contents = contents.replace('{{ name }}', name)
            contents = contents.replace('{{ author }}', author)
            contents = contents.replace('{{ email }}', email)
            contents = contents.replace('{{ license }}', license)

            with open(destination, 'w') as setup:
                setup.write(contents)

    # Hooks
    def readme(self):
        return (3, README_TEMPLATE.format(name=self.destination))

