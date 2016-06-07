# -*- coding: utf-8 -*-

import urllib2
import urllib
import re

from datetime import date

from lxml.html import document_fromstring

from courier import Courier, Statuses, logger
from exceptions import *

class CP(Courier):
    '''todo:'''

    extension_url = "https://www.postaonline.cz/sluzby-pri-dodani/prodlouzeni-ulozni-doby-pro-vyzvednuti-jiz-ulozene-zasilky"
    tracking_url = "https://www.postaonline.cz/trackandtrace/-/zasilka/cislo?parcelNumbers="

    tracknum_regexes = ['.*']
    extendable = True

    def __init__(self, tracknum):
        super(CP, self).__init__(tracknum)

        self.cp_page_document = document_fromstring(self.cp_page)

    def is_tracknum_valid(self):
        """Is self.tracknum valid?"""

        errorbox = self.cp_page_document.cssselect('.errorbox')
        errorclass = self.cp_page_document.cssselect('.error')

        return (len(errorbox) == 0 and len(errorclass) == 0)

    def is_extended(self):
        """Was delivery time already extended?"""
        try:
            for row in self.get_change_log_table():
                if row["event_name"] == u"Přijetí požadavku adresáta - prodloužení úložní doby zásilky.":
                    return True
            return False
        except IndexError:
            raise UnknownScrapingException('Unknown error. Is tracknum valid?')

    def get_form_info(self, recipient_name, recipient_address):
        try:
            initial_post = self.get_change_log_table()[-1]
            for event in self.get_change_log_table():
                if event.get("event_place"):
                    final_post = event
                    break
        except:
            raise UnknownScrapingException
        # xxx: is this really working?

        form = {}

        form['recipient'] = recipient_name
        form['address'] = recipient_address

        if self.tracknum[:2] == "RR":
            form['service'] = u"Doporučená zásilka"
        elif self.tracknum[:2] == "DR":
            form['service'] = u"Balík Do ruky"

        if initial_post['event_place']:
            form['posting_office'] = initial_post['event_place']
        else:
            form['posting_office'] = u"Depo Praha 701"

        form['posting_number'] = self.tracknum

        form['po_zip'] = final_post['event_zip']
        form['post_office'] = final_post['event_place']

        form['email'] = self.email

        return form

    def get_encode_utf8_form_params(self, recipient_name, recipient_address):
        # xxx: do we need try..except here?
        form_params = self.get_form_info(recipient_name, recipient_address)
        str_form_params = {}
        for k, v in form_params.iteritems():
            try:
                str_form_params[k] = v.encode('utf-8')
            except UnicodeEncodeError:
                str_form_params[k] = v

        return urllib.urlencode(str_form_params)

    def extend_storage(self, recipient_name, recipient_address):
        # Get cookies from form_page
        response = urllib2.urlopen(self.extension_url)
        cookies = response.headers['set-cookie']

        # Get url for time_extending post request
        page = response.read()
        doc = document_fromstring(page)
        post_url = doc.forms[0].action

        # Make request
        data = self.get_encode_utf8_form_params(recipient_name, recipient_address)

        logger.info("Extending delivery " + self.tracknum)
        logger.info("Form data : ")
        logger.info(str(data))

        request = urllib2.Request(post_url, data)

        request.headers['Cookie'] = cookies
        request.headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0"
        # request.headers['Connection'] = 'keep-alive'
        # request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        # request.headers['Accept-Encoding'] = 'deflate'
        # request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        # todo: try it without these headers

        logger.info("Request headers")
        logger.info(str(request.headers))

        logger.info("Request url")
        logger.info(post_url)

        response = urllib2.urlopen(request)
        html = response.read()
        document = document_fromstring(html)

        try:
            # xxx:
            answer = document.cssselect('.article-content')[0].getchildren()[0].text
            return re.findall('\d.*', answer)[0][:-1]
        except:
            type, value, traceback = sys.exc_info()
            raise BadFormDataException, 'Unknown error while submitting form', traceback


    def get_status(self):
        """State of delivery"""

        try:
            last_event = self.get_change_log_table()[0]
        except IndexError:
            logger.warning(u"Unknown shipping state")
            return Statuses.UNKNOWN

        if last_event in [
                u"Dodání zásilky.",
                u"Zásilka dodána do domovní schrány.",
                u"Uložení zásilky do dodávací schrány.",
                u"Uložení zásilky - adresát má P.O.Box."
                u"Zásilka dodána do domovní schrány."]:
            return Statuses.DELIVERED
        elif last_event in [
                u"Podání zásilky.",
                u"E-mail adresátovi - podání zásilky.",
                u"E-mail adresátovi - termín doručení zásilky.",
                u"SMS zpráva adresátovi - termín doručení zásilky.",
                u"SMS zpráva adresátovi - podání zásilky."]:
            return Statuses.SENT
        elif last_event in [
                u"Uložení zásilky - adresát nezastižen.",
                u"Uložení zásilky.",
                u"SMS zpráva adresátovi - neúspěšný pokus o doručení a uložení zásilky.",
                u"SMS zpráva adresátovi - blížící se konec úložní doby.",
                u"Uložení zásilky na žádost adresáta.",
                u"Přijetí požadavku adresáta - prodloužení úložní doby zásilky.",
                u"E-mail adresátovi - neúspěšný pokus o doručení a uložení zásilky.",
                u"Uložení zásilky - sjednaná výhrada odnášky.",
                u"E-mail adresátovi - neúspěšný pokus o doručení a uložení zásilky.",
                u"Uložení zásilky - adresát má P.O.Box.",
                u"Uložení zásilky - neuhrazená dobírka.",
                u"E-mail adresátovi - blížící se konec úložní doby."]:
            return Statuses.STORED
        elif last_event in [
                u"Doručování zásilky.",
                u"Doručování zásilky v rámci odpoledního doručování.",
                u"Příprava zásilky k doručení.",
                u"Vstup zásilky na SPU.",
                u"SMS zpráva adresátovi - důvody neučinění pokusu o doručení zásilky.",
                u"Příprava zásilky pro opakované doručení.",
                u"Příprava zásilky k doručení - pokus o doručení neuskutečněn z technických důvodů na straně České pošty.",
                u"Příprava zásilky pro opakované doručení.",
                u"Přeprava zásilky k dodací poště."]:
            return Statuses.DELIVERING
        elif last_event in [
                u"Vrácení zásilky odesílateli.",
                u"Odeslání zásilky zpět odesílateli - překážka na straně adresáta.",
                u"Odeslání zásilky zpět odesílateli - adresát zásilku nevyzvedl ve stanovené odběrní lhůtě.",
                u"Odeslání zásilky zpět odesílateli - adresát na uvedené adrese neznámý.",
                u"Odeslání zásilky zpět odesílateli - adresát odmítl zásilku převzít."]:
            return Statuses.RETURN_TO_SENDER
        elif last_event in [u"Pro další informace volejte naši infolinku - tel. 800 177 889."]:
            return Statuses.UNKNOWN
        
        logger.warning(u"Unknown shipping state : '" + last_event + "'")

        return Statuses.UNKNOWN

    def get_change_log_table(self):
        """Returns changelog of package, from newest to oldest."""

        rows = []

        try:
            tables = self.cp_page_document.cssselect('table.datatable2')
            table_with_changes = tables[1]
            table_rows = table_with_changes.cssselect('tr')
            del table_rows[0]

            for row in table_rows:
                row_dict = {}

                columns = row.cssselect('td')

                row_dict["event_date"] = columns[0].text_content()
                row_dict["event_name"] = columns[1].text_content()
                row_dict["event_zip"] = columns[2].text_content()
                row_dict["event_place"] = columns[3].text_content()

                rows.append(row_dict)
            return rows

        except:
            raise UnknownScrapingException()

    def date_from_string(self, date_string):
        """22.5.2015 -> date object"""

        date_list = date_string.split(".")

        return date(int(date_list[2]), int(
            date_list[1]), int(date_list[0]))

    def get_delivery_detail_by_filter(self, content_filter):
        """Vraci ruzne detaily o zasilce"""

        details = self.cp_page_document.cssselect(
            'div.item-detail-content ul li')

        for detail in details:
            if content_filter in detail.text_content():
                detail_split_string = detail.text_content().split(":")
                detail_string = detail_split_string[1].strip()

                return detail_string.replace(",", "")

        return None

    # def get_delivery_type(self):

    #     content_filter = u"Typ zásilky"

    #     detail_string = self.get_delivery_detail_by_filter(content_filter)

    #     return detail_string

    def get_expiration_date(self):
        """Do kdy je zasilka ulozena ?"""

        detail_string = self.get_delivery_detail_by_filter(u"Zásilka uložena do")

        if not detail_string:
            # Some packages do not have expiration date fill out
            logger.info("Package " + self.tracknum +
                        " doesn't have expiration date")
            return None

        return self.date_from_string(detail_string)
