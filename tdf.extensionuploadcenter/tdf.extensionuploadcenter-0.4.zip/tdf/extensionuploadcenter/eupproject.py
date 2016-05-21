from tdf.extensionuploadcenter import MessageFactory as _
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from plone.dexterity.browser.view import DefaultView
from Acquisition import aq_inner
from plone import api
from collective import dexteritytextindexer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides
import re
from plone.namedfile.field import NamedBlobImage
from zope.interface import Invalid, invariant
from plone import api
from tdf.extensionuploadcenter.euprelease import IEUpRelease
from tdf.extensionuploadcenter.eupreleaselink import IEUpReleaseLink
from z3c.form import validator
from plone.uuid.interfaces import IUUID
from plone.directives import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from Products.validation import V_REQUIRED





def vocabCategories(context):
    # For add forms

    # For other forms edited or displayed
    from tdf.extensionuploadcenter.eupcenter import IEUpCenter
    while context is not None and not IEUpCenter.providedBy(context):
        #context = aq_parent(aq_inner(context))
        context = context.__parent__

    category_list = []
    if context is not None and context.available_category:
        category_list = context.available_category

    terms = []
    for value in category_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))

    return SimpleVocabulary(terms)
directlyProvides(vocabCategories, IContextSourceBinder)



def isNotEmptyCategory(value):
    if not value:
        raise Invalid(u'You must choose at least one category for your project.')
    return True




checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match

def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True


class ProvideScreenshotLogo(Invalid):
    __doc__ =  _(u"Please add a Screenshot or a Logo to your project")



class MissingCategory(Invalid):
    __doc__ = _(u"You have not chosen a category for the project")



class IEUpProject(model.Schema):


    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Project Title - minimum 5 and maximum 50 characters"),
        min_length=5,
        max_length=50
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u"Project Summary"),
    )

    dexteritytextindexer.searchable('details')
    form.primary('details')
    details = RichText(
        title=_(u"Full Project Description"),
        required=False
    )



    dexteritytextindexer.searchable('category_choice')
    form.widget(category_choice=CheckBoxFieldWidget)
    category_choice = schema.List(
        title=_(u"Choose your categories"),
        description=_(u"Please select the appropriate categories (one or more) for your project."),
        value_type=schema.Choice(source=vocabCategories),
        constraint = isNotEmptyCategory,
        required=True
    )


    contactAddress=schema.ASCIILine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        constraint=validateEmail
    )

    homepage=schema.URI(
        title=_(u"Homepage"),
        description=_(u"If the project has an external home page, enter its URL (example: 'http://www.mysite.org')."),
        required=False
    )

    documentation_link=schema.URI(
        title=_(u"URL of documentation repository "),
        description=_(u"If the project has externally hosted documentation, enter its URL (example: 'http://www.mysite.org')."),
        required=False
    )

    project_logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(u"Add a logo for the project (or organization/company) by clicking the 'Browse' button."),
        required=False,
    )

    screenshot = NamedBlobImage(
        title=_(u"Screemshot of the Extension"),
        description=_(u"Add a screenshot by clicking the 'Browse' button."),
        required=False,
    )


    @invariant
    def missingScreenshotOrLogo(data):
        if not data.screenshot and not data.project_logo:
            raise ProvideScreenshotLogo(_(u'Please add a Screenshot or a Logo to your project page'))




def notifyProjectManager (eupproject, event):
    api.portal.send_email(
        recipient ="%s" % (eupproject.contactAddress),
        sender = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org'),
        subject = "Your Project %s" % (eupproject.title),
        body = "The status of your LibreOffice extension project changed"
    )

def notifyProjectManagerReleaseAdd (eupproject, event):
    api.portal.send_email(
        recipient ="%s" % (eupproject.contactAddress),
        sender = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org'),
        subject = "Your Project %s: new Release added"  % (eupproject.title),
        body = "A new release was added to your project: '%s'" % (eupproject.title),
         )

def notifyProjectManagerReleaseLinkedAdd (eupproject, event):
    api.portal.send_email(
        recipient ="%s" % (eupproject.contactAddress),
        sender = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org'),
        subject = "Your Project %s: new linked Release added"  % (eupproject.title),
        body = "A new linked release was added to your project: '%s'" % (eupproject.title),
         )


class ValidateEUpProjectUniqueness(validator.SimpleFieldValidator):
    #Validate site-wide uniqueness of project titles.


    def validate(self, value):
        # Perform the standard validation first
        super(ValidateEUpProjectUniqueness, self).validate(value)

        if value is not None:
            catalog = api.portal.get_tool(name='portal_catalog')
            results = catalog({'Title': value,
                               'object_provides': IEUpProject.__identifier__})

            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The project title is already in use"))

validator.WidgetValidatorDiscriminators(
    ValidateEUpProjectUniqueness,
    field=IEUpProject['title'],
)


class EUpProjectView(DefaultView):


    def all_releases(self):
        """Get a list of all releases, ordered by version, starting with the latest.
        """

        catalog = api.portal.get_tool(name='portal_catalog')
        current_path = "/".join(self.context.getPhysicalPath())
        res = catalog.searchResults(
            portal_type = ('tdf.extensionuploadcenter.euprelease', 'tdf.extensionuploadcenter.eupreleaselink'),
            path =current_path,
            sort_on = 'id',
            sort_order = 'reverse')
        return [r.getObject() for r in res]


    def latest_release(self):
        """Get the most recent final release or None if none can be found.
        """

        context = self.context
        res = None
        catalog = api.portal.get_tool('portal_catalog')

        res = catalog.searchResults(
            portal_type = ('tdf.extensionuploadcenter.euprelease', 'tdf.extensionuploadcenter.eupreleaselink'),
            path = '/'.join(context.getPhysicalPath()),
            review_state = 'final',
            sort_on = 'id',
            sort_order = 'reverse')

        if not res:
            return None
        else:
            return res[0].getObject()


    def latest_release_date(self):
        """Get the date of the latest release
        """

        latest_release = self.latest_release()
        if latest_release:
            return self.context.toLocalizedTime(latest_release.effective())
        else:
            return None



