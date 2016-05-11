import os
from datetime import datetime
import six
from maintain.creators.base import Creator, ValidationError


class LicenseCreator(Creator):
    name = 'license'

    def __str__(self):
        if self.license_name:
            return '{} ({})'.format(self.name, self.license_name)
        return super(LicenseCreator, self).__str__()

    def validate(self):
        self.year = datetime.now().year
        self.organization = self.config['user.name']
        self.project = self.destination

        license = self.config['license']
        license_type = self.config['license.type']
        license_file = self.config['license.file']

        if isinstance(license, six.string_types):
            path = self.path_for_license(license)

            if not path:
                raise ValidationError('Unsupported license: {}'.format(license))

            self.license_name = license.upper()
            self.license_path = path
        elif license_type and license_file:
            self.license_name = license_type
            self.license_path = license_file
            if not os.path.isfile(license_file):
                raise ValidationError('{} does not exist.'.format(license_file))
        else:
            raise ValidationError('Missing license.')

    def create(self):
        destination = os.path.join(self.destination, 'LICENSE')

        with open(self.license_path) as fp:
            contents = fp.read()
            contents = contents.replace('{{ year }}', str(self.year))
            contents = contents.replace('{{ organization }}', str(self.organization))
            contents = contents.replace('{{ project }}', self.project)

            with open(destination, 'w') as license:
                license.write(contents)

    # Private

    def path_for_license(self, name):
        if name.lower() == 'bsd':
            name = 'bsd2'

        licenses_dir = os.path.join(os.path.dirname(__file__), 'templates/templates')
        path = os.path.join(licenses_dir, name.lower() + '.txt')
        if os.path.exists(path):
            return path

    # Hooks

    def readme(self):
        return (
            6,
            '# License\n\n{} is released under the {} license. See [LICENSE](LICENSE).\n'.format(self.destination, self.license_name)
        )
