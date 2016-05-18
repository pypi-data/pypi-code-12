# add a new column to appears table
if repo.system_source.dbdriver == 'postgres':
    sql('ALTER TABLE appears ADD pwords text ARRAY;')
    sql('ALTER TABLE words ADD count INT DEFAULT 1;')
    # remove the old index
    sql('DROP INDEX words_unique_idx;')
    # add the unique index
    sql('CREATE UNIQUE INDEX words_unique_idx ON words (etype, word);')
