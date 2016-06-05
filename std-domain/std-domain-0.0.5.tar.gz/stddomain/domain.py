import idna
import tldextract


class Domain(object):
    """
    Standardized Domain object, with full support for IDNs
    and punycodes.
    """

    def __init__(self, domain_name):
        """
        This function creates and parses the domain name
        provided by the application.

        First we should detect if the domain given is an
        IDN, and if so, parse the domain correctly and give
        it a punycode and it's correct UTF-8 representation.

        :param domain_name: The domain name to parse (can by puny or IDN)
        """

        is_idn = False

        # Let's make sure that it's in a str representation
        if type(domain_name) == bytes:
            domain_name = domain_name.decode('utf-8')

        # Bug fix: Let's check both parts of the domain individually,
        # so if it's /really/ weird and a mix of IDN and punycode,
        # we still correct it.
        domain_parts = domain_name.split('.')

        for i in range(len(domain_parts)):
            if 'xn-' in domain_parts[i]:
                is_idn = True
                domain_parts[i] = idna.decode(domain_parts[i])

        domain = domain_name
        idn = idna.decode(domain)

        # If it can't be converted to ASCII, it's an IDN
        try:
            domain_name.encode('ascii')
        except UnicodeEncodeError:
            is_idn = True
            domain = idna.encode(domain_name).decode('utf-8')
            idn = domain_name

        if domain is None:
            domain = domain_name

        self.__domain_obj = tldextract.extract(domain)
        self.__is_idn = is_idn
        self.__idn_obj = tldextract.extract(idn) if is_idn else None

    @property
    def domain(self):
        """
        This function will return the domain name.

        If the domain is an IDN, then it will return
        the punycode version of the domain.

        If you want to retrieve the international version,
        use the `idn` attribute to get the UTF-8 version.


        :return: The domain in punycode format
        """
        return '.'.join([self.get_domain(), self.get_tld()])

    @property
    def idn(self):
        """
        This function returns the domain name in a UTF-8
        representation in the domain's natural language
        if it is an IDN, otherwise it will return the
        domain in its normal alphanumeric format.

        :return: The domain in its natural language
        """

        if not self.__is_idn:
            return self.domain

        return '.'.join([self.get_domain(True), self.get_tld(True)])

    @property
    def is_idn(self):
        """
        This function checks if the domain is an IDN.

        :return: Domain is an IDN
        """
        return self.__is_idn

    def get_domain(self, idn=False):
        """
        This function returns the SLD (secondary level domain), or
        the unique identifier in a domain name.

        Example:
            [something].[com]
            ^ SLD       ^ TLD

        :param idn: Defaults to **False**. Determines if it should return
                    the extension in its native language as Unicode.
        """
        if idn and self.is_idn:
            return self.__idn_obj.domain

        return self.__domain_obj.domain

    def get_tld(self, idn=False):
        """
        This function returns the top level domains, or the extension,
        of the domain name. If you pass idn=True, then it will return
        the Unicode representation.

        :param idn: Defaults to **False**. Determines if it should return
                    the extension in its native language as Unicode.
        """
        if idn and self.is_idn:
            # NOTE: The idna library doesn't handle TLD IDNs correctly,
            # so we're going to do them outselves.
            suffix = self.__idn_obj.suffix
            tld_punycode = suffix.encode('idna').decode('idna')

            return tld_punycode

        return self.__domain_obj.suffix

    def __str__(self):
        """
        This function should always return the punycode
        representation of the domain, if it's not an IDN,
        just return the domain name normally.

        :return: The string representation of this domain
        """
        return self.domain

    def __repr__(self):
        """
        The representative string of this object is the exact
        same as the __str__() returns, so let's just alias this
        function to it.

        :return: The string representation of this domain
        """
        return self.__str__()
