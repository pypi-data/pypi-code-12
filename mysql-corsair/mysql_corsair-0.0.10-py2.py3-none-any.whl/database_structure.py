import itertools
import json
from config_helpers import load_config
from foreign_key import ForeignKey
import sql_query_helpers


class DatabaseStructure:
    def __init__(self, table_list, source_db_conn_dict, local_db_conn_dict):
        self.table_list = table_list
        self.source_db_conn_dict = source_db_conn_dict
        self.local_db_conn_dict = local_db_conn_dict
        self.foreign_keys = [
            ForeignKey(k) for k in sql_query_helpers.get_foreign_keys(
                source_db_conn_dict
            )
        ]
        self.table_structures = [
            TableStructure(
                table_name, source_db_conn_dict, local_db_conn_dict,
                [k for k in self.foreign_keys if k.target_table == table_name]
            ) for table_name in table_list
        ]
        self.filename = 'structure.json'
        self.operations = {
            'createstructure':  self.create_table,
            'deletedata': self.delete_data
        }

    def initially_populate(self, conn_dict):
        print """Discovering correct foreign key relations for the database {0}.
            """.format(conn_dict['db'])
        for target_table_structure in self.table_structures:
            fks_in = target_table_structure.foreign_keys
            self.make_links(target_table_structure, fks_in)

    def make_links(self, target_table_structure, fks_in):
        for fk in fks_in:
            source_table_structure = self.get_table_structure(
                fk.source_table
            )
            source_table_structure.add_to_links(target_table_structure)

    def get_table_structure(self, name):
        return next(x for x in self.table_structures if x.name == name)

    def tables_ready_for_operation(self, operation_name):
        return [
            ts for ts in self.table_structures if
            ts.is_ready_for_operation(operation_name)
        ]

    def all_tables_done(self, operation_name):
        return len(self.tables_ready_for_operation(operation_name)) == 0

    def recursively_perform_operations(self, operation_name):
        while not self.all_tables_done(operation_name):
            for ts in self.table_structures:
                if ts.is_ready_for_operation(operation_name):
                    self.execute_operation(ts.name, operation_name)

    def execute_operation(self, table_name, operation_name):
        op = self.operations.get(operation_name)
        if not op:
            print "Sorry, I don't know the operation {0}.".format(
                operation_name
            )
        else:
            op(table_name)
        self.get_table_structure(table_name).mark_done()

    def create_table(self, table_name):
        table_creation_ddl = "SHOW CREATE TABLE {0}".format(table_name)
        table_creation_statement = sql_query_helpers.get_sql_result(
            table_creation_ddl, self.source_db_conn_dict
        )[0][1]

        print "Creating the table {0}.{1}".format(
            self.local_db_conn_dict['db'], table_name
        )
        sql_query_helpers.execute_sql(
            table_creation_statement, self.local_db_conn_dict
        )

    def delete_data(self, table_name, config_file_path=None):
        default_tables = load_config(config_file_path).DEFAULT_TABLES
        if table_name not in default_tables:
            sql = "DELETE IGNORE FROM {0};".format(table_name)
            print "Deleting all data from table {0}.{1}".format(
                self.local_db_conn_dict['db'], table_name
            )
            sql_query_helpers.execute_sql(sql, self.local_db_conn_dict)

    def write_structure_to_file(self, filename, conn_dict):
        db_structure_dict = {}

        db_structure_dict['table_names'] = [
            ts.name for ts in self.table_structures
        ]
        db_structure_dict['foreign_keys'] = [
            fk.to_dict() for fk in self.foreign_keys
        ]
        json_to_write = json.dumps(db_structure_dict)
        print "Writing structure to file {0}.".format(filename)
        open(filename, 'w').write(json_to_write)


def flatten(list_of_lists):
    return list(itertools.chain.from_iterable(list_of_lists))


class TableStructure:
    def __init__(self, name, source_db_conn_dict, local_db_conn_dict,
                 foreign_keys):
        self.name = name
        self.source_db_conn_dict = source_db_conn_dict
        self.local_db_conn_dict = local_db_conn_dict
        self.foreign_keys = foreign_keys

        self.is_done = False
        self.links_out = []
        self.links_in = []

    def mark_done(self):
        self.is_done = True

    def add_to_links(self, table_structure):
        self.links_out.append(table_structure)
        table_structure.links_in.append(self)

    def num_relevant_links(self, direction):
        predicate = lambda l: not l.is_done and l.name != self.name
        links = getattr(self, 'links_%s' % direction)
        return len([l for l in links if predicate(l)])

    def no_links(self, direction):
        return self.num_relevant_links(direction) == 0

    def is_ready_for_operation(self, operation_name):
        direction = {
            'createstructure': 'out',
            'deletedata': 'in'
        }
        return (self.no_links(direction[operation_name]) and
                not self.is_done)
