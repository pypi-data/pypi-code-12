# missed by 0.10.0 migration
for ertype in ('in_scheme', 'broader_concept', 'label_of'):
    sync_schema_props_perms(ertype, syncprops=False)
