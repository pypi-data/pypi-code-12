# -*- coding: utf-8 -*-
from App.Common import package_home
from DateTime import DateTime
from PIL import Image
from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.testing import z2
from StringIO import StringIO

import os
import random


class CreateTestContent(object):
    test_date_order = [3, 1, 2]
    test_startdate_order = [3, 2, 1]
    YOUTUBE_EMBED = """
<iframe width="459" height="344" \
src="http://www.youtube.com/embed/d8bEU80gIzQ?feature=oembed" \
frameborder="0" allowfullscreen></iframe>
""".strip('\n')

    def __init__(self, portal):
        self.portal = portal
        for m in dir(self):
            if m.startswith('create_'):
                m = getattr(self, m)
                if callable(m):
                    with api.env.adopt_roles(['Manager']):
                        m()

    def _loadFile(self, name, size=0):
        """Load file from testing directory
        """
        path = os.path.join(package_home(globals()), 'tests/input', name)
        fd = open(path, 'rb')
        data = fd.read()
        fd.close()
        return data

    def _generate_jpeg(self, width, height):
        # Mandelbrot fractal
        # FB - 201003254
        # drawing area
        xa = -2.0
        xb = 1.0
        ya = -1.5
        yb = 1.5
        maxIt = 25  # max iterations allowed
        # image size
        image = Image.new('RGB', (width, height))
        c = complex(random.random() * 2.0 - 1.0, random.random() - 0.5)
        for y in range(height):
            zy = y * (yb - ya) / (height - 1) + ya
            for x in range(width):
                zx = x * (xb - xa) / (width - 1) + xa
                z = complex(zx, zy)
                for i in range(maxIt):
                    if abs(z) > 2.0:
                        break
                    z = z * z + c
                r = i % 4 * 64
                g = i % 8 * 32
                b = i % 16 * 16
                image.putpixel((x, y), b * 65536 + g * 256 + r)
        output = StringIO()
        image.save(output, format='PNG')
        return output.getvalue()

    def create_news(self):
        news_folder = api.content.create(
            type='Folder',
            title='News Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='News Item',
                title='New {0}'.format(i),
                description=(
                    'New {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                container=news_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
            o.setImage(self._generate_jpeg(50, 50))
        api.content.create(
            type='Collection',
            title='News Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'News Item'
            }],
            sort_on='created',
            container=news_folder
        )

    def create_events(self):
        events_folder = api.content.create(
            type='Folder',
            title='Events Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='Event',
                title='Event {0}'.format(i),
                description=(
                    'Event {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                startDate=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_startdate_order[i - 1])),
                container=events_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
        api.content.create(
            type='Collection',
            title='Events Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'Event'
            }],
            sort_on='created',
            container=events_folder
        )

    def create_images(self):
        images_folder = api.content.create(
            type='Folder',
            title='Images Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='Image',
                title='Image {0}'.format(i),
                description=(
                    'Image {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                rights='Image rights',
                container=images_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
            o.setImage(self._generate_jpeg(50, 50))
        api.content.create(
            type='Collection',
            title='Images Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'Image'
            }],
            sort_on='created',
            container=images_folder
        )

    def create_files(self):
        files_folder = api.content.create(
            type='Folder',
            title='Files Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='File',
                title='File {0}'.format(i),
                description=(
                    'File {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                container=files_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
            o.setFile(self._loadFile('lorem_ipsum.txt'))
            o.reindexObject()
        api.content.create(
            type='Collection',
            title='Files Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'File'
            }],
            sort_on='created',
            container=files_folder
        )

    def create_videos(self):
        videos_folder = api.content.create(
            type='Folder',
            title='Videos Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='sc.embedder',
                title='Video {0}'.format(i),
                description=(
                    'Video {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                url='http://www.youtube.com/watch?v=d8bEU80gIzQ',
                embed_html=self.YOUTUBE_EMBED,
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                container=videos_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
            o.image = NamedBlobImage(self._generate_jpeg(50, 50),
                                     'image/jpeg', u'image.jpg')
            o.reindexObject()
        api.content.create(
            type='Collection',
            title='Videos Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'sc.embedder'
            }],
            sort_on='created',
            container=videos_folder
        )

    def create_audios(self):
        audios_folder = api.content.create(
            type='Folder',
            title='Audios Folder',
            container=self.portal
        )
        for i in xrange(1, 4):
            o = api.content.create(
                type='Audio',
                title='Audio {0}'.format(i),
                description=(
                    'Audio {0} description - Lorem ipsum dolor sit amet, ' +
                    'consectetur adipiscing elit. Donec eleifend hendrerit ' +
                    'interdum.').format(i),
                creation_date=DateTime(
                    '2014/05/0{0} 14:23:38.334118 GMT-3'
                    .format(self.test_date_order[i - 1])),
                rights='Audio rights',
                container=audios_folder
            )
            o.setModificationDate(DateTime(
                '2014/05/0{0} 14:23:38.334118 GMT-3'
                .format(self.test_date_order[i - 1])
            ))
            mp3_file = api.content.create(
                type='MPEG Audio File',
                title='file.mp3',
                container=o
            )
            mp3_file.file = NamedBlobFile(self._loadFile('file.mp3'),
                                          'audio/mp3', u'file.mp3')
        api.content.create(
            type='Collection',
            title='Audios Collection',
            query=[{
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.is',
                u'v': u'Audio'
            }],
            sort_on='created',
            container=audios_folder
        )


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import brasil.gov.portlets
        self.loadZCML(package=brasil.gov.portlets)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'brasil.gov.portlets:testfixture')
        CreateTestContent(portal)
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='brasil.gov.portlets:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='brasil.gov.portlets:Functional')

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='brasil.gov.portlets:Robot',
)
