import random
import re
from html import escape
from operator import attrgetter

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from natsort import natsorted
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle

from openslides.core.config import config
from openslides.utils.pdf import stylesheet

from .models import Category


def motions_to_pdf(pdf, motions):
    """
    Create a PDF with all motions.
    """
    motions = natsorted(motions, key=attrgetter('identifier'))
    all_motion_cover(pdf, motions)
    for motion in motions:
        pdf.append(PageBreak())
        motion_to_pdf(pdf, motion)


def motion_to_pdf(pdf, motion):
    """
    Create a PDF for one motion.
    """
    identifier = ''
    if motion.identifier:
        identifier = ' %s' % motion.identifier
    pdf.append(Paragraph('%s%s: %s' % (_('Motion'), identifier, escape(motion.title)), stylesheet['Heading1']))

    motion_data = []

    # submitter
    cell1a = []
    cell1a.append(Spacer(0, 0.2 * cm))
    cell1a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font>" % _("Submitter"),
                            stylesheet['Heading4']))
    cell1b = []
    cell1b.append(Spacer(0, 0.2 * cm))
    for submitter in motion.submitters.all():
        cell1b.append(Paragraph(str(submitter), stylesheet['Normal']))
    motion_data.append([cell1a, cell1b])

    # TODO: choose this in workflow
    if motion.state.allow_submitter_edit:
        # Cell for the signature
        cell2a = []
        cell2b = []
        cell2a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font>" %
                                _("Signature"), stylesheet['Heading4']))
        cell2b.append(Paragraph(42 * "_", stylesheet['Signaturefield']))
        cell2b.append(Spacer(0, 0.1 * cm))
        cell2b.append(Spacer(0, 0.2 * cm))
        motion_data.append([cell2a, cell2b])

    # supporters
    if config['motions_min_supporters']:
        cell3a = []
        cell3b = []
        cell3a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font><seqreset id='counter'>"
                                % _("Supporters"), stylesheet['Heading4']))
        supporters = motion.supporters.all()
        for supporter in supporters:
            cell3b.append(Paragraph("<seq id='counter'/>.&nbsp; %s" % str(supporter),
                                    stylesheet['Normal']))
        cell3b.append(Spacer(0, 0.2 * cm))
        motion_data.append([cell3a, cell3b])

    # Motion state
    cell4a = []
    cell4b = []
    cell4a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font>" % _("State"),
                            stylesheet['Heading4']))
    cell4b.append(Paragraph(_(motion.state.name), stylesheet['Normal']))
    motion_data.append([cell4a, cell4b])

    # Version number
    if motion.versions.count() > 1:
        version = motion.get_active_version()
        cell5a = []
        cell5b = []
        cell5a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font>" % _("Version"),
                                stylesheet['Heading4']))
        cell5b.append(Paragraph("%s" % version.version_number, stylesheet['Normal']))
        motion_data.append([cell5a, cell5b])

    # voting result
    polls = []
    for poll in motion.polls.all():
        if not poll.has_votes():
            continue
        polls.append(poll)

    if polls:
        cell6a = []
        cell6b = []
        cell6a.append(Paragraph("<font name='Ubuntu-Bold'>%s:</font>" %
                                _("Vote result"), stylesheet['Heading4']))
        ballotcounter = 0
        for poll in polls:
            ballotcounter += 1
            option = poll.get_options()[0]
            yes, no, abstain = (option['Yes'], option['No'], option['Abstain'])
            valid, invalid, votescast = ('', '', '')
            if poll.votesvalid is not None:
                valid = "<br/>%s: %s" % (_("Valid votes"), poll.print_votesvalid())
            if poll.votesinvalid is not None:
                invalid = "<br/>%s: %s" % (_("Invalid votes"), poll.print_votesinvalid())
            if poll.votescast is not None:
                votescast = "<br/>%s: %s" % (_("Votes cast"), poll.print_votescast())
            if len(polls) > 1:
                cell6b.append(Paragraph("%s. %s" % (ballotcounter, _("Vote")),
                                        stylesheet['Bold']))
            cell6b.append(Paragraph(
                "%s: %s <br/> %s: %s <br/> %s: %s <br/> %s %s %s" %
                (_("Yes"), yes, _("No"), no, _("Abstain"), abstain, valid, invalid, votescast),
                stylesheet['Normal']))
            cell6b.append(Spacer(0, 0.2 * cm))
        motion_data.append([cell6a, cell6b])

    # Creating Table
    table = Table(motion_data)
    table._argW[0] = 4.5 * cm
    table._argW[1] = 11 * cm
    table.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 1, colors.black),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    pdf.append(table)
    pdf.append(Spacer(0, 1 * cm))

    # motion title
    pdf.append(Paragraph(escape(motion.title), stylesheet['Heading3']))

    # motion text
    convert_html_to_reportlab(pdf, motion.text)
    pdf.append(Spacer(0, 1 * cm))

    # motion reason
    if motion.reason:
        pdf.append(Paragraph(_("Reason") + ":", stylesheet['Heading3']))
        convert_html_to_reportlab(pdf, motion.reason)
    return pdf


