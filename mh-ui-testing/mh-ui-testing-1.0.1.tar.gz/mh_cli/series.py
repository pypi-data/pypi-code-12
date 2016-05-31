
import click
import random

from mh_cli import cli

from urlparse import urljoin
from common import pass_state, init_browser, selenium_options
from mh_pages.pages import ApiDocPage

CATALOG_XML = '''
<?xml version="1.0" encoding="UTF-8"?>
<dublincore xmlns="http://www.opencastproject.org/xsd/1.0/dublincore/"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:oc="http://www.opencastproject.org/matterhorn/">
    <dcterms:creator>Harvard Extension School</dcterms:creator>
    <dcterms:contributor>Henry H. Leitner</dcterms:contributor>
    <dcterms:description>http://extension.harvard.edu</dcterms:description>
    <dcterms:subject>SERIES_SUBJECT</dcterms:subject>
    <dcterms:language>eng</dcterms:language>
    <dcterms:publisher>Harvard University, DCE</dcterms:publisher>
    <oc:annotation>true</oc:annotation>
    <dcterms:identifier>SERIES_ID</dcterms:identifier>
    <dcterms:title>SERIES_TITLE</dcterms:title>
</dublincore>
'''

ACL_XML = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<acl xmlns="http://org.opencastproject.security">
    <ace>
        <role>ROLE_ADMIN</role>
        <action>read</action>
        <allow>true</allow>
    </ace>
    <ace>
        <role>ROLE_ADMIN</role>
        <action>write</action>
        <allow>true</allow>
    </ace>
    <ace>
        <role>ROLE_ADMIN</role>
        <action>delete</action>
        <allow>true</allow>
    </ace>
    <ace>
        <role>ROLE_ADMIN</role>
        <action>analyze</action>
        <allow>true</allow>
    </ace>
    <ace>
        <role>ROLE_ANONYMOUS</role>
        <action>read</action>
        <allow>true</allow>
    </ace>
</acl>
'''


@cli.group()
def series():
    """Do stuff with Matterhorn series"""


@series.command()
@selenium_options
@click.option('--title', default='Test Offering',
              help="Title of the series")
@click.option('--subject', default=None,
              help=("Subject of the series. If not specified this "
                    "will take the form 'TEST S-xxxxx', "
                    "where 'xxxxx' is the last 5 digits of the identifier."))
@click.option('--id', default=None,
              help=("Series identifier. If not specified this will be "
                    "generated for you in the format '203501xxxxx' "
                    "where 'xxxxx' is a random number sequence"))
@pass_state
@init_browser('/admin')
def create(state, title, subject, id):

    if id is None:
        id = '203501' + ''.join([str(x) for x in random.sample(range(10), 5)])

    if subject is None:
        subject = 'TEST S-' + id[-5:]

    catalog_xml = CATALOG_XML.replace('SERIES_ID', id)
    catalog_xml = catalog_xml.replace('SERIES_TITLE', title)
    catalog_xml = catalog_xml.replace('SERIES_SUBJECT', subject)

    doc_page_url = urljoin(state.base_url, '/docs.html?path=/series')
    page = ApiDocPage(state.browser, doc_page_url)

    page.submit_form(
        'form_updateSeries',
        {
            'updateSeries_series': catalog_xml.strip(),
            'updateSeries_acl': ACL_XML.strip()
        }
    )
