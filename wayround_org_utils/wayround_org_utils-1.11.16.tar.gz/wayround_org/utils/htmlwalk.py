
import urllib.request
import logging
import os.path

import lxml.html

import wayround_org.utils.directory
import wayround_org.utils.path
import wayround_org.utils.uri


class HTMLWalk:

    def __init__(self, domain, scheme='https', port=None):
        self._scheme = scheme
        self._port = port
        self._domain = domain
        self._tree = wayround_org.utils.directory.Directory()
        self._searched_paths = dict()
        return

    def get_tree(self):
        return self._tree

    def _listdir(self, path, variant=0):

        if isinstance(path, str):
            path = wayround_org.utils.path.split(
                path,
                end_slash='eat'
                )

        if variant == 0:
            ret = None
        elif variant == 1:
            ret = None, None
        else:
            raise Exception("programming error")

        ctpp_res = self.check_tree_path_population(path)
        if ctpp_res is True:
            directory = self._tree.getpath(path)
            if directory is not None:
                if variant == 0:
                    ret = directory.listdir()
                elif variant == 1:
                    ret = directory.listdir2()
                else:
                    raise Exception("programming error")

        return ret

    def listdir(self, path):
        return self._listdir(path, variant=0)

    def listdir2(self, path):
        return self._listdir(path, variant=1)

    def search_objects(self, path_lst):

        if not isinstance(path_lst, list):
            raise TypeError("`path_lst' must be str list")

        path_lst_j = wayround_org.utils.path.join(path_lst)

        if path_lst_j in self._searched_paths:
            ret = self._searched_paths[path_lst_j]
        else:

            ret = None

            port_str = ''
            if self._port is not None:
                port_str = ':{}'.format(self._port)

            uri = '{scheme}://{domain}{port}{path}'.format(
                scheme=self._scheme,
                domain=self._domain,  # .encode('idna').decode('utf-8'),
                port=port_str,
                path='/{}/'.format(
                    urllib.request.quote(path_lst_j, '/').strip('/')
                    )
                )

            # print("uri: {}".format(uri))

            try:
                uri_req = urllib.request.Request(
                    uri,
                    # tell thanks to https://www.burghardt.pl/files/ admin
                    # for making Me doing this. 15 Apr 2016 MSK
                    headers={
                        'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64; rv:45.0)'
                        ' Gecko/20100101 Firefox/45.0'
                        }
                    )
                page = urllib.request.urlopen(uri_req)
                page_text = page.read()
                page.close()
            except urllib.error.HTTPError:
                logging.exception("error. uri: {}".format(uri))
                page_text = None
            except urllib.error.URLError:
                logging.exception("error. uri: {}".format(uri))
                page_text = None

            if page_text is not None:
                page = lxml.html.document_fromstring(page_text)

                hrefs = set()

                for i in page.findall('.//a'):
                    hrefs.add(urllib.request.unquote(i.get('href', '')))

                hrefs -= set([''])

                ret = list(hrefs)
                ret.sort()

            self._searched_paths[path_lst_j] = ret

        return ret

    def populate_tree_from_search_objects_result(self, path_lst):

        # NOTE: path_lst slashes are stripped in _listdir method
        '''
        print(
            "populate_tree_from_search_objects_result path_lst {}".format(
                path_lst
                )
            )
        '''

        search_objects_res = self.search_objects(path_lst)

        '''
        print(
            "populate_tree_from_search_objects_result search_objects_res {}".format(
                search_objects_res
                )
            )
        '''

        if not isinstance(path_lst, list):
            raise TypeError("`path_lst' must be str list")

        if (search_objects_res is not None
                and not isinstance(search_objects_res, list)):
            raise Exception(
                "Programming error."
                " Here `search_objects_res' must always"
                " be None or list of str"
                )

        # if len(path_lst) != 0:
        #    directory = self._tree.getpath(path_lst, create_dirs=True)
        # else:
        #    directory = self._tree.getpath([])

        if search_objects_res is not None:
            for i in search_objects_res:

                # print("i: {}".format(i))

                i_unquoted = urllib.request.unquote(i)

                if i_unquoted in ['..', '../', '.', './', '/']:
                    continue

                if i_unquoted.startswith('?'):
                    continue

                if not wayround_org.utils.uri.isuri(i_unquoted):

                    is_dir = i_unquoted.endswith('/')

                    i_unquoted_norm = wayround_org.utils.path.normpath(
                        i_unquoted
                        )

                    i_unquoted_norm_dirname = os.path.dirname(i_unquoted_norm)

                    i_unquoted_norm_basename = os.path.basename(
                        i_unquoted_norm)

                    if i_unquoted_norm_dirname == '':
                        i_unquoted_norm = wayround_org.utils.path.join(
                            path_lst,
                            i_unquoted_norm_basename
                            )
                        i_unquoted_norm_dirname = os.path.dirname(
                            i_unquoted_norm
                            )

                    i_unquoted_norm_dirname_splitted = \
                        wayround_org.utils.path.split(
                            i_unquoted_norm_dirname
                        )

                    if (wayround_org.utils.path.join(path_lst)
                            != wayround_org.utils.path.join(
                            i_unquoted_norm_dirname_splitted
                            )
                            ):
                        continue

                    '''
                    print(
                        "i_unquoted_norm_dirname_splitted: {}".format(
                            i_unquoted_norm_dirname_splitted
                            )
                        )
                    '''
                    tree_dir_to_work_on = self._tree.getpath(
                        i_unquoted_norm_dirname_splitted,
                        create_dirs=True
                        )

                    '''
                    print(
                        "i_unquoted_norm_basename: {}".format(
                            i_unquoted_norm_basename
                            )
                        )

                    print("is_dir: {}".format(is_dir))
                    '''

                    if tree_dir_to_work_on.isdir():
                        if is_dir:
                            tree_dir_to_work_on.mkdir(i_unquoted_norm_basename)
                        else:
                            tree_dir_to_work_on.mkfile(
                                i_unquoted_norm_basename
                                )

        return

    def check_tree_path_population(self, path_lst):
        """
        return: True - ok, False - error
        """
        if not isinstance(path_lst, list):
            raise TypeError("`path_lst' must be str list")

        path_lst_j = wayround_org.utils.path.join(path_lst)

        if path_lst_j not in self._searched_paths:
            self.search_objects(path_lst)
            if (path_lst_j in self._searched_paths
                    and self._searched_paths[path_lst_j] is not None):
                self.populate_tree_from_search_objects_result(path_lst)
        ret = (path_lst_j in self._searched_paths)
        return ret
