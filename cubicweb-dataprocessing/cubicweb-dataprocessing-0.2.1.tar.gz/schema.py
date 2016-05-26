# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-dataprocessing schema"""

from yams.buildobjs import (ComputedRelation, EntityType, RelationDefinition,
                            Int, String)

from cubicweb.schema import (RRQLExpression, ERQLExpression,
                             RQLConstraint, WorkflowableEntityType)

from cubes.file.schema import File


_ = unicode


DATAPROCESS_UPDATE_PERMS_RQLEXPR = (
    'U in_group G, G name "users", '
    'X in_state S, S name "wfs_dataprocess_initialized"')


class _DataProcess(WorkflowableEntityType):
    __abstract__ = True
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': ('managers',
                   ERQLExpression(DATAPROCESS_UPDATE_PERMS_RQLEXPR)),
        'delete': ('managers',
                   ERQLExpression(DATAPROCESS_UPDATE_PERMS_RQLEXPR)),
        'add': ('managers', 'users')
    }


class DataTransformationProcess(_DataProcess):
    """Data transformation process"""


class DataValidationProcess(_DataProcess):
    """Data validation process"""


class process_depends_on(RelationDefinition):
    subject = 'DataTransformationProcess'
    object = 'DataValidationProcess'
    cardinality = '??'


class process_input_file(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression(
            'U in_group G, G name "users", '
            'S in_state ST, ST name "wfs_dataprocess_initialized"')),
        'delete': ('managers', RRQLExpression('U has_update_permission S'))}
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'File'
    cardinality = '?*'
    description = _('input file of the data process')
    constraints = [
        RQLConstraint('NOT EXISTS(SC implemented_by O)',
                      msg=_('file is used by a script')),
    ]


class validated_by(RelationDefinition):
    """A File may be validated by a validation process"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'DataValidationProcess'
    cardinality = '**'


class produced_by(RelationDefinition):
    """A File may be produced by a transformation process"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'DataTransformationProcess'
    cardinality = '?*'


class process_stderr(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'add': (),
        'delete': (),
    }
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'File'
    cardinality = '??'
    inlined = True
    composite = 'subject'
    description = _('standard error output')


# Set File permissions:
#  * use `produced_by` relation to prevent modification of generated files
#  * bind the update permissions on the Script which uses the File as
#    implementation if any
_update_file_perms = ('managers', ERQLExpression(
    'U in_group G, G name "users", '
    'NOT EXISTS(X produced_by Y), '
    'NOT EXISTS(S1 implemented_by X)'
    ' OR EXISTS(S implemented_by X, U has_update_permission S)'
))
File.__permissions__ = File.__permissions__.copy()
File.__permissions__.update({'update': _update_file_perms,
                             'delete': _update_file_perms})


class _Script(EntityType):
    name = String(required=True, fulltextindexed=True)


class implemented_by(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (RRQLExpression('U has_update_permission S'), ),
        'delete': (RRQLExpression('U has_update_permission S'), ),
    }
    subject = ('ValidationScript', 'TransformationScript')
    object = 'File'
    cardinality = '1?'
    inlined = True
    composite = 'subject'
    description = _('the resource (file) implementing a script')


_validationscript_update_perms = (
    'managers',
    ERQLExpression('U in_group G, G name "users", '
                   'NOT EXISTS(P1 validation_script X) OR '
                   'EXISTS(P2 validation_script X, P2 in_state S,'
                   '       S name "wfs_dataprocess_initialized")'),
)


class ValidationScript(_Script):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': _validationscript_update_perms,
        'delete': _validationscript_update_perms,
        'add': ('managers', 'users')
    }
    parameters = String(
        description=_('parameters for the script, will be used as JSON data '
                      'structure'))


class validation_script(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('U has_update_permission S'), )
    }
    subject = 'DataValidationProcess'
    object = 'ValidationScript'
    cardinality = '1*'
    inlined = True


_transformationscript_update_perms = (
    'managers',
    ERQLExpression('U in_group G, G name "users", '
                   'NOT EXISTS(S1 step_script X, S1 in_sequence SQ1,'
                   '           P1 transformation_sequence SQ1) OR '
                   'EXISTS(S2 step_script X, S2 in_sequence SQ2,'
                   '       P2 transformation_sequence SQ2, P2 in_state S,'
                   '       S name "wfs_dataprocess_initialized")'),
)


class TransformationScript(_Script):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': _transformationscript_update_perms,
        'delete': _transformationscript_update_perms,
        'add': ('managers', 'users')
    }
    output_format = String(maxsize=128,
                           description=_('format (MIME type) of stderr data'))


class transformation_sequence(RelationDefinition):
    # TODO __permissions__
    subject = 'DataTransformationProcess'
    object = 'TransformationSequence'
    cardinality = '1*'


class TransformationSequence(EntityType):
    """A sequence of scripts involved in a given process."""
    # TODO __permissions__
    # name = String(required=True) XXX useful?


class TransformationStep(EntityType):
    """A step in a transformation sequence."""
    # TODO __permissions__
    index = Int(required=True,
                description=_('position in the transformation sequence'))
    parameters = String(
        description=_('parameters for the script, will be used as JSON data '
                      'structure'))
    __unique_together__ = [
        ('index', 'in_sequence'),
        ('in_sequence', 'step_script')
    ]


class step_script(RelationDefinition):
    # TODO __permissions__
    subject = 'TransformationStep'
    object = 'TransformationScript'
    cardinality = '1*'
    inlined = True


class in_sequence(RelationDefinition):
    # TODO __permissions__
    subject = 'TransformationStep'
    object = 'TransformationSequence'
    cardinality = '1+'
    composite = 'object'
    inlined = True


class transformation_scripts(ComputedRelation):
    rule = 'S transformation_sequence SEQ, O in_sequence SEQ'
