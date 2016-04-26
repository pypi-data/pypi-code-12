from __future__ import print_function, unicode_literals
from string import Template

__author__ = "danishabdullah"

ITEM_JSON = Template("""{"name": "$name", "type": "$type", "mode": "$mode"}""")
RECORD_JSON = Template("""{"name": "$name", "type": "RECORD", "mode": "$mode", "fields":[$fields]}""")
TABLE_JSON = Template("""[$fields]""")
SPEC_JSON = Template("""$tables""")

ITEM_JAVA = Template(
    """$path_modifier.add(new TableFieldSchema().setName("$name").setType("$type").setMode("$mode"));""")
RECORD_JAVA = Template("""$path_modifier.add(new TableFieldSchema().setName("$name").setType("RECORD").setMode("$mode").setFields(
    new ArrayList<TableFieldSchema>() {
        {$fields}
    }));""")
TABLE_JAVA = Template("""private static TableSchema $name() {
    List<TableFieldSchema> fields = new ArrayList<>();
    $fields
    TableSchema schema = new TableSchema().setFields(fields);
    return schema;
}""")
SPEC_JAVA = Template("""import com.google.api.services.bigquery.model.TableFieldSchema;
import com.google.api.services.bigquery.model.TableSchema;

import java.util.ArrayList;
import java.util.List;

public class Pipeline {
    $tables
}
""")
