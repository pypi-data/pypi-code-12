if repo.system_source.dbdriver == 'postgres':
    sql('''
DROP FUNCTION IF EXISTS limit_size (fulltext text, format text, maxsize integer);
CREATE FUNCTION limit_size (fulltext text, format text, maxsize integer) RETURNS text AS $$
DECLARE
    plaintext text;
BEGIN
    IF char_length(fulltext) < maxsize THEN
       RETURN fulltext;
    END IF;
    IF format = 'text/html' OR format = 'text/xhtml' OR format = 'text/xml' THEN
       plaintext := regexp_replace(fulltext, '<[a-zA-Z/][^>]*>', '', 'g');
    ELSE
       plaintext := fulltext;
    END IF;
    IF char_length(plaintext) < maxsize THEN
       RETURN plaintext;
    ELSE
       RETURN substring(plaintext from 1 for maxsize) || '...';
    END IF;
END
$$ LANGUAGE plpgsql;;
''')

for etype in ('Structure', 'History'):
    drop_relation_definition(etype, 'equivalent_concept', 'Concept')
    drop_relation_definition(etype, 'equivalent_concept', 'ExternalUri')
    sync_schema_props_perms(etype)
