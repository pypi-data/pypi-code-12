
import re
from bl.dict import Dict
from bl.config import Config

class AccessFile(Config):
    """This file is used by the SVN archive for path-based access control.
    See http://svnbook.red-bean.com/en/1.7/svn.serverconfig.pathbasedauthz.html
    """
    # Comment from above:
    #   If you're using the SVNParentPath directive, it's important to specify 
    #   the repository names in your sections. If you omit them, a section such 
    #   as [/some/dir] will match the path /some/dir in every repository. 
    #   If you're using the SVNPath directive, however, it's fine to only define 
    #   paths in your sections—after all, there's only one repository.

    def __init__(self, filename, **SVN):
        # turn off interpolation -- SVN itself doesn't use it
        Config.__init__(self, filename, interpolation=None, split_list='\s*,\s*', join_list=', ')
        if self.aliases is None: 
            self.aliases = Dict()
        if self.groups is None: 
            self.groups = Dict()
        for group in self.groups.keys():
            if type(self.groups[group])==str:
                self.groups[group] = re.split('\s*,\s*', self.groups[group])
        self.__dict__['__svn__'] = SVN
        
    def __repr__(self):
        return "SVNAccessFile('%s')" % self.__filename__

    def add_user_to_group(self, user, group):
        if group not in self.groups:
            self.groups[group] = []
        if user not in self.groups[group]:
            self.groups[group].append(user)
            self.write()

    def remove_user_from_group(self, user, group):
        if group in self.groups and user in self.groups[group]:
            self.groups[group].remove(user)
            self.write()

    def group_members(self, group):
        """return a flat list of group members, with all aliases and subgroups expanded."""
        members = []
        if self.groups.get(group) is not None:
            for user in self.groups[group]:
                if user[:1]=='&':
                    alias = user[1:]
                    if self.aliases.get(alias) is not None and self.aliases[alias] not in members:
                        members.append(self.aliases[alias])
                elif user[:1]=='@':
                    subgroup = user[1:]
                    for member in self.group_members(subgroup):
                        if member not in members:
                            members.append(member)
                elif user not in members:
                    members.append(user)
        return members

    def match_sections(self, path):
        """For a given file path, return config sections that match."""
        # If SVN.parent_path is defined,
        #   If the section has a repos: name, then the repos is that folder within SVN.parent_path.
        #   If the section has no repos: name, then this section matches all repositories
        # If SVN.parent_path is not defined,
        #   If the section has a repos: name, it's an error
        #   If the section has no repos: name, this section matches that path in the repository

    def check_path_access(self, user, action, repos_path, dest_path=None):
        """Check if user has access to do action on repos_path, 
            and on dest_path if action=='move' or 'copy'.
        """
        # This method based on study of req_check_access(...) in   
        # <http://svn.apache.org/repos/asf/subversion/tags/1.9.3/subversion/mod_authz_svn/mod_authz_svn.c>.
        # However, any errors in the implementation are mine. --sah@blackearth.us

        action = action.lower()
        authz_svn_type = []
        if action in ['copy', 'move', 'delete']:
            authz_svn_type += ['recursive']
        if action in ['copy', 'options', 'get', 'propfind', 'report']:
            authz_svn_type += ['read']
        if action in ['move', 'delete', 'mkcol', 'put', 'proppatch', 
                    'checkout', 'merge', 'mkactivity', 'lock', 'unlock']:
            authz_svn_type += ['write']

        if action in ['move', 'copy']:
            if not dest_path: 
                return False


