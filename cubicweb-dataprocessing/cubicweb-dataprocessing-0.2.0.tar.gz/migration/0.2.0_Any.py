def copy_script(eid, etype, **kwargs):
    """Copy a `Script` entity with `eid` into an entity of `etype`
    (ValidationScript or TransformationScript).
    """
    script = cnx.entity_from_eid(eid)
    kwargs['name'] = script.name
    kwargs['implemented_by'] = script.implemented_by
    new = create_entity(etype, **kwargs)
    script.cw_delete()
    return new


add_entity_type('ValidationScript')
add_entity_type('TransformationScript')
add_entity_type('TransformationSequence')
add_entity_type('TransformationStep')

rset = rql('Any P,S WHERE P is DataTransformationProcess, P process_script S',
           ask_confirm=False)
drop_relation_definition('DataTransformationProcess', 'process_script', 'Script')
for peid, seid in rset:
    script = copy_script(seid, 'TransformationScript')
    seq = create_entity('TransformationSequence',
                        reverse_transformation_sequence=peid)
    create_entity('TransformationStep', index=0, step_script=script,
                  in_sequence=seq)
commit(ask_confirm=False)

rset = rql('Any P,S WHERE P is DataValidationProcess, P process_script S',
           ask_confirm=False)
drop_relation_definition('DataValidationProcess', 'process_script', 'Script')
for peid, seid in rset:
    copy_script(seid, 'ValidationScript', reverse_validation_script=peid)
commit(ask_confirm=False)

drop_relation_type('process_script')
drop_relation_definition('Script', 'implemented_by', 'File')
drop_entity_type('Script')

add_relation_type('process_stderr')

sync_schema_props_perms('DataTransformationProcess')
sync_schema_props_perms('DataValidationProcess')
sync_schema_props_perms('process_input_file')
sync_schema_props_perms('File', syncprops=False)