def convert_html_to_reportlab(pdf, text):
    # parsing and replacing not supported html tags for reportlab...
    soup = BeautifulSoup(text, "html5lib")

    # number ol list elements
    ols = soup.find_all('ol')
    for ol in ols:
        counter = 0
        for li in ol.children:
            if li.name == 'li':
                # if start attribute is available set counter for first list element
                if li.parent.get('start') and not li.find_previous_sibling():
                    counter = int(ol.get('start'))
                else:
                    counter += 1
                if li.get('value'):
                    counter = li.get('value')
                else:
                    li['value'] = counter

    # read all list elements...
    for element in soup.find_all('li'):
        # ... and replace ul list elements with <para><bullet>&bull;</bullet>...<para>
        if element.parent.name == "ul":
            # nested lists
            if element.ul or element.ol:
                for i in element.find_all('li'):
                    element.insert_before(i)
                element.clear()
            else:
                element.name = "para"
                bullet_tag = soup.new_tag("bullet")
                bullet_tag.string = u"•"
                element.insert(0, bullet_tag)
        # ... and replace ol list elements with <para><bullet><seqreset id="%id" base="value"><seq id="%id"></seq>.</bullet>...</para>
        if element.parent.name == "ol":
            counter = None
            # set list id if element is the first of numbered list
            if not element.find_previous_sibling():
                id = random.randrange(0, 101)
                if element.parent.get('start'):
                    counter = element.parent.get('start')
            if element.get('value'):
                counter = element.get('value')
            # nested lists
            if element.ul or element.ol:
                nested_list = element.find_all('li')
                for i in reversed(nested_list):
                    element.insert_after(i)

            element.attrs = {}
            element.name = "para"
            element.insert(0, soup.new_tag("bullet"))
            element.bullet.insert(0, soup.new_tag("seq"))
            element.bullet.seq['id'] = id
            if counter:
                element.bullet.insert(0, soup.new_tag("seqreset"))
                element.bullet.seqreset['id'] = id
                element.bullet.seqreset['base'] = int(counter) - 1
            element.bullet.insert(2, ".")
    # remove tags which are not supported by reportlab (replace tags with their children tags)
    for tag in soup.find_all('ul'):
        tag.unwrap()
    for tag in soup.find_all('ol'):
        tag.unwrap()
    for tag in soup.find_all('li'):
        tag.unwrap()

    # use tags which are supported by reportlab
    # replace <s> to <strike>
    for tag in soup.find_all('s'):
        tag.name = "strike"

    # replace <del> to <strike>
    for tag in soup.find_all('del'):
        tag.name = "strike"

    for tag in soup.find_all('a'):
        # remove a tags without href attribute
        if not tag.get('href'):
            tag.extract()
    for tag in soup.find_all('img'):
        # remove img tags without src attribute
        if not tag.get('src'):
            tag.extract()

    # replace style attributes in <span> tags
    for tag in soup.find_all('span'):
        if tag.get('style'):
            # replace style attribute "text-decoration: line-through;" to <strike> tag
            if 'text-decoration: line-through' in str(tag['style']):
                strike_tag = soup.new_tag("strike")
                strike_tag.string = tag.string
                tag.replace_with(strike_tag)
            # replace style attribute "text-decoration: underline;" to <u> tag
            elif 'text-decoration: underline' in str(tag['style']):
                u_tag = soup.new_tag("u")
                u_tag.string = tag.string
                tag.replace_with(u_tag)
            # replace style attribute "color: #xxxxxx;" to "<font backcolor='#xxxxxx'>...</font>"
            elif 'background-color: ' in str(tag['style']):
                font_tag = soup.new_tag("font")
                color = re.findall('background-color: (.*?);', str(tag['style']))
                if color:
                    font_tag['backcolor'] = color
                if tag.string:
                    font_tag.string = tag.string
                tag.replace_with(font_tag)
            # replace style attribute "color: #xxxxxx;" to "<font color='#xxxxxx'>...</font>"
            elif 'color: ' in str(tag['style']):
                font_tag = soup.new_tag("font")
                color = re.findall('color: (.*?);', str(tag['style']))
                if color:
                    font_tag['color'] = color
                if tag.string:
                    font_tag.string = tag.string
                tag.replace_with(font_tag)
            else:
                tag.unwrap()
        else:
            tag.unwrap()
    # print paragraphs with numbers
    text = soup.body.contents
    paragraph_number = 1
    for paragraph in text:
        paragraph = str(paragraph)
        # ignore empty paragraphs (created by newlines/tabs of ckeditor)
        if paragraph == '\n' or paragraph == '\n\n' or paragraph == '\n\t':
            continue
        if "<pre>" in paragraph:
            txt = paragraph.replace('\n', '<br/>').replace(' ', '&nbsp;')
            if config["motions_pdf_paragraph_numbering"]:
                pdf.append(Paragraph(txt, stylesheet['InnerMonotypeParagraph'], str(paragraph_number)))
                paragraph_number += 1
            else:
                pdf.append(Paragraph(txt, stylesheet['InnerMonotypeParagraph']))
        elif "<para>" in paragraph:
            pdf.append(Paragraph(paragraph, stylesheet['InnerListParagraph']))
        elif "<seqreset" in paragraph:
            pass
        elif "<h1>" in paragraph:
            pdf.append(Paragraph(paragraph, stylesheet['InnerH1Paragraph']))
        elif "<h2>" in paragraph:
            pdf.append(Paragraph(paragraph, stylesheet['InnerH2Paragraph']))
        elif "<h3>" in paragraph:
            pdf.append(Paragraph(paragraph, stylesheet['InnerH3Paragraph']))
        else:
            if config["motions_pdf_paragraph_numbering"]:
                pdf.append(Paragraph(paragraph, stylesheet['InnerParagraph'], str(paragraph_number)))
                paragraph_number += 1
            else:
                pdf.append(Paragraph(paragraph, stylesheet['InnerParagraph']))


