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


class BaseResource(UserContent):
    """Base class for all resources that are added to projects and
    uploaded to steno3d
    """
    meta = properties.Object('Meta data in JSON form.', default={})

    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        return True


class CompositeResource(BaseResource):
    """A composite resource that stores references to lower-level
    objects, and may also grant access to them through ACL delegation.
    """
    project = properties.Pointer(
        'Project',
        ptype='Project',
        required=True,
        repeated=True
    )
    _children = {
        'mesh': None,
        'data': 'data',
        'textures': None,
    }

    def __init__(self, project=None, **kwargs):
        if project is None:
            raise TypeError('Resource must be constructed with its '
                            'containing project(s)')
        super(CompositeResource, self).__init__(**kwargs)
        self.project = project

    @properties.validator
    def validate(self):
        for proj in self.project:
            if self not in proj.resources:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that projects contain all the '
                                 'resources that point to them.')

    def upload(self, *args, **kwargs):
        """Upload the resource through its containing project(s)"""
        # self.validate()
        for proj in self.project:
            proj.upload(*args, **kwargs)

    def _upload(self, *args, **kwargs):
        """Perform the upload and any follow-up tasks"""
        pause()
        res = super(CompositeResource, self)._upload(*args, **kwargs)
        pause()
        resp = self.add_recursive_view_permissions()
        if not resp:
            raise Exception(('Could not add delegation permissions '
                             'for one or more child object(s)'))
        return res

    def _on_property_change(self, name, pre, post):
        if name == 'project':
            if pre is None:
                pre = []
            if post is None:
                post = []
            for proj in post:
                if proj not in pre:
                    proj.resources += [self]
            for proj in pre:
                if proj not in post:
                    proj.resources = [r for r in proj.resources
                                      if r is not self]
            if len(set(post)) != len(post):
                post_post = []
                for p in post:
                    if p not in post_post:
                        post_post += [p]
                self.project = post_post

    def add_recursive_view_permissions(self, accessor=None):
        """Add recursive view permissions to child objects for
        this class or another accessor (e.g., a project)
        """
        if accessor is None:
            accessor = self
        acl_responses = []
        for key in self._children:
            subkey = self._children[key]
            child = getattr(self, key, None)
            if child:
                if isinstance(child, list):
                    for item in child:
                        target = getattr(item, subkey) if subkey else item
                        pause()
                        acl_responses.append(
                            target.add_view_permissions(accessor)
                        )
                else:
                    target = getattr(child, subkey) if subkey else child
                    pause()
                    acl_responses.append(target.add_view_permissions(accessor))
        return all(acl_responses)


class BaseMesh(BaseResource):
    """Base class for all mesh resources. These are contained within
    each composite resources and define its structure
    """
    pass


class BaseData(BaseResource):
    """Base class for all data resources. These can be contained within
    each composite resource and define data corresponding to the mesh
    """
    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/data/{className}'.format(
                className=cls._resource_class)
        return cls.__model_api_location


class BaseTexture2D(BaseResource):
    """Base class for all texture resources. These can be contained
    within some composite resources and define data in space that gets
    mapped to the mesh.
    """
    @properties.classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/texture2d/{className}'.format(
                className=cls._resource_class)
        return cls.__model_api_location
