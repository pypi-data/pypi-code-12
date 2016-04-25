import re
import random
import datetime

def is_valid_pan(pan):
    if not re.match('^[0-9 ]+$', pan):
        return False

    card_digits=[int(c) for c in pan if c in '0123456789']

    if len(card_digits) < 13 or len(card_digits) > 19:
        return False

    card_digits.reverse()
    sum=0
    for i,c in enumerate(card_digits):
        if i % 2 == 1:
            sum+=[0, 2, 4, 6, 8, 1, 3, 5, 7, 9][c]
        else:
            sum+=c

    return sum % 10 == 0


class CardDate(object):
    """Generalised handling of credit card dates"""

    def __init__(self, strmonth):
        mo = re.match('([0-9]{2}(?:[0-9]{2})?)[^0-9a-zA-Z]([0-9]{2}(?:[0-9]{2}))', strmonth)
        if not mo:
            raise ValueError("Couldn't interpret card date")

        if len(mo.group(1)) == 4 and len(mo.group(2)) == 2:
            self.year = int(mo.group(1))
            self.month = int(mo.group(2))
        elif len(mo.group(1)) == 2 and len(mo.group(2)) == 4:
            self.year = int(mo.group(2))
            self.month = int(mo.group(1))
        elif len(mo.group(1)) == 2 and len(mo.group(2)) == 2:
            self.year = int(mo.group(2)) + 2000
            self.month = int(mo.group(1))

        if not hasattr(self, 'month') or self.month < 1 or self.month > 12:
            raise ValueError("Invalid card month")

    def format(self, formatstr):
        s = formatstr.replace('MM', '%02d'%self.month)
        s = s.replace('YYYY', '%04d'%self.year)
        return s.replace('YY', '%02d'%(self.year % 100))


class Card(object):
    """Encryptable object representing a Credit Card"""

    def __init__(self, card_type, pan, name_on_card, cv2, expiry_date, billing_address, billing_postcode, start_date=None, issue_number=None):
        self.card_type=card_type
        self.sensitive_data={
                'name_on_card': name_on_card,
                'expiry_date': CardDate(expiry_date),
                'billing_address': billing_address,
                'billing_postcode': billing_postcode,
        }
        self.setPAN(pan)

        if issue_number:
            self.sensitive_data['issue_number'] = issue_number

        if start_date:
            self.sensitive_data['start_date'] = CardDate(start_date)

        self.volatile_sensitive_data={'cv2': cv2}

    def getCardType(self):
        return self.card_type

    def setPAN(self, pan):
        ndigits=len([c for c in pan if c in '0123456789'])
        ostr=''
        digits = list(str(pan).strip())
        while ndigits > 4 and digits:
            d = digits.pop(0)
            if d in '0123456789':
                ostr+='X'
                ndigits-=1
            else:
                ostr+=d
        self.obfuscated_pan = ostr + ''.join(digits)
        self.sensitive_data['pan'] = pan

    def getObfuscatedPAN(self):
        return self.obfuscated_pan

    def getAddressLines(self, max_lines=None):
        """Cleans and returns the address as at most max_lines lines"""

        lines = []
        for l in self.sensitive_data['billing_address'].split('\n'):
            l = re.sub(r'^\s*(.*?)\s*,\s*', r'\1', l)       #remove whitespace and trailing comma, if any
            if l:
                lines.append(l)

        if max_lines is None or len(lines) <= max_lines:
            return lines

        # some APIs can only accept a limited number of address lines, so if there are any
        # more we will combine the remainder into one line
        return lines[:max_lines-1] + [', '.join(lines[max_lines-1:])]

    @staticmethod
    def generateTestCard(type):
        """Generates a card instance for testing.
        The PAN and expiry date will be random but valid; all other details are currently hard-coded."""

        if type == 'visa':
            pan = '4'
        else:
            pan = '54'

        while len(pan) < 15:
            pan += random.choice('0123456789')

        pan_digits=[int(c) for c in pan]
        pan_digits.reverse()

        sum=0
        for i, c in enumerate(pan_digits):
            if i % 2 == 0:
                sum += [0, 2, 4, 6, 8, 1, 3, 5, 7, 9][c]
            else:
                sum += c

        d = -sum % 10   # compute the check digit d such that (d + sum) % 10 == 0
        pan += str(d)

        expiry = datetime.date.today() + datetime.timedelta(days = max(31, int(random.normalvariate(365*2, 12))))
        expiry_date = '%02d-%04d'%(expiry.month, expiry.year)

        return Card(
                pan=pan,
                card_type=type,
                expiry_date=expiry_date,
                name_on_card='mr test test',
                cv2='123',
                billing_address='123 test street\ntestville',
                billing_postcode='ab12 3cd'
        )


from django import forms
if hasattr(forms, 'Manipulator'):
    try:
        from django import newforms as forms
    except ImportError:
        from django import forms

class CardNumberField(forms.RegexField):
    """Django forms field for validating credit card numbers
    using the Luhn checksum.

    """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 19
        kwargs['min_length'] = 13
        kwargs['regex'] = '^[0-9 ]*$'
        super(CardNumberField, self).__init__(*args, **kwargs)
        self.error_messages['invalid']=u'Please enter a valid credit card number'

    def clean(self, value):
        card_number=super(CardNumberField, self).clean(value)

        if not is_valid_pan(card_number):
            raise forms.ValidationError(self.error_messages['invalid'])

        return value
