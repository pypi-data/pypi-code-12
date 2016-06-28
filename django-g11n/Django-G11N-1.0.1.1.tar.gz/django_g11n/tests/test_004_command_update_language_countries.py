"main testing module"
from django.test import TestCase

# Create your tests here.
class UpdateLanguagesTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(UpdateLanguagesTestCase, cls).setUpClass()
        return returns

    def setUp(self):
        returns = TestCase.setUp(self)
        from django.core.management import call_command
        self.call_command = call_command

        from . import common
        self.mock = common.RequestsMock()
        url = 'http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt'
        file_name = 'ISO-639-2_utf-8.txt'

        self.mock.add_response_text_from_data(url, file_name)
        self.mock.insert_mock()

        return returns

    def tearDown(self):
        TestCase.tearDown(self)
        self.mock.remove_mock()


    def test_001_update_language(self):
        self.call_command('update_languages')
        # Calling twice, as the second time it should exclude it.
        #pylint: disable=protected-access, undefined-variable
        #
        from ..tools import models
        models.ALL['Language'].objects.create(
            code_a2='**', english='Double Star', french='Astérisque Double')
        self.call_command('update_languages')

    def test_002_update_language_country(self):
        self.call_command('update_countries')
        self.call_command('update_languages')
        self.call_command('update_language_countries')
        #
        from ..tools import models
        models.ALL['LanguageCountrySpecifier'].objects.create(
            short='??', value='Question Marks', override=False)
        model = models.ALL['LanguageCountry']()
        model.language_id=4
        model.country_id=16
        model.specifier_id=1
        model.override=False
        model.save()
        self.call_command('update_language_countries')

    def test_003_tool_country_addition(self):
        from ..tools import language
        addition = [1,2,3,4,5,6]
        language.ADDITIONS.append(addition)
        is_added = False
        for entry in language.get():
            if entry == addition:
                is_added = True
                break

        self.assertTrue(is_added)
        


if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

