import ldap
from ldap.ldapobject import ReconnectLDAPObject
from ldap.controls import SimplePagedResultsControl


class PagedResultsSearchObject:
    page_size = 500

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None,
                           attrsonly=0, serverctrls=None, clientctrls=None, timeout=-1,
                           sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.

        This is non-sense for really large results sets which you would like
        to process one-by-one
        """

        while True:  # loop for reconnecting if necessary
            req_ctrl = SimplePagedResultsControl(True, size=self.page_size, cookie='')
            try:
                # Send first search request
                msgid = self.search_ext(
                    base,
                    scope,
                    filterstr=filterstr,
                    attrlist=attrlist,
                    attrsonly=attrsonly,
                    serverctrls=(serverctrls or [])+[req_ctrl],
                    clientctrls=clientctrls,
                    timeout=timeout,
                    sizelimit=sizelimit
                )


                while True:
                    rtype, rdata, rmsgid, rctrls = self.result3(msgid)
                    for result in rdata:
                        yield result
                    # Extract the simple paged results response control
                    pctrls = [
                        c
                        for c in rctrls
                        if c.controlType == SimplePagedResultsControl.controlType
                    ]
                    if pctrls and pctrls[0].cookie:
                        # Copy cookie from response control to request control
                        req_ctrl.cookie = pctrls[0].cookie
                        msgid = self.search_ext(
                            base,
                            scope,
                            filterstr=filterstr,
                            attrlist=attrlist,
                            attrsonly=attrsonly,
                            serverctrls=(serverctrls or [])+[req_ctrl],
                            clientctrls=clientctrls,
                            timeout=timeout,
                            sizelimit=sizelimit
                        )
                        continue
                    break  # no more pages available
            except ldap.SERVER_DOWN:
                self.reconnect(self._uri)
            else:
                break


class PagedLDAPObject(ReconnectLDAPObject, PagedResultsSearchObject):
    pass