def all_motion_cover(pdf, motions):
    """
    Create a coverpage for all motions.
    """
    pdf.append(Paragraph(escape(config["motions_pdf_title"]), stylesheet['Heading1']))

    preamble = escape(config["motions_pdf_preamble"])
    if preamble:
        pdf.append(Paragraph("%s" % preamble.replace('\r\n', '<br/>'), stylesheet['Paragraph']))

    pdf.append(Spacer(0, 0.75 * cm))

    # list of categories
    categories = False
    for i, category in enumerate(Category.objects.all()):
        categories = True
        if i == 0:
            pdf.append(Paragraph(_("Categories"), stylesheet['Heading2']))
        pdf.append(Paragraph("%s &nbsp;&nbsp; %s" % (escape(category.prefix), escape(category.name)), stylesheet['Paragraph']))
    if categories:
        pdf.append(PageBreak())

    # list of motions
    if not motions:
        pdf.append(Paragraph(_("No motions available."), stylesheet['Heading3']))
    else:
        for motion in motions:
            identifier = ''
            if motion.identifier:
                identifier = ' %s' % motion.identifier
            pdf.append(Paragraph('%s%s: %s' % (_('Motion'), identifier, escape(motion.title)), stylesheet['Heading3']))


def motion_poll_to_pdf(pdf, poll):
    circle = "*"  # = Unicode Character 'HEAVY LARGE CIRCLE' (U+2B55)
    cell = []
    cell.append(Spacer(0, 0.8 * cm))
    cell.append(Paragraph(_("Motion No. %s") % poll.motion.identifier, stylesheet['Ballot_title']))
    cell.append(Paragraph(poll.motion.title, stylesheet['Ballot_subtitle']))
    cell.append(Spacer(0, 0.5 * cm))
    cell.append(Paragraph("<font name='circlefont' size='15'>%s</font> <font name='Ubuntu'>%s</font>"
                % (circle, _("Yes")), stylesheet['Ballot_option']))
    cell.append(Paragraph("<font name='circlefont' size='15'>%s</font> <font name='Ubuntu'>%s</font>"
                % (circle, _("No")), stylesheet['Ballot_option']))
    cell.append(Paragraph("<font name='circlefont' size='15'>%s</font> <font name='Ubuntu'>%s</font>"
                % (circle, _("Abstain")), stylesheet['Ballot_option']))
    data = []
    # get ballot papers config values
    ballot_papers_selection = config["motions_pdf_ballot_papers_selection"]
    ballot_papers_number = config["motions_pdf_ballot_papers_number"]

    # set number of ballot papers
    if ballot_papers_selection == "NUMBER_OF_DELEGATES":
        if 'openslides.users' in settings.INSTALLED_APPS:
            from openslides.users.models import Group
            try:
                if Group.objects.get(pk=3):
                    number = get_user_model().objects.filter(groups__pk=3).count()
            except Group.DoesNotExist:
                number = 0
        else:
            number = 0
    elif ballot_papers_selection == "NUMBER_OF_ALL_PARTICIPANTS":
        number = int(get_user_model().objects.count())
    else:  # ballot_papers_selection == "CUSTOM_NUMBER"
        number = int(ballot_papers_number)
    number = max(1, number)

    # print ballot papers
    if number > 0:
        # TODO: try [cell, cell] * (number / 2)
        for user in range(int(number / 2)):
            data.append([cell, cell])
        rest = number % 2
        if rest:
            data.append([cell, ''])
        t = Table(data, 10.5 * cm, 7.42 * cm)
        t.setStyle(TableStyle(
            [('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
             ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        pdf.append(t)
