import sys


class KindType(object):
    """
    The types of items that are part of a project. Strings are from the duke-data-service.
    """
    file_str = 'dds-file'
    folder_str = 'dds-folder'
    project_str = 'dds-project'

    @staticmethod
    def is_file(item):
        return item.kind == KindType.file_str

    @staticmethod
    def is_folder(item):
        return item.kind == KindType.folder_str

    @staticmethod
    def is_project(item):
        return item.kind == KindType.project_str


class ProgressPrinter(object):
    """
    Prints a progress bar(percentage) to the terminal, expects to have sending_item and finished called.
    Replaces the same line again and again as progress changes.
    """
    def __init__(self, total, msg_verb):
        """
        Setup printer expecting to have sending_item called total times.
        :param total: int the number of items we are expecting, used to determine progress
        """
        self.total = total
        self.cnt = 0
        self.max_width = 0
        self.msg_verb = msg_verb

    def transferring_item(self, item, increment_amt=1):
        """
        Update progress that item is about to be transferred.
        :param item: LocalFile, LocalFolder, or LocalContent(project) that is about to be sent.
        :param increment_amt: int amount to increase our count(how much progress have we made)
        """
        percent_done = int(float(self.cnt)/float(self.total) * 100.0)
        name = ''
        if KindType.is_project(item):
            name = 'project'
        else:
            name = item.path
        # left justify message so we cover up the previous one
        message = u'\rProgress: {}% - {} {}'.format(percent_done, self.msg_verb, name)
        self.max_width = max(len(message), self.max_width)
        sys.stdout.write(message.ljust(self.max_width))
        sys.stdout.flush()
        self.cnt += increment_amt

    def finished(self):
        """
        Must be called to print final progress label.
        """
        sys.stdout.write('\rDone: 100%'.ljust(self.max_width) + '\n')
        sys.stdout.flush()


class ProjectWalker(object):
    """
    Generic tool for visiting all the nodes in a project.
    For use with RemoteProject and LocalProject
    """
    @staticmethod
    def walk_project(project, visitor):
        """

        :param project: LocalProject project we want to visit all children of.
        :param visitor: object must implement visit_project, visit_folder, visit_file
        :return:
        """
        ProjectWalker._visit_content(project, None, visitor)

    @staticmethod
    def _visit_content(item, parent, visitor):
        """
        Recursively visit nodes in the project tree.
        :param item: LocalContent/LocalFolder/LocalFile we are traversing down from
        :param parent: LocalContent/LocalFolder parent or None
        :param visitor: object visiting the tree
        """
        if KindType.is_project(item):
            visitor.visit_project(item)
        elif KindType.is_folder(item):
            visitor.visit_folder(item, parent)
        else:
            visitor.visit_file(item, parent)
        if not KindType.is_file(item):
            for child in item.children:
                ProjectWalker._visit_content(child, item, visitor)