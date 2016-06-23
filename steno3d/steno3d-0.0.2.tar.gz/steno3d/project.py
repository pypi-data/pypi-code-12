"""resource.py contains the base resource classes that user-created
resources depend on in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import properties

from .client import pause
from .content import UserContent


class Project(UserContent):
    """Steno3D top-level project"""
    _model_api_location = 'project/steno3d'

    resources = properties.Pointer(
        'Project Resources',
        ptype='CompositeResource',
        repeated=True
    )

    public = properties.Bool(
        'Public visibility of project',
        default=False
    )

    def upload(self, *args, **kwargs):
        """Upload the project"""
        print(self._upload(*args, **kwargs))

    @properties.validator
    def validate(self):
        """Check if project resource pointers are correct"""
        for res in self.resources:
            if self not in res.project:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that resources point to containing '
                                 'project.')
        return True

    def _on_property_change(self, name, pre, post):
        if name == 'resources':
            if pre is None:
                pre = []
            if post is None:
                post = []
            for res in post:
                if res not in pre:
                    res.project += [self]
            for res in pre:
                if res not in post:
                    res.project = [p for p in res.project
                                   if p is not self]
            if len(set(post)) != len(post):
                post_post = []
                for r in post:
                    if r not in post_post:
                        post_post += [r]
                self.resources = post_post

    @property
    def _contentdata(self):
        """Get basic data about the content"""
        datadict = {
            'title': self.title,
            'description': self.description,
            'public': self.public
        }
        return datadict

    @property
    def _reqdata(self):
        """get the required longUids"""
        resource_reqs = (r.json_after_upload for r in self.resources)
        datadict = {
            'resourceUids': ','.join((r['longUid'] for r in resource_reqs)),
        }
        return datadict

    def _upload(self, *args, **kwargs):
        """Perform the upload and any follow-up tasks"""
        res = super(Project, self)._upload(*args, **kwargs)
        pause()
        acl_responses = []
        for resource in self.resources:
            acl_responses.append(resource.add_view_permissions(self))
            resource.add_recursive_view_permissions(self)
        if all(acl_responses):
            return res
        raise Exception(
            'Could not add delegation permissions for one or more '
            'child object(s)'
        )


__all__ = ['Project']
