import itertools
import json

from table_column import TableColumn
from table import Table
import formatted_text

class TableBuilder(object):
    """ High level API to build a table in analysis

    :param numpy 2Darray, pandas DataFrame or List of columns data: table data
    :param str title: table title
    :param int default_rows_per_page: the default number of rows per page when the table is initially rendered
    :param List of str column_names: names of each column
    :param bool striped: whether or not the table rows should be rendered in alternating grey and white stripes
    :param str search_box_place_holder: the default text shown in the search box when user hasn't typed any search keyword
    """

    ALLOWED_ROWS_PER_PAGE = [10, 20, 50, 100]

    def __init__(self, data, title, default_rows_per_page = 20, column_names = [], striped = True, search_box_place_holder = 'Search'):
        self._table_id = None

        self.title = title
        self.striped = striped
        self.search_box_place_holder = search_box_place_holder

        if not (default_rows_per_page in self.ALLOWED_ROWS_PER_PAGE):
            raise RuntimeError("Only one of {0} is allowed for default_rows_per_page".format(self.ALLOWED_ROWS_PER_PAGE))
        self.default_rows_per_page = default_rows_per_page

        self._columns = []
        self._col_name_to_idx = {}

        if type(data).__name__ == 'DataFrame':  # treat it as Pandas DataFrame
            df = data
            n_cols = df.shape[1]
            if column_names and len(column_names) < n_cols:
                raise RuntimeError("The length of column_names must be the same as number of columns")

            for i in xrange(0, n_cols):
                self._add_col(df.ix[:,i], i, column_names[i] if column_names else df.ix[:,i].name);
        else:
            if type(data).__name__ == 'ndarray':  # treat it as Numpy Array, need to transpose the data
                data = data.T

            if len(column_names) < len(data):
                raise RuntimeError("Must provide column_names and its length must be the same as number of columns")

            # assume it is a list of columns
            for (i, col) in enumerate(data):
                self._add_col(col, i, column_names[i]);

    @property
    def _component_type(self):
        return "TABLE"

    def _add_col(self, col_data, col_idx, col_name):
        self._columns.append(TableColumn(self, list(col_data), col_name))
        self._col_name_to_idx[col_name] = col_idx

    def _change_col_name(self, old_name, new_name):
        col_idx = self._col_name_to_idx[old_name]
        del self._col_name_to_idx[old_name]
        self._col_name_to_idx[new_name] = col_idx

    def __getitem__(self, idx):
        if isinstance(idx, basestring):
            return self._columns[self._col_name_to_idx[idx]]
        else:
            return self._columns[idx]

    def _get_table_data(self, analysis):
        all_cols_data = []  # all columns including the columns for rendering and sorting, each element is a column
        all_cols_name = []  # 1 to 1 mapping to the all_cols_data, each element is the name of a column
        row_components_col = []  # the "row_components" column, each element is the list of components for the a row
        for col_obj in self._columns:
            cols_data, cols_name, cols_comp = col_obj._get_data_columns(analysis)
            assert len(cols_data) == len(cols_name)
            all_cols_data.extend(cols_data)
            all_cols_name.extend(cols_name)

            # for each row, accumulate the new components into the existing row_components column
            if cols_comp:
                if row_components_col:
                    row_components_col = [existing_comp+new_comp for existing_comp, new_comp in itertools.izip(row_components_col, cols_comp)]
                else:
                    row_components_col = cols_comp

        # the "row_components" is just another column in the table data
        all_cols_data.append(row_components_col)
        all_cols_name.append("row_components")
        assert len(all_cols_data) == len(all_cols_name)

        # access the data by row, and turn it into a list of dict, each representing a row
        rows = itertools.izip_longest(*all_cols_data)
        table_data_json = [dict(itertools.izip(all_cols_name, row)) for row in rows]

        return table_data_json

    def _get_table_component(self, table_id, analysis = None):
        title_comp_ref, _ = formatted_text._get_component_ref_and_defs_for_value(
                self.title, analysis, associate_with_analysis=True)  # components in table title is put into the analysis' main component list

        columns = []
        filter_columns = []
        search_columns = []
        for col_obj in self._columns:
            if col_obj.filterable:
                filter_columns.append({
                    "key": col_obj._column_name,
                    "label": col_obj.filter_name })
            if col_obj.searchable:
                search_columns.append(col_obj._column_name)
            if not col_obj.filter_only:
                header_comp_ref, _ = formatted_text._get_component_ref_and_defs_for_value(
                        col_obj.column_header, analysis, associate_with_analysis=True)  # components in table title is put into the analysis' main component list
                columns.append({
                    "displayKey": col_obj._rendered_col_name,
                    "name":  header_comp_ref,
                    "sortKey": col_obj._sort_col_name,
                    "width": col_obj.width })

        # put the default_rows_per_page as the first element, this is what WebUI requires
        page_sizes = [self.default_rows_per_page] + sorted(set(self.ALLOWED_ROWS_PER_PAGE) - {self.default_rows_per_page})

        default_sort_order = {'key': columns[0]["sortKey"], 'order': 'ASC'}

        return Table(
                table_id = table_id,
                columns = columns,
                defaultSort = default_sort_order,
                filters = filter_columns,
                searchBoxAttributes = search_columns,
                pageSizes = page_sizes,
                searchBoxPlaceholder = self.search_box_place_holder,
                striped = self.striped,
                title = title_comp_ref)

    def _associate(self, analysis):
        """ Associate the table with specified analysis
        """

        # upload the table data
        endpoint = '/analysis/%s/tables' % analysis._id
        resp = analysis._eureqa._session.execute(endpoint, method='POST', args=self._get_table_data(analysis))
        table_id = resp['table_id']

        # upload the table component
        table_component = self._get_table_component(table_id, analysis = analysis)
        table_component._associate(analysis);

        # book keeping
        self._table_id = table_id
        self._component_id = table_component._component_id

        self._analysis = analysis
