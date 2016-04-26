APP_NAME = "zotcli"


class ZoteroBackend(object):
    def __init__(self, api_key=None, library_id=None, library_type=None):
        """ Service class for communicating with the Zotero API.

        This is mainly a thin wrapper around :py:class:`pyzotero.zotero.Zotero`
        that handles things like transparent HTML<->[edit-formt] conversion.

        :param api_key:     API key for the Zotero API, will be loaded from
                            the configuration if not specified
        :param library_id:  Zotero library ID the API key is valid for, will
                            be loaded from the configuration if not specified
        :param library_type: Type of the library, can be 'user' or 'group',
                             will also be loaded from the configuration if
                             not specified
        """
        cfg_path = os.path.join(click.get_app_dir(APP_NAME), 'config.ini')
        self.config = load_config(cfg_path)
        self.note_format = self.config['zotcli.note_format']

        api_key = api_key or self.config.get('zotcli.api_key')
        library_id = library_id or self.config.get('zotcli.library_id')
        library_type = (library_type or self.config.get('zotcli.library_type')
                        or 'user')
        if not api_key or not library_id:
            raise ValueError(
                "Please set your API key and library ID in the configuration file "
                "({}) or pass them as command-line options.\nIf you do not have "
                "these, please go to https://www.zotero.org/settings/keys to "
                "retrieve them.".format(cfg_path))
        self._zot = Zotero(library_id=library_id, api_key=api_key,
                           library_type=library_type)

    def items(self, query=None, limit=None, recursive=False):
        raise NotImplementedError

    def notes(self, item_id):
        raise NotImplementedError

    def create_note(self, item_id, note_text):
        """ Create a new note for a given item.

        :param item_id:     ID/key of the item to create the note for
        :param note_text:   Text of the note
        """
        note = self._zot.item_template('note')
        note['note'] = pypandoc.convert(
            note_text, 'html', format=self.note_format)
        self._zot.create_items([note], item_id)

    def save_note(self, note):
        """ Update an existing note.

        :param note:        The updated note
        """
        note_html = pypandoc.convert(
            note['data']['note'], 'html', format=self.note_format)
        note['data']['note'] = note_html
        self._zot.update_item(note)


class OnlineBackend(ZoteroBackend):
    def items(self, query=None, limit=None, recursive=False):
        """ Get a list of all items in the library matching the arguments.

        :param query:   Filter items by this query string (targets author and
                        title fields)
        :type query:    str/unicode
        :param limit:   Limit maximum number of returned items
        :type limit:    int
        :param recursive: Include non-toplevel items (attachments, notes, etc)
                          in output
        :type recursive: bool
        :returns:       Generator that yields items
        """
        query_args = {}
        if query:
            query_args['q'] = query
        if limit:
            query_args['limit'] = limit
        query_fn = self._zot.items if recursive else self._zot.top
        items = self._zot.everything(query_fn(**query_args))
        for it in items:
            yield {'key': it['data']['key'],
                   'creator': it['meta'].get('creatorSummary'),
                   'title': it['data'].get('title', "Untitled"),
                   'date': it['data'].get('date'),
                   'has_children': it['meta'].get('numChildren', 0) > 0}

    def notes(self, item_id):
        """ Get a list of all notes for a given item.

        :param item_id:     ID/key of the item to get notes for
        :returns:           Notes for item
        """
        notes = self._zot.children(item_id, itemType="note")
        for note in notes:
            note['data']['note'] = pypandoc.convert(
                note['data']['note'], self.note_format, format='html')
        return notes


class CachedBackend(ZoteroBackend):
    def __init__(self, *args, **kwargs):
        ZoteroBackend(*args, **kwargs)
        self.db_path = os.path.join(click.get_app_dir(APP_NAME),
                                    'cache.sqlite')
