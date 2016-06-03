#
# Copyright (c) 2015 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Auto-generated file for API static documentation stubs (2016-06-02T20:59:32.166405)
#
# **DO NOT EDIT**

from trustedanalytics.meta.docstub import doc_stub, DocStubCalledError



@doc_stub
class _DocStubsEdgeFrame(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, graph=None, label=None, src_vertex_label=None, dest_vertex_label=None, directed=None):
        """
            Examples

        --------
        Given a data file */movie.csv*, create a frame to match this data and move
        the data to the frame.
        Create an empty graph and define some vertex and edge types.

        .. code::

            >>> my_csv = ta.CsvFile("/movie.csv", schema= [('user_id', int32),
            ...                                     ('user_name', str),
            ...                                     ('movie_id', int32),
            ...                                     ('movie_title', str),
            ...                                     ('rating', str)])

            >>> my_frame = ta.Frame(my_csv)
            >>> my_graph = ta.Graph()
            >>> my_graph.define_vertex_type('users')
            >>> my_graph.define_vertex_type('movies')
            >>> my_graph.define_edge_type('ratings','users','movies',directed=True)

        Add data to the graph from the frame:

        .. only:: html

            .. code::

                >>> my_graph.vertices['users'].add_vertices(my_frame, 'user_id', ['user_name'])
                >>> my_graph.vertices['movies].add_vertices(my_frame, 'movie_id', ['movie_title])

        .. only:: latex

            .. code::

                >>> my_graph.vertices['users'].add_vertices(my_frame, 'user_id',
                ... ['user_name'])
                >>> my_graph.vertices['movies'].add_vertices(my_frame, 'movie_id', ['movie_title'])

        Create an edge frame from the graph, and add edge data from the frame.

        .. code::

            >>> my_edge_frame = graph.edges['ratings']
            >>> my_edge_frame.add_edges(my_frame, 'user_id', 'movie_id', ['rating']

        Retrieve a previously defined graph and retrieve an EdgeFrame from it:

        .. code::

            >>> my_old_graph = ta.get_graph("your_graph")
            >>> my_new_edge_frame = my_old_graph.edges["your_label"]

        Calling methods on an EdgeFrame:

        .. code::

            >>> my_new_edge_frame.inspect(20)

        Copy an EdgeFrame to a frame using the copy method:

        .. code::

            >>> my_new_frame = my_new_edge_frame.copy()

            

        :param graph: (default=None)  
        :type graph: 
        :param label: (default=None)  
        :type label: 
        :param src_vertex_label: (default=None)  
        :type src_vertex_label: 
        :param dest_vertex_label: (default=None)  
        :type dest_vertex_label: 
        :param directed: (default=None)  
        :type directed: 
        """
        raise DocStubCalledError("frame:edge/__init__")


    @doc_stub
    def add_columns(self, func, schema, columns_accessed=None):
        """
        Add columns to current frame.

        Assigns data to column based on evaluating a function for each row.

        Notes
        -----
        1)  The row |UDF| ('func') must return a value in the same format as
            specified by the schema.
            See :doc:`/ds_apir`.
        2)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!

        Examples
        --------
        Given our frame, let's add a column which has how many years the person has been over 18

        .. code::


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183

            >>> frame.add_columns(lambda row: row.age - 18, ('adult_years', ta.int32))
            [===Job Progress===]

            >>> frame.inspect()
            [#]  name      age  tenure  phone     adult_years
            =================================================
            [0]  Fred       39      16  555-1234           21
            [1]  Susan      33       3  555-0202           15
            [2]  Thurston   65      26  555-4510           47
            [3]  Judy       44      14  555-2183           26


        Multiple columns can be added at the same time.  Let's add percentage of
        life and percentage of adult life in one call, which is more efficient.

        .. code::

            >>> frame.add_columns(lambda row: [row.tenure / float(row.age), row.tenure / float(row.adult_years)], [("of_age", ta.float32), ("of_adult", ta.float32)])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54

        Note that the function returns a list, and therefore the schema also needs to be a list.

        It is not necessary to use lambda syntax, any function will do, as long as it takes a single row argument.  We
        can also call other local functions within.

        Let's add a column which shows the amount of person's name based on their adult tenure percentage.

            >>> def percentage_of_string(string, percentage):
            ...     '''returns a substring of the given string according to the given percentage'''
            ...     substring_len = int(percentage * len(string))
            ...     return string[:substring_len]

            >>> def add_name_by_adult_tenure(row):
            ...     return percentage_of_string(row.name, row.of_adult)

            >>> frame.add_columns(add_name_by_adult_tenure, ('tenured_name', unicode))
            [===Job Progress===]

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame.inspect(columns=['name', 'of_adult', 'tenured_name'], round=2)
            [#]  name      of_adult  tenured_name
            =====================================
            [0]  Fred          0.76  Fre
            [1]  Susan         0.20  S
            [2]  Thurston      0.55  Thur
            [3]  Judy          0.54  Ju


        **Optimization** - If we know up front which columns our row function will access, we
        can tell add_columns to speed up the execution by working on only the limited feature
        set rather than the entire row.

        Let's add a name based on tenure percentage of age.  We know we're only going to use
        columns 'name' and 'of_age'.

        .. code::

            >>> frame.add_columns(lambda row: percentage_of_string(row.name, row.of_age),
            ...                   ('tenured_name_age', unicode),
            ...                   columns_accessed=['name', 'of_age'])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54
            <BLANKLINE>
            [#]  tenured_name  tenured_name_age
            ===================================
            [0]  Fre           F
            [1]  S
            [2]  Thur          Thu
            [3]  Ju            J

        More information on a row |UDF| can be found at :doc:`/ds_apir`



        :param func: User-Defined Function (|UDF|) which takes the values in the row and produces a value, or collection of values, for the new cell(s).
        :type func: UDF
        :param schema: The schema for the results of the |UDF|, indicating the new column(s) to add.  Each tuple provides the column name and data type, and is of the form (str, type).
        :type schema: tuple | list of tuples
        :param columns_accessed: (default=None)  List of columns which the |UDF| will access.  This adds significant performance benefit if we know which column(s) will be needed to execute the |UDF|, especially when the frame has significantly more columns than those being used to evaluate the |UDF|.
        :type columns_accessed: list
        """
        return None


    @doc_stub
    def add_edges(self, source_frame, column_name_for_source_vertex_id, column_name_for_dest_vertex_id, column_names=None, create_missing_vertices=False):
        """
        Add edges to a graph.

        Includes appending to a list of existing edges.

        See :doc:`here <../../graphs/graph-/__init__>` for example usage in
        graph construction.


        :param source_frame: Frame that will be the source of
            the edge data.
        :type source_frame: Frame
        :param column_name_for_source_vertex_id: column name for a unique id for
            each source vertex (this is not the system defined _vid).
        :type column_name_for_source_vertex_id: unicode
        :param column_name_for_dest_vertex_id: column name for a unique id for
            each destination vertex (this is not the system defined _vid).
        :type column_name_for_dest_vertex_id: unicode
        :param column_names: (default=None)  Column names to be used as properties for each vertex,
            None means use all columns,
            empty list means use none.
        :type column_names: list
        :param create_missing_vertices: (default=False)  True to create missing vertices for edge (slightly slower),
            False to drop edges pointing to missing vertices.
            Defaults to False.
        :type create_missing_vertices: bool

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def assign_sample(self, sample_percentages, sample_labels=None, output_column=None, random_seed=None):
        """
        Randomly group rows into user-defined classes.

        Randomly assign classes to rows given a vector of percentages.
        The table receives an additional column that contains a random label.
        The random label is generated by a probability distribution function.
        The distribution function is specified by the sample_percentages, a list of
        floating point values, which add up to 1.
        The labels are non-negative integers drawn from the range
        :math:`[ 0, len(S) - 1]` where :math:`S` is the sample_percentages.

        **Notes**

        The sample percentages provided by the user are preserved to at least eight
        decimal places, but beyond this there may be small changes due to floating
        point imprecision.

        In particular:

        #)  The engine validates that the sum of probabilities sums to 1.0 within
            eight decimal places and returns an error if the sum falls outside of this
            range.
        #)  The probability of the final class is clamped so that each row receives a
            valid label with probability one.


        Consider this simple frame.

        >>> frame.inspect()
        [#]  blip  id
        =============
        [0]  abc    0
        [1]  def    1
        [2]  ghi    2
        [3]  jkl    3
        [4]  mno    4
        [5]  pqr    5
        [6]  stu    6
        [7]  vwx    7
        [8]  yza    8
        [9]  bcd    9

        We'll assign labels to each row according to a rough 40-30-30 split, for
        "train", "test", and "validate".

        >>> frame.assign_sample([0.4, 0.3, 0.3])
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin
        =========================
        [0]  abc    0  VA
        [1]  def    1  TR
        [2]  ghi    2  TE
        [3]  jkl    3  TE
        [4]  mno    4  TE
        [5]  pqr    5  TR
        [6]  stu    6  TR
        [7]  vwx    7  VA
        [8]  yza    8  VA
        [9]  bcd    9  VA


        Now the frame  has a new column named "sample_bin" with a string label.
        Values in the other columns are unaffected.

        Here it is again, this time specifying labels, output column and random seed

        >>> frame.assign_sample([0.2, 0.2, 0.3, 0.3],
        ...                     ["cat1", "cat2", "cat3", "cat4"],
        ...                     output_column="cat",
        ...                     random_seed=12)
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin  cat
        ===============================
        [0]  abc    0  VA          cat4
        [1]  def    1  TR          cat2
        [2]  ghi    2  TE          cat3
        [3]  jkl    3  TE          cat4
        [4]  mno    4  TE          cat1
        [5]  pqr    5  TR          cat3
        [6]  stu    6  TR          cat2
        [7]  vwx    7  VA          cat3
        [8]  yza    8  VA          cat3
        [9]  bcd    9  VA          cat4



        :param sample_percentages: Entries are non-negative and sum to 1. (See the note below.)
            If the *i*'th entry of the  list is *p*,
            then then each row receives label *i* with independent probability *p*.
        :type sample_percentages: list
        :param sample_labels: (default=None)  Names to be used for the split classes.
            Defaults to "TR", "TE", "VA" when the length of *sample_percentages* is 3,
            and defaults to Sample_0, Sample_1, ... otherwise.
        :type sample_labels: list
        :param output_column: (default=None)  Name of the new column which holds the labels generated by the
            function.
        :type output_column: unicode
        :param random_seed: (default=None)  Random seed used to generate the labels.
            Defaults to 0.
        :type random_seed: int32

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column(self, column_name, cutoffs, include_lowest=None, strict_binning=None, bin_column_name=None):
        """
        Classify data into user-defined groups.

        Summarize rows of data based on the value in a single column by sorting them
        into bins, or groups, based on a list of bin cutoff points.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  Bins IDs are 0-index, in other words, the lowest bin number is 0.
        #)  The first and last cutoffs are always included in the bins.
            When *include_lowest* is ``True``, the last bin includes both cutoffs.
            When *include_lowest* is ``False``, the first bin (bin 0) includes both
            cutoffs.

        Examples
        --------
        For these examples, we will use a frame with column *a* accessed by a Frame
        object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame with a column showing what bin the data is in.
        The data values should use strict_binning:

        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1      -1
        [1]    1      -1
        [2]    2      -1
        [3]    3      -1
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89      -1

        Modify the frame with a column showing what bin the data is in.
        The data value should not use strict_binning:


        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89       2

        Modify the frame with a column showing what bin the data is in.
        The bins should be lower inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       1
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       3
        [10]  89       3

        Modify the frame with a column showing what bin the data is in.
        The bins should be upper inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=False,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       1
        [9]   55       2
        [10]  89       3



        :param column_name: Name of the column to bin.
        :type column_name: unicode
        :param cutoffs: Array of values containing bin cutoff points.
            Array can be list or tuple.
            Array values must be progressively increasing.
            All bin boundaries must be included, so, with N bins, you need N+1 values.
        :type cutoffs: list
        :param include_lowest: (default=None)  Specify how the boundary conditions are handled.
            ``True`` indicates that the lower bound of the bin is inclusive.
            ``False`` indicates that the upper bound is inclusive.
            Default is ``True``.
        :type include_lowest: bool
        :param strict_binning: (default=None)  Specify how values outside of the cutoffs array should be binned.
            If set to ``True``, each value less than cutoffs[0] or greater than
            cutoffs[-1] will be assigned a bin value of -1.
            If set to ``False``, values less than cutoffs[0] will be included in the first
            bin while values greater than cutoffs[-1] will be included in the final
            bin.
        :type strict_binning: bool
        :param bin_column_name: (default=None)  The name for the new binned column.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column_equal_depth(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into groups with the same frequency.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal depth binning attempts to label rows such that each bin contains the
        same number of elements.
        For :math:`n` bins of a column :math:`C` of length :math:`m`, the bin
        number is determined by:

        .. math::

            \lceil n * \frac { f(C) }{ m } \rceil

        where :math:`f` is a tie-adjusted ranking function over values of
        :math:`C`.
        If there are multiples of the same value in :math:`C`, then their
        tie-adjusted rank is the average of their ordered rank values.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has a quantity of :math"`X`
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89


        Modify the frame, adding a column showing what bin the data is in.
        The data should be grouped into a maximum of five bins.
        Note that each bin will have the same quantity of members (as much as
        possible):

        >>> cutoffs = my_frame.bin_column_equal_depth('a', 5, 'aEDBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEDBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          1
        [3]    3          1
        [4]    5          2
        [5]    8          2
        [6]   13          3
        [7]   21          3
        [8]   34          4
        [9]   55          4
        [10]  89          4

        >>> print cutoffs
        [1.0, 2.0, 5.0, 13.0, 34.0, 89.0]


        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list containing the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def bin_column_equal_width(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into same-width groups.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal width binning places column values into groups such that the values
        in each group fall within the same interval and the interval width for each
        group is equal.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has 10
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the number of actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame, adding a column showing what bin the data is in.
        The data should be separated into a maximum of five bins and the bin cutoffs
        should be evenly spaced.
        Note that there may be bins with no members:

        >>> cutoffs = my_frame.bin_column_equal_width('a', 5, 'aEWBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEWBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          0
        [3]    3          0
        [4]    5          0
        [5]    8          0
        [6]   13          0
        [7]   21          1
        [8]   34          1
        [9]   55          3
        [10]  89          4

        The method returns a list of 6 cutoff values that define the edges of each bin.
        Note that difference between the cutoff values is constant:

        >>> print cutoffs
        [1.0, 18.6, 36.2, 53.8, 71.4, 89.0]



        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list of the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def categorical_summary(self, *column_inputs):
        """
        Compute a summary of the data in a column(s) for categorical or numerical data types.

        The returned value is a Map containing categorical summary for each specified column.

        For each column, levels which satisfy the top k and/or threshold cutoffs are displayed along
        with their frequency and percentage occurrence with respect to the total rows in the dataset.

        Missing data is reported when a column value is empty ("") or null.

        All remaining data is grouped together in the Other category and its frequency and percentage are reported as well.

        User must specify the column name and can optionally specify top_k and/or threshold.

        Optional parameters:

            top_k
                Displays levels which are in the top k most frequently occurring values for that column.

            threshold
                Displays levels which are above the threshold percentage with respect to the total row count.

            top_k and threshold
                Performs level pruning first based on top k and then filters out levels which satisfy the threshold criterion.

            defaults
                Displays all levels which are in Top 10.


        Examples
        --------


        .. code::

            >>> frame.categorical_summary('source','target')
            >>> frame.categorical_summary(('source', {'top_k' : 2}))
            >>> frame.categorical_summary(('source', {'threshold' : 0.5}))
            >>> frame.categorical_summary(('source', {'top_k' : 2}), ('target',
            ... {'threshold' : 0.5}))

        Sample output (for last example above):

            >>> {u'categorical_summary': [{u'column': u'source', u'levels': [
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'thing'},
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'abstraction'},
            ... {u'percentage': 0.25, u'frequency': 7, u'level': u'physical_entity'},
            ... {u'percentage': 0.10714285714285714, u'frequency': 3, u'level': u'entity'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Other'}]},
            ... {u'column': u'target', u'levels': [
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'thing'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2,
            ...  u'level': u'physical_entity'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'entity'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'variable'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'unit'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'substance'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'subject'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'set'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'reservoir'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'relation'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.5357142857142857, u'frequency': 15, u'level': u'Other'}]}]}



        :param *column_inputs: (default=None)  Comma-separated column names to summarize or tuple containing column name and dictionary of optional parameters. Optional parameters (see below for details): top_k (default = 10), threshold (default = 0.0)
        :type *column_inputs: str | tuple(str, dict)

        :returns: Summary for specified column(s) consisting of levels with their frequency and percentage
        :rtype: dict
        """
        return None


    @doc_stub
    def classification_metrics(self, label_column, pred_column, pos_label=None, beta=None, frequency_column=None):
        """
        Model statistics of accuracy, precision, and others.

        Calculate the accuracy, precision, confusion_matrix, recall and
        :math:`F_{ \beta}` measure for a classification model.

        *   The **f_measure** result is the :math:`F_{ \beta}` measure for a
            classification model.
            The :math:`F_{ \beta}` measure of a binary classification model is the
            harmonic mean of precision and recall.
            If we let:

            * beta :math:`\equiv \beta`,
            * :math:`T_{P}` denotes the number of true positives,
            * :math:`F_{P}` denotes the number of false positives, and
            * :math:`F_{N}` denotes the number of false negatives

            then:

            .. math::

                F_{ \beta} = (1 + \beta ^ 2) * \frac{ \frac{T_{P}}{T_{P} + F_{P}} * \
                \frac{T_{P}}{T_{P} + F_{N}}}{ \beta ^ 2 * \frac{T_{P}}{T_{P} + \
                F_{P}}  + \frac{T_{P}}{T_{P} + F_{N}}}

            The :math:`F_{ \beta}` measure for a multi-class classification model is
            computed as the weighted average of the :math:`F_{ \beta}` measure for
            each label, where the weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **recall** result of a binary classification model is the proportion
            of positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{N}` denote the number of false negatives, then the model
            recall is given by :math:`\frac {T_{P}} {T_{P} + F_{N}}`.

            For multi-class classification models, the recall measure is computed as
            the weighted average of the recall for each label, where the weight is
            the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **precision** of a binary classification model is the proportion of
            predicted positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{P}` denote the number of false positives, then the model
            precision is given by: :math:`\frac {T_{P}} {T_{P} + F_{P}}`.

            For multi-class classification models, the precision measure is computed
            as the weighted average of the precision for each label, where the
            weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **accuracy** of a classification model is the proportion of
            predictions that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives,
            :math:`T_{N}` denote the number of true negatives, and :math:`K` denote
            the total number of classified instances, then the model accuracy is
            given by: :math:`\frac{T_{P} + T_{N}}{K}`.

            This measure applies to binary and multi-class classifiers.

        *   The **confusion_matrix** result is a confusion matrix for a
            binary classifier model, formatted for human readability.

        Notes
        -----
        The **confusion_matrix** is not yet implemented for multi-class classifiers.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  a      b  labels  predictions
            ==================================
            [0]  red    1       0            0
            [1]  blue   3       1            0
            [2]  green  1       0            0
            [3]  green  0       1            1


            >>> cm = my_frame.classification_metrics('labels', 'predictions', 1, 1)
            [===Job Progress===]

            >>> cm.f_measure
            0.6666666666666666

            >>> cm.recall
            0.5

            >>> cm.accuracy
            0.75

            >>> cm.precision
            1.0

            >>> cm.confusion_matrix
                        Predicted_Pos  Predicted_Neg
            Actual_Pos              1              1
            Actual_Neg              0              2





        :param label_column: The name of the column containing the
            correct label for each instance.
        :type label_column: unicode
        :param pred_column: The name of the column containing the
            predicted label for each instance.
        :type pred_column: unicode
        :param pos_label: (default=None)  
        :type pos_label: None
        :param beta: (default=None)  This is the beta value to use for
            :math:`F_{ \beta}` measure (default F1 measure is computed); must be greater than zero.
            Defaults is 1.
        :type beta: float64
        :param frequency_column: (default=None)  The name of an optional column containing the
            frequency of observations.
        :type frequency_column: unicode

        :returns: The data returned is composed of multiple components\:

            |   <object>.accuracy : double
            |   <object>.confusion_matrix : table
            |   <object>.f_measure : double
            |   <object>.precision : double
            |   <object>.recall : double
        :rtype: dict
        """
        return None


    @doc_stub
    def column_median(self, data_column, weights_column=None):
        """
        Calculate the (weighted) median of a column.

        The median is the least value X in the range of the distribution so that
        the cumulative weight of values strictly below X is strictly less than half
        of the total weight and the cumulative weight of values up to and including X
        is greater than or equal to one-half of the total weight.

        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If a weight column is provided and no weights are finite numbers greater
        than 0, None is returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return middle number of values in column *a*:

        .. code::

           >>> median = my_frame.column_median('a')
           [===Job Progress===]
           >>> print median
           5

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return middle number of values in column 'a' with weights 'w':

        .. code::

           >>> median = my_frame.column_median('a', weights_column='w')
           [===Job Progress===]
           >>> print median
           3


        :param data_column: The column whose median is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies)
            for the median calculation.
            Must contain numerical data.
            Default is all items have a weight of 1.
        :type weights_column: unicode

        :returns: varies
                The median of the values.
                If a weight column is provided and no weights are finite numbers greater
                than 0, None is returned.
                The type of the median returned is the same as the contents of the data
                column, so a column of Longs will result in a Long median and a column of
                Floats will result in a Float median.
        :rtype: None
        """
        return None


    @doc_stub
    def column_mode(self, data_column, weights_column=None, max_modes_returned=None):
        """
        Evaluate the weights assigned to rows.

        Calculate the modes of a column.
        A mode is a data element of maximum weight.
        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight greater than 0,
        no mode is returned.

        Because data distributions often have multiple modes, it is possible for a
        set of modes to be returned.
        By default, only one is returned, but by setting the optional parameter
        max_modes_returned, a larger number of modes can be returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30
           

        Compute and return a dictionary containing summary statistics of column *a*:

        .. code::

           >>> mode = my_frame.column_mode('a')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 1), (u'modes', [3]), (u'total_weight', 7.0), (u'weight_of_mode', 2.0)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149
           

        Compute and return dictionary containing summary statistics of column 'a' with weights 'w':

        .. code::

           >>> mode = my_frame.column_mode('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 2), (u'modes', [2]), (u'total_weight', 6.200000144541264), (u'weight_of_mode', 1.7000000476837158)]



        :param data_column: Name of the column supplying the data.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of the column supplying the weights.
            Default is all items have weight of 1.
        :type weights_column: unicode
        :param max_modes_returned: (default=None)  Maximum number of modes returned.
            Default is 1.
        :type max_modes_returned: int32

        :returns: Dictionary containing summary statistics.
                The data returned is composed of multiple components\:

            mode : A mode is a data element of maximum net weight.
                A set of modes is returned.
                The empty set is returned when the sum of the weights is 0.
                If the number of modes is less than or equal to the parameter
                max_modes_returned, then all modes of the data are
                returned.
                If the number of modes is greater than the max_modes_returned
                parameter, only the first max_modes_returned many modes (per a
                canonical ordering) are returned.
            weight_of_mode : Weight of a mode.
                If there are no data elements of finite weight greater than 0,
                the weight of the mode is 0.
                If no weights column is given, this is the number of appearances
                of each mode.
            total_weight : Sum of all weights in the weight column.
                This is the row count if no weights are given.
                If no weights column is given, this is the number of rows in
                the table with non-zero weight.
            mode_count : The number of distinct modes in the data.
                In the case that the data is very multimodal, this number may
                exceed max_modes_returned.


        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def column_names(self):
        """
        Column identifications in the current frame.

        Returns the names of the columns of the current frame.

        Examples
        --------

        .. code::


            >>> frame.column_names
            [u'name', u'age', u'tenure', u'phone']





        :returns: list of names of all the frame's columns
        :rtype: list
        """
        return None


    @doc_stub
    def column_summary_statistics(self, data_column, weights_column=None, use_population_variance=None):
        """
        Calculate multiple statistics for a column.

        Notes
        -----
        Sample Variance
            Sample Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W - 1} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Population Variance
            Population Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Standard Deviation
            The square root of the variance.

        Logging Invalid Data
            A row is bad when it contains a NaN or infinite value in either
            its data or weights column.
            In this case, it contributes to bad_row_count; otherwise it
            contributes to good row count.

            A good row can be skipped because the value in its weight
            column is less than or equal to 0.
            In this case, it contributes to non_positive_weight_count, otherwise
            (when the weight is greater than 0) it contributes to
            valid_data_weight_pair_count.

        **Equations**

            .. code::

                bad_row_count + good_row_count = # rows in the frame
                positive_weight_count + non_positive_weight_count = good_row_count

            In particular, when no weights column is provided and all weights are 1.0:

            .. code::

                non_positive_weight_count = 0 and
                positive_weight_count = good_row_count

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return summary statistics for values in column *a*:

        .. code::

           >>> summary_statistics = my_frame.column_summary_statistics('a')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 5.6725751451901045), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 8.571428571428571), (u'mean_confidence_lower', 1.277083729932067), (u'mean_confidence_upper', 15.865773412925076), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 9.846440014156434), (u'total_weight', 7.0), (u'variance', 96.95238095238095)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return summary statistics values in column 'a' with weights 'w':

        .. code::
           >>> summary_statistics = my_frame.column_summary_statistics('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 4.039682869616821), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 5.032258048622591), (u'mean_confidence_lower', 1.4284724667085964), (u'mean_confidence_upper', 8.636043630536586), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 4.578241754132706), (u'total_weight', 6.200000144541264), (u'variance', 20.96029755928412)]


        :param data_column: The column to be statistically summarized.
            Must contain numerical data; all NaNs and infinite values are excluded
            from the calculation.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of column holding weights of
            column values.
        :type weights_column: unicode
        :param use_population_variance: (default=None)  If true, the variance is calculated
            as the population variance.
            If false, the variance calculated as the sample variance.
            Because this option affects the variance, it affects the standard
            deviation and the confidence intervals as well.
            Default is false.
        :type use_population_variance: bool

        :returns: Dictionary containing summary statistics.
            The data returned is composed of multiple components\:

            |   mean : [ double | None ]
            |       Arithmetic mean of the data.
            |   geometric_mean : [ double | None ]
            |       Geometric mean of the data. None when there is a data element <= 0, 1.0 when there are no data elements.
            |   variance : [ double | None ]
            |       None when there are <= 1 many data elements. Sample variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight minus 1. None when the sum of the weights is <= 1. Population variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight.
            |   standard_deviation : [ double | None ]
            |       The square root of the variance. None when  sample variance is being used and the sum of weights is <= 1.
            |   total_weight : long
            |       The count of all data elements that are finite numbers. In other words, after excluding NaNs and infinite values.
            |   minimum : [ double | None ]
            |       Minimum value in the data. None when there are no data elements.
            |   maximum : [ double | None ]
            |       Maximum value in the data. None when there are no data elements.
            |   mean_confidence_lower : [ double | None ]
            |       Lower limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   mean_confidence_upper : [ double | None ]
            |       Upper limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   bad_row_count : [ double | None ]
            |       The number of rows containing a NaN or infinite value in either the data or weights column.
            |   good_row_count : [ double | None ]
            |       The number of rows not containing a NaN or infinite value in either the data or weights column.
            |   positive_weight_count : [ double | None ]
            |       The number of valid data elements with weight > 0. This is the number of entries used in the statistical calculation.
            |   non_positive_weight_count : [ double | None ]
            |       The number valid data elements with finite weight <= 0.
        :rtype: dict
        """
        return None


    @doc_stub
    def copy(self, columns=None, where=None, name=None):
        """
        Create new frame from current frame.

        Copy frame or certain frame columns entirely or filtered.
        Useful for frame query.

        Examples
        --------

        .. code::

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode, tenured_name_age:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame2 = frame.copy()  # full copy of the frame
            [===Job Progress===]

            >>> frame3 = frame.copy(['name', 'age'])  # copy only two columns
            [===Job Progress===]
            >>> frame3
            Frame  <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32]
            status = ACTIVE  (last_read_date = -etc-)

        .. code::

            >>> frame4 = frame.copy({'name': 'name', 'age': 'age', 'tenure': 'years'},
            ...                     where=lambda row: row.age > 40)
            [===Job Progress===]
            >>> frame4.inspect()
            [#]  name      age  years
            =========================
            [0]  Thurston   65     26
            [1]  Judy       44     14



        :param columns: (default=None)  If not None, the copy will only include the columns specified. If dict, the string pairs represent a column renaming, {source_column_name: destination_column_name}
        :type columns: str | list of str | dict
        :param where: (default=None)  If not None, only those rows for which the UDF evaluates to True will be copied.
        :type where: function
        :param name: (default=None)  Name of the copied frame
        :type name: str

        :returns: A new Frame of the copied data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def correlation(self, data_column_names):
        """
        Calculate correlation for two columns of current frame.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation computes the common correlation coefficient (Pearson's) on the pair
        of columns provided.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051 .


            >>> my_frame.correlation(["x1", "x2"])
            [===Job Progress===]

                -1.0
            >>> my_frame.correlation(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.correlation(["x2", "x3"])
            [===Job Progress===]

                -0.948683298051




        :param data_column_names: The names of 2 columns from which
            to compute the correlation.
        :type data_column_names: list

        :returns: Pearson correlation coefficient of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def correlation_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate correlation matrix for two or more columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation_matrix computes the common correlation coefficient (Pearson's) on each pair
        of columns in the user-provided list.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051

            >>> corr_matrix = my_frame.correlation_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> corr_matrix.inspect()
            [#]  idnum           x1              x2               x3               x4
            ==========================================================================
            [0]             1.0             1.0             -1.0   0.948683298051  0.0
            [1]             1.0             1.0             -1.0   0.948683298051  0.0
            [2]            -1.0            -1.0              1.0  -0.948683298051  0.0
            [3]  0.948683298051  0.948683298051  -0.948683298051              1.0  0.0
            [4]             0.0             0.0              0.0              0.0  1.0





        :param data_column_names: The names of the columns from
            which to compute the matrix.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name for the returned
            matrix Frame.
        :type matrix_name: unicode

        :returns: A Frame with the matrix of the correlation values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def count(self, where):
        """
        Counts the number of rows which meet given criteria.

        Examples
        --------


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.count(lambda row: row.age > 35)
            [===Job Progress===]
            3



        :param where: |UDF| which evaluates a row to a boolean
        :type where: function

        :returns: number of rows for which the where |UDF| evaluated to True.
        :rtype: int
        """
        return None


    @doc_stub
    def covariance(self, data_column_names):
        """
        Calculate covariance for exactly two columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance computes the covariance on the pair of columns provided.

            >>> my_frame.covariance(["x1", "x2"])
            [===Job Progress===]

                -2.5
            >>> my_frame.covariance(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.covariance(["x2", "x3"])
            [===Job Progress===]

                -1.5




        :param data_column_names: The names of two columns from which
            to compute the covariance.
        :type data_column_names: list

        :returns: Covariance of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def cumulative_percent(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative percent sum is computed by sequentially stepping through the
        rows, observing the column values and keeping track of the current percentage of the total sum
        accounted for at the current value.


        Notes
        -----
        This method applies only to columns containing numerical data.
        Although this method will execute for columns containing negative
        values, the interpretation of the result will change (for example,
        negative percentages).

        Examples
        --------
        Consider Frame *my_frame* accessing a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent sum for column *obs* is obtained by:

            >>> my_frame.cumulative_percent('obs')
            [===Job Progress===]

        The Frame *my_frame* now contains two columns *obs* and
        *obsCumulativePercentSum*.
        They contain the original data and the cumulative percent sum,
        respectively:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_percent
            ================================
            [0]    0                     0.0
            [1]    1          0.166666666667
            [2]    2                     0.5
            [3]    0                     0.5
            [4]    1          0.666666666667
            [5]    2                     1.0


        :param sample_col: The name of the column from which to compute
            the cumulative percent sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def cumulative_sum(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative sum is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the cumulative sum for each value.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative sum for column *obs* is obtained by:

            >>> my_frame.cumulative_sum('obs')
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativeSum* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_sum
            ============================
            [0]    0                 0.0
            [1]    1                 1.0
            [2]    2                 3.0
            [3]    0                 3.0
            [4]    1                 4.0
            [5]    2                 6.0

        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def daal_covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Uses Intel Data Analytics and Acceleration Library (DAAL) to compute covariance matrix.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.daal_covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.daal_covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def dot_product(self, left_column_names, right_column_names, dot_product_column_name, default_left_values=None, default_right_values=None):
        """
        Calculate dot product for each row in current frame.

        Calculate the dot product for each row in a frame using values from two
        equal-length sequences of columns.

        Dot product is computed by the following formula:

        The dot product of two vectors :math:`A=[a_1, a_2, ..., a_n]` and
        :math:`B =[b_1, b_2, ..., b_n]` is :math:`a_1*b_1 + a_2*b_2 + ...+ a_n*b_n`.
        The dot product for each row is stored in a new column in the existing frame.

        Notes
        -----
        If default_left_values or default_right_values are not specified, any null
        values will be replaced by zeros.

        Examples
        --------
        Calculate the dot product for a sequence of columns in Frame object *my_frame*:

        .. code::

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3
            ===============================
            [0]      1    0.2     -2      5
            [1]      2    0.4     -1      6
            [2]      3    0.6      0      7
            [3]      4    0.8      1      8


        Modify the frame by computing the dot product for a sequence of columns:

        .. code::

             >>> my_frame.dot_product(['col_0','col_1'], ['col_2', 'col_3'], 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3  dot_product
            ============================================
            [0]      1    0.2     -2      5         -1.0
            [1]      2    0.4     -1      6          0.4
            [2]      3    0.6      0      7          4.2
            [3]      4    0.8      1      8         10.4


        Calculate the dot product for columns of vectors in Frame object *my_frame*:


        .. code::
             >>> my_frame.dot_product('col_4', 'col_5', 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_4       col_5        dot_product
            =========================================
            [0]  [1.0, 0.2]  [-2.0, 5.0]         -1.0
            [1]  [2.0, 0.4]  [-1.0, 6.0]          0.4
            [2]  [3.0, 0.6]  [0.0, 7.0]           4.2
            [3]  [4.0, 0.8]  [1.0, 8.0]          10.4


        :param left_column_names: Names of columns used to create the left vector (A) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type left_column_names: list
        :param right_column_names: Names of columns used to create right vector (B) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type right_column_names: list
        :param dot_product_column_name: Name of column used to store the
            dot product.
        :type dot_product_column_name: unicode
        :param default_left_values: (default=None)  Default values used to substitute null values in left vector.
            Default is None.
        :type default_left_values: list
        :param default_right_values: (default=None)  Default values used to substitute null values in right vector.
            Default is None.
        :type default_right_values: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def download(self, n=100, offset=0, columns=None):
        """
        Download frame data from the server into client workspace as a pandas dataframe

        Similar to the 'take' function, but puts the data in a pandas dataframe.

        Examples
        --------

        .. code::

            >>> pandas_frame = frame.download(columns=['name', 'phone'])
            >>> pandas_frame
                   name     phone
            0      Fred  555-1234
            1     Susan  555-0202
            2  Thurston  555-4510
            3      Judy  555-2183



        :param n: (default=100)  The number of rows to download to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before copying
        :type offset: int
        :param columns: (default=None)  Column filter, the names of columns to be included (default is all columns)
        :type columns: list

        :returns: A new pandas dataframe object containing the downloaded frame data
        :rtype: pandas.DataFrame
        """
        return None


    @doc_stub
    def drop_columns(self, columns):
        """
        Remove columns from the frame.

        The data from the columns is lost.

        Notes
        -----
        It is not possible to delete all columns from a frame.
        At least one column needs to remain.
        If it is necessary to delete all columns, then delete the frame.

        Examples
        --------
        For this example, the Frame object *my_frame* accesses a frame with 4 columns
        columns *column_a*, *column_b*, *column_c* and *column_d* and drops 2 columns *column_b* and *column_d* using drop columns.



            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_b', <type 'numpy.int32'>), (u'column_c', <type 'unicode'>), (u'column_d', <type 'numpy.int32'>)]


        Eliminate columns *column_b* and *column_d*:

            >>> my_frame.drop_columns(["column_b", "column_d"])
            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_c', <type 'unicode'>)]

        Now the frame only has the columns *column_a* and *column_c*.
        For further examples, see: ref:`example_frame.drop_columns`.




        :param columns: Column name OR list of column names to be removed from the frame.
        :type columns: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_duplicates(self, unique_columns=None):
        """
        Modify the current frame, removing duplicate rows.

        Remove data rows which are the same as other rows.
        The entire row can be checked for duplication, or the search for duplicates
        can be limited to one or more columns.
        This modifies the current frame.

        Given a frame with data:

        .. code::


            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  200  4  25
            [1]  200  5  25
            [2]  200  4  25
            [3]  200  5  35
            [4]  200  6  25
            [5]  200  8  35
            [6]  200  4  45
            [7]  200  4  25
            [8]  200  5  25
            [9]  201  4  25

        Remove any rows that are identical to a previous row.
        The result is a frame of unique rows.
        Note that row order may change.

        .. code::

            >>> frame.drop_duplicates()
            [===Job Progress===]
            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  201  4  25
            [1]  200  4  25
            [2]  200  5  25
            [3]  200  8  35
            [4]  200  6  25
            [5]  200  5  35
            [6]  200  4  45


        Now remove any rows that have the same data in columns *a* and
        *c* as a previously checked row:

        .. code::

            >>> frame.drop_duplicates([ "a", "c"])
            [===Job Progress===]

        The result is a frame with unique values for the combination of columns *a*
        and *c*.

        .. code::

            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  201  4  25
            [1]  200  4  45
            [2]  200  4  25
            [3]  200  8  35


        :param unique_columns: (default=None)  
        :type unique_columns: None

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_rows(self, predicate):
        """
        Erase any row in the current frame which qualifies.

        Examples
        --------

        .. code::


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.drop_rows(lambda row: row.name[-1] == 'n')  # drop people whose name ends in 'n'
            [===Job Progress===]
            >>> frame.inspect()
            [#]  name  age  tenure  phone
            ================================
            [0]  Fred   39      16  555-1234
            [1]  Judy   44      14  555-2183

        More information on a |UDF| can be found at :doc:`/ds_apir`.


        :param predicate: |UDF| which evaluates a row to a boolean; rows that answer True are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def ecdf(self, column, result_frame_name=None):
        """
        Builds new frame with columns for data and distribution.

        Generates the empirical cumulative distribution for the input column.

        Consider the following sample data set in *frame* 'frame' containing several numbers.


        >>> frame.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        4
        [7]        3
        >>> ecdf_frame = frame.ecdf('numbers')
        [===Job Progress===]
        >>> ecdf_frame.inspect()
        [#]  numbers  numbers_ECDF
        ==========================
        [0]        0         0.125
        [1]        1           0.5
        [2]        2         0.625
        [3]        3         0.875
        [4]        4           1.0



        :param column: The name of the input column containing sample.
        :type column: unicode
        :param result_frame_name: (default=None)  A name for the resulting frame which is created
            by this operation.
        :type result_frame_name: unicode

        :returns: A new Frame containing each distinct value in the sample and its corresponding ECDF value.
        :rtype: Frame
        """
        return None


    @doc_stub
    def entropy(self, data_column, weights_column=None):
        """
        Calculate the Shannon entropy of a column.

        The data column is weighted via the weights column.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements with a finite weight greater than 0,
        the entropy is zero.

        Consider the following sample data set in *frame* 'frame' containing several numbers.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data  weight
        =================
        [0]     0       1
        [1]     1       2
        [2]     2       4
        [3]     4       8
        >>> entropy = frame.entropy("data", "weight")
        [===Job Progress===]

        >>> "%0.8f" % entropy
        '1.13691659'



        If we have more choices and weights, the computation is not as simple.
        An on-line search for "Shannon Entropy" will provide more detail.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data
        =========
        [0]  H
        [1]  T
        [2]  H
        [3]  T
        [4]  H
        [5]  T
        [6]  H
        [7]  T
        [8]  H
        [9]  T
        >>> entropy = frame.entropy("data")
        [===Job Progress===]
        >>> "%0.8f" % entropy
        '0.69314718'



        :param data_column: The column whose entropy is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the entropy calculation.
            Must contain numerical data.
            Default is using uniform weights of 1 for all items.
        :type weights_column: unicode

        :returns: Entropy.
        :rtype: float64
        """
        return None


    @doc_stub
    def export_to_csv(self, folder_name, separator=',', count=-1, offset=0):
        """
        Write current frame to HDFS in csv format.

        Export the frame to a file in csv format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_csv('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"



        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param separator: (default=,)  The separator for separating the values.
            Default is comma (,).
        :type separator: unicode
        :param count: (default=-1)  The number of records you want.
            Default, or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def export_to_hbase(self, table_name, key_column_name=None, family_name='familyColumn'):
        """
        Write current frame to HBase table.

        Table must exist in HBase.
        Export of Vectors is not currently supported.

        Examples
        --------

        Overwrite/append scenarios (see below):

        1. create a simple hbase table from csv
               load csv into a frame using existing frame api
               save the frame into hbase (it creates a table - lets call it table1)

        2. overwrite existing table with new data
               do scenario 1 and create table1
               load the second csv into a frame
               save the frame into table1 (old data is gone)

        3. append data to the existing table 1
               do scenario 1 and create table1
               load table1 into frame1
               load csv into frame2
               let frame1 = frame1 + frame2 (concatenate frame2 into frame1)
               save frame1 into base as table1 (overwrite with initial + appended data)


        Vector scenarios (see below):

        Vectors are not directly supported by HBase (which represents data as byte arrays) or the plugin.
        While is true that a vector can be saved because of the byte array conversion for hbase, the following
        is actually the recommended practice:

        1. Convert the vector to csv (in python, outside ATK)
        2. save the csv as string in the database (using ATK export_to_hbase)
        3. read the cell as string (using ATK, read from hbase
        4. convert the csv to vector (in python, outside ATK)




        :param table_name: The name of the HBase table that will contain the exported frame
        :type table_name: unicode
        :param key_column_name: (default=None)  The name of the column to be used as row key in hbase table
        :type key_column_name: unicode
        :param family_name: (default=familyColumn)  The family name of the HBase table that will contain the exported frame
        :type family_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_hive(self, table_name):
        """
        Write  current frame to Hive table.

        Table must not exist in Hive. Hive does not support case sensitive table names and columns names. Hence column names with uppercase letters will be converted to lower case by Hive.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_hive('covarianceresults')

        :param table_name: The name of the Hive table that will contain the exported frame
        :type table_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_jdbc(self, table_name, connector_type='postgres'):
        """
        Write current frame to JDBC table.

        Table will be created or appended to.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_jdbc('covarianceresults')



        :param table_name: JDBC table name
        :type table_name: unicode
        :param connector_type: (default=postgres)  (optional) JDBC connector, either mysql or postgres. Default is postgres
        :type connector_type: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_json(self, folder_name, count=0, offset=0):
        """
        Write current frame to HDFS in JSON format.

        Export the frame to a file in JSON format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_json('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"


        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param count: (default=0)  The number of records you want.
            Default (0), or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def filter(self, predicate):
        """
        Select all rows which satisfy a predicate.

        Modifies the current frame to save defined rows and delete everything
        else.

        Examples
        --------

            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.filter(lambda row: row.tenure >= 15)  # keep only people with 15 or more years tenure
            [===Job Progress===]
            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Thurston   65      26  555-4510

        More information on a |UDF| can be found at :doc:`/ds_apir`.


        :param predicate: |UDF| which evaluates a row to a boolean; rows that answer False are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def flatten_columns(self, columns, delimiters=None):
        """
        Spread data to multiple rows based on cell data.

        Splits cells in the specified columns into multiple rows according to a string
        delimiter.
        New rows are a full copy of the original row, but the specified columns only
        contain one value.
        The original row is deleted.

        Examples
        --------

        Given a data file::

            1-solo,mono,single-green,yellow,red
            2-duo,double-orange,black

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32), ('b', str),('c',str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32),
                ... ('b', str),('c', str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)


        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a  b                 c
            ==========================================
            [0]  1  solo,mono,single  green,yellow,red
            [1]  2  duo,double        orange,black

        Now, spread out those sub-strings in column *b* and *c*:

        .. code::

            >>> frame.flatten_columns(['b','c'], ',')
            [===Job Progress===]

        Note that the delimiters parameter is optional, and if no delimiter is specified, the default
        is a comma (,).  So, in the above example, the delimiter parameter could be omitted.  Also, if
        the delimiters are different for each column being flattened, a list of delimiters can be
        provided.  If a single delimiter is provided, it's assumed that we are using the same delimiter
        for all columns that are being flattened.  If more than one delimiter is provided, the number of
        delimiters must match the number of string columns being flattened.

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a  b       c
            ======================
            [0]  1  solo    green
            [1]  1  mono    yellow
            [2]  1  single  red
            [3]  2  duo     orange
            [4]  2  double  black


        Alternatively, flatten_columns also accepts a single column name (instead of a list) if just one
        column is being flattened.  For example, we could have called flatten_column on just column *b*:


        .. code::

            >>> frame.flatten_columns('b', ',')
            [===Job Progress===]

        Check again:

        .. code ::

            >>> frame.inspect()
            [#]  a  b       c
            ================================
            [0]  1  solo    green,yellow,red
            [1]  1  mono    green,yellow,red
            [2]  1  single  green,yellow,red
            [3]  2  duo     orange,black
            [4]  2  double  orange,black





        :param columns: The columns to be flattened.
        :type columns: list
        :param delimiters: (default=None)  The list of delimiter strings for each column.
            Default is comma (,).
        :type delimiters: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def get_error_frame(self):
        """
        Get a frame with error recordings.

        When a frame is created, another frame is transparently
        created to capture parse errors.

        Returns
        -------
        Frame : error frame object
            A new object accessing a frame that contains the parse errors of
            the currently active Frame or None if no error frame exists.



        """
        return None


    @doc_stub
    def group_by(self, group_by_columns, *aggregation_arguments):
        """
        Create summarized frame.

        Creates a new frame and returns a Frame object to access it.
        Takes a column or group of columns, finds the unique combination of
        values, and creates unique rows with these column values.
        The other columns are combined according to the aggregation
        argument(s).

        Notes
        -----
        *   Column order is not guaranteed when columns are added
        *   The column names created by aggregation functions in the new frame
            are the original column name appended with the '_' character and
            the aggregation function.
            For example, if the original field is *a* and the function is
            *avg*, the resultant column is named *a_avg*.
        *   An aggregation argument of *count* results in a column named
            *count*.
        *   The aggregation function *agg.count* is the only full row
            aggregation function supported at this time.
        *   Aggregation currently supports using the following functions:

            *   avg
            *   count
            *   count_distinct
            *   max
            *   min
            *   stdev
            *   sum
            *   var (see glossary Bias vs Variance)
            *   The aggregation arguments also accepts the User Defined function(UDF). UDF acts on each row

        Examples
        --------
        For setup, we will use a Frame *my_frame* accessing a frame with a
        column *a*:

        .. code::


            >>> frame.inspect()
            [#]  a  b        c     d       e  f    g
            ========================================
            [0]  1  alpha     3.0  small   1  3.0  9
            [1]  1  bravo     5.0  medium  1  4.0  9
            [2]  1  alpha     5.0  large   1  8.0  8
            [3]  2  bravo     8.0  large   1  5.0  7
            [4]  2  charlie  12.0  medium  1  6.0  6
            [5]  2  bravo     7.0  small   1  8.0  5
            [6]  2  bravo    12.0  large   1  6.0  4

            Count the groups in column 'b'

            >>> b_count = frame.group_by('b', ta.agg.count)
            [===Job Progress===]
            >>> b_count.inspect()
            [#]  b        count
            ===================
            [0]  alpha        2
            [1]  bravo        4
            [2]  charlie      1

            >>> avg1 = frame.group_by(['a', 'b'], {'c' : ta.agg.avg})
            [===Job Progress===]
            >>> avg1.inspect()
            [#]  a  b        c_AVG
            ======================
            [0]  2  bravo      9.0
            [1]  1  alpha      4.0
            [2]  2  charlie   12.0
            [3]  1  bravo      5.0

            >>> mix_frame = frame.group_by('a', ta.agg.count, {'f': [ta.agg.avg, ta.agg.sum, ta.agg.min], 'g': ta.agg.max})
            [===Job Progress===]
            >>> mix_frame.inspect()
            [#]  a  count  g_MAX  f_AVG  f_SUM  f_MIN
            =========================================
            [0]  1      3      9    5.0   15.0    3.0
            [1]  2      4      7   6.25   25.0    5.0

            >>> def custom_agg(acc, row):
            ...     acc.c_sum = acc.c_sum + row.c
            ...     acc.c_prod= acc.c_prod*row.c

            >>> sum_prod_frame = frame.group_by(['a', 'b'], ta.agg.udf(aggregator=custom_agg,output_schema=[('c_sum', ta.float64),('c_prod', ta.float64)],init_values=[0,1]))
            [===Job Progress===]

            >>> sum_prod_frame.inspect()
            [#]  a  b        c_sum  c_prod
            ==============================
            [0]  2  bravo     27.0   672.0
            [1]  1  alpha      8.0    15.0
            [2]  2  charlie   12.0    12.0
            [3]  1  bravo      5.0     5.0

        For further examples, see :ref:`example_frame.group_by`.


        :param group_by_columns: Column name or list of column names
        :type group_by_columns: list
        :param *aggregation_arguments: (default=None)  Aggregation function based on entire row, and/or dictionaries (one or more) of { column name str : aggregation function(s) }.
        :type *aggregation_arguments: dict

        :returns: A new frame with the results of the group_by
        :rtype: Frame
        """
        return None


    @doc_stub
    def histogram(self, column_name, num_bins=None, weight_column_name=None, bin_type='equalwidth'):
        """
        Compute the histogram for a column in a frame.

        Compute the histogram of the data in a column.
        The returned value is a Histogram object containing 3 lists one each for:
        the cutoff points of the bins, size of each bin, and density of each bin.

        **Notes**

        The num_bins parameter is considered to be the maximum permissible number
        of bins because the data may dictate fewer bins.
        With equal depth binning, for example, if the column to be binned has 10
        elements with only 2 distinct values and the *num_bins* parameter is
        greater than 2, then the number of actual number of bins will only be 2.
        This is due to a restriction that elements with an identical value must
        belong to the same bin.

        Examples
        --------

        Consider the following sample data set\:

        .. code::

            >>> frame.inspect()
                [#]  a  b
                =========
                [0]  a  2
                [1]  b  7
                [2]  c  3
                [3]  d  9
                [4]  e  1

        A simple call for 3 equal-width bins gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3)
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 3.6666666666666665, 6.333333333333333, 9.0],
            hist: [3.0, 0.0, 2.0],
            density: [0.6, 0.0, 0.4]

        Switching to equal depth gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3, bin_type='equaldepth')
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 2.0, 7.0, 9.0],
            hist: [1.0, 2.0, 2.0],
            density: [0.2, 0.4, 0.4]

        .. only:: html

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - hist.cutoffs[0])
        .. only:: latex

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - 
                ... hist.cutoffs[0])


        :param column_name: Name of column to be evaluated.
        :type column_name: unicode
        :param num_bins: (default=None)  Number of bins in histogram.
            Default is Square-root choice will be used
            (in other words math.floor(math.sqrt(frame.row_count)).
        :type num_bins: int32
        :param weight_column_name: (default=None)  Name of column containing weights.
            Default is all observations are weighted equally.
        :type weight_column_name: unicode
        :param bin_type: (default=equalwidth)  The type of binning algorithm to use: ["equalwidth"|"equaldepth"]
            Defaults is "equalwidth".
        :type bin_type: unicode

        :returns: histogram
                A Histogram object containing the result set.
                The data returned is composed of multiple components:
            cutoffs : array of float
                A list containing the edges of each bin.
            hist : array of float
                A list containing count of the weighted observations found in each bin.
            density : array of float
                A list containing a decimal containing the percentage of
                observations found in the total set per bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def inspect(self, n=10, offset=0, columns=None, wrap='inspect_settings', truncate='inspect_settings', round='inspect_settings', width='inspect_settings', margin='inspect_settings', with_types='inspect_settings'):
        """
        Pretty-print of the frame data

        Essentially returns a string, but technically returns a RowInspection object which renders a string.
        The RowInspection object naturally converts to a str when needed, like when printed or when displayed
        by python REPL (i.e. using the object's __repr__).  If running in a script and want the inspect output
        to be printed, then it must be explicitly printed, then `print frame.inspect()`


        Examples
        --------
        To look at the first 4 rows of data in a frame:

        .. code::

            >>> frame.inspect(4)
            [#]  animal    name    age  weight
            ==================================
            [0]  human     George    8   542.5
            [1]  human     Ursula    6   495.0
            [2]  ape       Ape      41   400.0
            [3]  elephant  Shep      5  8630.0

        # For other examples, see :ref:`example_frame.inspect`.

        Note: if the frame data contains unicode characters, this method may raise a Unicode exception when
        running in an interactive REPL or otherwise which triggers the standard python repr().  To get around
        this problem, explicitly print the unicode of the returned object:

        .. code::

            >>> print unicode(frame.inspect())


        **Global Settings**

        If not specified, the arguments that control formatting receive default values from
        'trustedanalytics.inspect_settings'.  Make changes there to affect all calls to inspect.

        .. code::

            >>> import trustedanalytics as ta
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = 120  # changes inspect to use 120 width globally
            >>> ta.inspect_settings.truncate = 16  # changes inspect to always truncate strings to 16 chars
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width           120
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = None  # return value back to default
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.reset()  # set everything back to default
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False

        ..


        :param n: (default=10)  The number of rows to print (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before printing.
        :type offset: int
        :param columns: (default=None)  Filter columns to be included.  By default, all columns are included
        :type columns: int
        :param wrap: (default=inspect_settings)  If set to 'stripes' then inspect prints rows in stripes; if set to an integer N, rows will be printed in clumps of N columns, where the columns are wrapped
        :type wrap: int or 'stripes'
        :param truncate: (default=inspect_settings)  If set to integer N, all strings will be truncated to length N, including a tagged ellipses
        :type truncate: int
        :param round: (default=inspect_settings)  If set to integer N, all floating point numbers will be rounded and truncated to N digits
        :type round: int
        :param width: (default=inspect_settings)  If set to integer N, the print out will try to honor a max line width of N
        :type width: int
        :param margin: (default=inspect_settings)  ('stripes' mode only) If set to integer N, the margin for printing names in a stripe will be limited to N characters
        :type margin: int
        :param with_types: (default=inspect_settings)  If set to True, header will include the data_type of each column
        :type with_types: bool

        :returns: An object which naturally converts to a pretty-print string
        :rtype: RowsInspection
        """
        return None


    @doc_stub
    def join(self, right, left_on, right_on=None, how='inner', name=None):
        """
        Join operation on one or two frames, creating a new frame.

        Create a new frame from a SQL JOIN operation with another frame.
        The frame on the 'left' is the currently active frame.
        The frame on the 'right' is another frame.
        This method take column(s) in the left frame and matches its values
        with column(s) in the right frame.
        Using the default 'how' option ['inner'] will only allow data in the
        resultant frame if both the left and right frames have the same value
        in the matching column(s).
        Using the 'left' 'how' option will allow any data in the resultant
        frame if it exists in the left frame, but will allow any data from the
        right frame if it has a value in its column(s) which matches the value in
        the left frame column(s).
        Using the 'right' option works similarly, except it keeps all the data
        from the right frame and only the data from the left frame when it
        matches.
        The 'outer' option provides a frame with data from both frames where
        the left and right frames did not have the same value in the matching
        column(s).

        Notes
        -----
        When a column is named the same in both frames, it will result in two
        columns in the new frame.
        The column from the *left* frame (originally the current frame) will be
        copied and the column name will have the string "_L" added to it.
        The same thing will happen with the column from the *right* frame,
        except its name has the string "_R" appended. The order of columns
        after this method is called is not guaranteed.

        It is recommended that you rename the columns to meaningful terms prior
        to using the ``join`` method.
        Keep in mind that unicode in column names will likely cause the
        drop_frames() method (and others) to fail!

        Examples
        --------


        Consider two frames: codes and colors

        >>> codes.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        5
        [7]        3


        >>> colors.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        2  yellow
        [2]        3  green
        [3]        4  blue


        Join them on the 'numbers' column ('inner' join by default)

        >>> j = codes.join(colors, 'numbers')
        [===Job Progress===]

        >>> j.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        3  green
        [2]        1  red
        [3]        2  yellow
        [4]        1  red
        [5]        3  green

        (The join adds an extra column *_R which is the join column from the right frame; it may be disregarded)

        Try a 'left' join, which includes all the rows of the codes frame.

        >>> j_left = codes.join(colors, 'numbers', how='left')
        [===Job Progress===]

        >>> j_left.inspect()
        [#]  numbers_L  color
        ======================
        [0]          1  red
        [1]          3  green
        [2]          1  red
        [3]          0  None
        [4]          2  yellow
        [5]          1  red
        [6]          5  None
        [7]          3  green


        And an outer join:

        >>> j_outer = codes.join(colors, 'numbers', how='outer')
        [===Job Progress===]

        >>> j_outer.inspect()
        [#]  numbers_L  color
        ======================
        [0]          0  None
        [1]          1  red
        [2]          1  red
        [3]          1  red
        [4]          2  yellow
        [5]          3  green
        [6]          3  green
        [7]          4  blue
        [8]          5  None

        Consider two frames: country_codes_frame and country_names_frame

        >>> country_codes_frame.inspect()
        [#]  col_0  col_1  col_2
        ========================
        [0]      1    354  a
        [1]      2     91  a
        [2]      2    100  b
        [3]      3     47  a
        [4]      4    968  c
        [5]      5     50  c


        >>> country_names_frame.inspect()
        [#]  col_0  col_1     col_2
        ===========================
        [0]      1  Iceland   a
        [1]      1  Ice-land  a
        [2]      2  India     b
        [3]      3  Norway    a
        [4]      4  Oman      c
        [5]      6  Germany   c

        Join them on the 'col_0' and 'col_2' columns ('inner' join by default)

        >>> composite_join = country_codes_frame.join(country_names_frame, ['col_0', 'col_2'])
        [===Job Progress===]

        >>> composite_join.inspect()
        [#]  col_0  col_1_L  col_2  col_1_R
        ====================================
        [0]      1      354  a      Ice-land
        [1]      1      354  a      Iceland
        [2]      2      100  b      India
        [3]      3       47  a      Norway
        [4]      4      968  c      Oman

        More examples can be found in the :ref:`user manual
        <example_frame.join>`.


        :param right: Another frame to join with
        :type right: Frame
        :param left_on: Names of the columns in the left frame used to match up the two frames.
        :type left_on: list
        :param right_on: (default=None)  Names of the columns in the right frame used to match up the two frames. Default is the same as the left frame.
        :type right_on: list
        :param how: (default=inner)  How to qualify the data to be joined together.  Must be one of the following:  'left', 'right', 'inner', 'outer'.  Default is 'inner'
        :type how: str
        :param name: (default=None)  Name of the result grouped frame
        :type name: str

        :returns: A new frame with the results of the join
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def last_read_date(self):
        """
        Last time this frame's data was accessed.

        Examples
        --------

        .. code::

            >>> frame.last_read_date
            datetime.datetime(2015, 10, 8, 15, 48, 8, 791000, tzinfo=tzoffset(None, -25200))





        :returns: Date string of the last time this frame's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the frame object.

        Change or retrieve frame object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_frame.name
            "abc"

            >>> my_frame.name = "xyz"
            >>> my_frame.name
            "xyz"




        """
        return None


    @doc_stub
    def quantiles(self, column_name, quantiles):
        """
        New frame with Quantiles and their values.

        Calculate quantiles on the given column.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column *final_sale_price*:

        .. code::

            >>> my_frame.inspect()
            [#]  final_sale_price
            =====================
            [0]               100
            [1]               250
            [2]                95
            [3]               179
            [4]               315
            [5]               660
            [6]               540
            [7]               420
            [8]               250
            [9]               335

        To calculate 10th, 50th, and 100th quantile:

        .. code::

            >>> quantiles_frame = my_frame.quantiles('final_sale_price', [10, 50, 100])
            [===Job Progress===]

        A new Frame containing the requested Quantiles and their respective values
        will be returned :

        .. code::

           >>> quantiles_frame.inspect()
           [#]  Quantiles  final_sale_price_QuantileValue
           ==============================================
           [0]       10.0                            95.0
           [1]       50.0                           250.0
           [2]      100.0                           660.0


        :param column_name: The column to calculate quantiles.
        :type column_name: unicode
        :param quantiles: What is being requested.
        :type quantiles: list

        :returns: A new frame with two columns (float64): requested Quantiles and their respective values.
        :rtype: Frame
        """
        return None


    @doc_stub
    def rename_columns(self, names):
        """
        Rename columns for edge frame.

        :param names: Dictionary of old names to new names.
        :type names: dict

        :returns: 
        :rtype: _Unit
        """
        return None


    @property
    @doc_stub
    def row_count(self):
        """
        Number of rows in the current frame.

        Counts all of the rows in the frame.

        Examples
        --------
        Get the number of rows:

        .. code::

            >>> frame.row_count
            4





        :returns: The number of rows in the frame
        :rtype: int
        """
        return None


    @property
    @doc_stub
    def schema(self):
        """
        Current frame column names and types.

        The schema of the current frame is a list of column names and
        associated data types.
        It is retrieved as a list of tuples.
        Each tuple has the name and data type of one of the frame's columns.

        Examples
        --------

        .. code::

            >>> frame.schema
            [(u'name', <type 'unicode'>), (u'age', <type 'numpy.int32'>), (u'tenure', <type 'numpy.int32'>), (u'phone', <type 'unicode'>)]

        Note how the types shown are the raw, underlying types used in python.  To see the schema in a friendlier
        format, used the __repr__ presentation, invoke by simply entering the frame:
            >>> frame
            Frame "example_frame"
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode]
            status = ACTIVE  (last_read_date = -etc-)





        :returns: list of tuples of the form (<column name>, <data type>)
        :rtype: list
        """
        return None


    @doc_stub
    def sort(self, columns, ascending=True):
        """
        Sort the data in a frame.

        Sort a frame by column values either ascending or descending.

        Examples
        --------


        Consider the frame
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     1  charlie
            [2]     3  bravo
            [3]     2  echo
            [4]     4  delta
            [5]     3  alpha

        Sort a single column:

        .. code::

            >>> frame.sort('col1')
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  foxtrot
            [3]     3  bravo
            [4]     3  alpha
            [5]     4  delta

        Sort a single column descending:

        .. code::

            >>> frame.sort('col2', False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     2  echo
            [2]     4  delta
            [3]     1  charlie
            [4]     3  bravo
            [5]     3  alpha

        Sort multiple columns:

        .. code::

            >>> frame.sort(['col1', 'col2'])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  alpha
            [3]     3  bravo
            [4]     3  foxtrot
            [5]     4  delta


        Sort multiple columns descending:

        .. code::

            >>> frame.sort(['col1', 'col2'], False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  foxtrot
            [2]     3  bravo
            [3]     3  alpha
            [4]     2  echo
            [5]     1  charlie

        Sort multiple columns: 'col1' decending and 'col2' ascending:

        .. code::

            >>> frame.sort([ ('col1', False), ('col2', True) ])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  alpha
            [2]     3  bravo
            [3]     3  foxtrot
            [4]     2  echo
            [5]     1  charlie



        :param columns: Either a column name, a list of column names, or a list of tuples where each tuple is a name and an ascending bool value.
        :type columns: str | list of str | list of tuples
        :param ascending: (default=True)  True for ascending, False for descending.
        :type ascending: bool
        """
        return None


    @doc_stub
    def sorted_k(self, k, column_names_and_ascending, reduce_tree_depth=None):
        """
        Get a sorted subset of the data.

        Take a number of rows and return them
        sorted in either ascending or descending order.

        Sorting a subset of rows is more efficient than sorting the entire frame when
        the number of sorted rows is much less than the total number of rows in the frame.

        Notes
        -----
        The number of sorted rows should be much smaller than the number of rows
        in the original frame.

        In particular:

        #)  The number of sorted rows returned should fit in Spark driver memory.
            The maximum size of serialized results that can fit in the Spark driver is
            set by the Spark configuration parameter *spark.driver.maxResultSize*.
        #)  If you encounter a Kryo buffer overflow exception, increase the Spark
            configuration parameter *spark.kryoserializer.buffer.max.mb*.
        #)  Use Frame.sort() instead if the number of sorted rows is very large (in
            other words, it cannot fit in Spark driver memory).

        Examples
        --------
        These examples deal with the most recently-released movies in a private collection.
        Consider the movie collection already stored in the frame below:

            >>> my_frame.inspect()
            [#]  genre      year  title
            ========================================================
            [0]  Drama      1957  12 Angry Men
            [1]  Crime      1946  The Big Sleep
            [2]  Western    1969  Butch Cassidy and the Sundance Kid
            [3]  Drama      1971  A Clockwork Orange
            [4]  Drama      2008  The Dark Knight
            [5]  Animation  2013  Frozen
            [6]  Drama      1972  The Godfather
            [7]  Animation  1994  The Lion King
            [8]  Animation  2010  Tangled
            [9]  Fantasy    1939  The WOnderful Wizard of Oz


        This example returns the top 3 rows sorted by a single column: 'year' descending:

            >>> topk_frame = my_frame.sorted_k(3, [ ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Drama      2008  The Dark Knight

        This example returns the top 5 rows sorted by multiple columns: 'genre' ascending, then 'year' descending:

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Animation  1994  The Lion King
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      2008  The Dark Knight


        This example returns the top 5 rows sorted by multiple columns: 'genre'
        ascending, then 'year' ascending.
        It also illustrates the optional tuning parameter for reduce-tree depth
        (which does not affect the final result).

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', True) ], reduce_tree_depth=1)
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            ===================================
            [0]  Animation  1994  The Lion King
            [1]  Animation  2010  Tangled
            [2]  Animation  2013  Frozen
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      1957  12 Angry Men




        :param k: Number of sorted records to return.
        :type k: int32
        :param column_names_and_ascending: Column names to sort by, and true to sort column by ascending order,
            or false for descending order.
        :type column_names_and_ascending: list
        :param reduce_tree_depth: (default=None)  Advanced tuning parameter which determines the depth of the
            reduce-tree (uses Spark's treeReduce() for scalability.)
            Default is 2.
        :type reduce_tree_depth: int32

        :returns: A new frame with a subset of sorted rows from the original frame.
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Current frame life cycle status.

        One of three statuses: ACTIVE, DROPPED, FINALIZED
           ACTIVE:    Entity is available for use
           DROPPED:   Entity has been dropped by user or by garbage collection which found it stale
           FINALIZED: Entity's data has been deleted

        Examples
        --------

        .. code::

            >>> frame.status
            u'ACTIVE'





        :returns: Status of the frame
        :rtype: str
        """
        return None


    @doc_stub
    def take(self, n, offset=0, columns=None):
        """
        Get data subset.

        Take a subset of the currently active Frame.

        Examples
        --------
        .. code::

            >>> frame.take(2)
            [[u'Fred', 39, 16, u'555-1234'], [u'Susan', 33, 3, u'555-0202']]

            >>> frame.take(2, offset=2)
            [[u'Thurston', 65, 26, u'555-4510'], [u'Judy', 44, 14, u'555-2183']]



        :param n: The number of rows to copy to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before starting to copy
        :type offset: int
        :param columns: (default=None)  If not None, only the given columns' data will be provided.  By default, all columns are included
        :type columns: str | iterable of str

        :returns: A list of lists, where each contained list is the data for one row.
        :rtype: list
        """
        return None


    @doc_stub
    def tally(self, sample_col, count_val):
        """
        Count number of times a value is seen.

        A cumulative count is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the number of times the specified
        *count_value* has been seen.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally
            ===================
            [0]    0        0.0
            [1]    1        1.0
            [2]    2        1.0
            [3]    0        1.0
            [4]    1        2.0
            [5]    2        2.0

        :param sample_col: The name of the column from which to compute the cumulative count.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def tally_percent(self, sample_col, count_val):
        """
        Compute a cumulative percent count.

        A cumulative percent count is computed by sequentially stepping through
        the rows, observing the column values and keeping track of the percentage of the
        total number of times the specified *count_value* has been seen up to
        the current value.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally_percent("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally_percent
            ===========================
            [0]    0                0.0
            [1]    1                0.5
            [2]    2                0.5
            [3]    0                0.5
            [4]    1                1.0
            [5]    2                1.0



        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def timeseries_from_observations(self, date_time_index, timestamp_column, key_column, value_column):
        """
        Returns a frame that has the observations formatted as a time series.

        Uses the specified timestamp, key, and value columns and the date/time
                        index provided to format the observations as a time series.  The time series
                        frame will have columns for the key and a vector of the observed values that
                        correspond to the date/time index.

        Examples
        --------
        In this example, we will use a frame of observations of resting heart rate for
        three individuals over three days.  The data is accessed from Frame object
        called *my_frame*:


        .. code::

         >>> my_frame.inspect( my_frame.row_count )
         [#]  name     date                      resting_heart_rate
         ==========================================================
         [0]  Edward   2016-01-01T12:00:00.000Z                62.0
         [1]  Stanley  2016-01-01T12:00:00.000Z                57.0
         [2]  Edward   2016-01-02T12:00:00.000Z                63.0
         [3]  Sarah    2016-01-02T12:00:00.000Z                64.0
         [4]  Stanley  2016-01-02T12:00:00.000Z                57.0
         [5]  Edward   2016-01-03T12:00:00.000Z                62.0
         [6]  Sarah    2016-01-03T12:00:00.000Z                64.0
         [7]  Stanley  2016-01-03T12:00:00.000Z                56.0


        We then need to create an array that contains the date/time index,
        which will be used when creating the time series.  Since our data
        is for three days, our date/time index will just contain those
        three dates:

        .. code::

         >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z"]

        Then we can create our time series frame by specifying our date/time
        index along with the name of our timestamp column (in this example, it's
         "date"), key column (in this example, it's "name"), and value column (in
        this example, it's "resting_heart_rate").

        .. code::

         >>> ts = my_frame.timeseries_from_observations(datetimeindex, "date", "name", "resting_heart_rate")
         [===Job Progress===]

        Take a look at the resulting time series frame schema and contents:

        .. code::

         >>> ts.schema
         [(u'name', <type 'unicode'>), (u'resting_heart_rate', vector(3))]

         >>> ts.inspect()
         [#]  name     resting_heart_rate
         ================================
         [0]  Stanley  [57.0, 57.0, 56.0]
         [1]  Edward   [62.0, 63.0, 62.0]
         [2]  Sarah    [None, 64.0, 64.0]



        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param timestamp_column: The name of the column telling when the observation occurred.
        :type timestamp_column: unicode
        :param key_column: The name of the column that contains which string key the observation belongs to.
        :type key_column: unicode
        :param value_column: The name of the column that contains the observed value.
        :type value_column: unicode

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def timeseries_slice(self, date_time_index, start, end):
        """
        Returns a frame that is a sub-slice of the given series.

        Splits a time series frame on the specified start and end date/times.

        Examples
        --------
        For this example, we start with a frame that has already been formatted as a time series.
        This means that the frame has a string column for key and a vector column that contains
        a series of the observed values.  We must also know the date/time index that corresponds
        to the time series.

        The time series is in a Frame object called *ts_frame*.


        .. code::

            >>> ts_frame.inspect()
            [#]  key  series
            ==============================================
            [0]  A    [62.0, 55.0, 60.0, 61.0, 60.0, 59.0]
            [1]  B    [60.0, 58.0, 61.0, 62.0, 60.0, 61.0]
            [2]  C    [69.0, 68.0, 68.0, 70.0, 71.0, 69.0]

        Next, we define the date/time index.  In this example, it is one day intervals from
        2016-01-01 to 2016-01-06:

        .. code::

            >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z","2016-01-04T12:00:00.000Z","2016-01-05T12:00:00.000Z","2016-01-06T12:00:00.000Z"]

        Get a slice of our time series from 2016-01-02 to 2016-01-04:

        .. code::
            >>> slice_start = "2016-01-02T12:00:00.000Z"
            >>> slice_end = "2016-01-04T12:00:00.000Z"

            >>> sliced_frame = ts_frame.timeseries_slice(datetimeindex, slice_start, slice_end)
            [===Job Progress===]

        Take a look at our sliced time series:

        .. code::

            >>> sliced_frame.inspect()
            [#]  key  series
            ============================
            [0]  A    [55.0, 60.0, 61.0]
            [1]  B    [58.0, 61.0, 62.0]
            [2]  C    [68.0, 68.0, 70.0]


        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param start: The start date for the slice in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ 
        :type start: datetime
        :param end: The end date for the slice (inclusive) in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ.
        :type end: datetime

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def top_k(self, column_name, k, weights_column=None):
        """
        Most or least frequent column values.

        Calculate the top (or bottom) K distinct values by count of a column.
        The column can be weighted.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight > 0, then topK is empty.

        Examples
        --------
        For this example, we calculate the top 5 movie genres in a data frame:
        Consider the following frame containing four columns.

        >>> frame.inspect()
            [#]  rank  city         population_2013  population_2010  change  county
            ============================================================================
            [0]     1  Portland              609456           583776  4.40%   Multnomah
            [1]     2  Salem                 160614           154637  3.87%   Marion
            [2]     3  Eugene                159190           156185  1.92%   Lane
            [3]     4  Gresham               109397           105594  3.60%   Multnomah
            [4]     5  Hillsboro              97368            91611  6.28%   Washington
            [5]     6  Beaverton              93542            89803  4.16%   Washington
            [6]    15  Grants Pass            35076            34533  1.57%   Josephine
            [7]    16  Oregon City            34622            31859  8.67%   Clackamas
            [8]    17  McMinnville            33131            32187  2.93%   Yamhill
            [9]    18  Redmond                27427            26215  4.62%   Deschutes
        >>> top_frame = frame.top_k("county", 2)
        [===Job Progress===]
        >>> top_frame.inspect()
            [#]  county      count
                ======================
                [0]  Washington    4.0
                [1]  Clackamas     3.0

















        :param column_name: The column whose top (or bottom) K distinct values are
            to be calculated.
        :type column_name: unicode
        :param k: Number of entries to return (If k is negative, return bottom k).
        :type k: int32
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the topK calculation.
            Must contain numerical data.
            Default is 1 for all items.
        :type weights_column: unicode

        :returns: An object with access to the frame of data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def unflatten_columns(self, columns, delimiter=None):
        """
        Compacts data from multiple rows based on cell data.

        Groups together cells in all columns (less the composite key) using "," as string delimiter.
        The original rows are deleted.
        The grouping takes place based on a composite key created from cell values.
        The column datatypes are changed to string.

        Examples
        --------
        Given a data file::

            user1 1/1/2015 1 70
            user1 1/1/2015 2 60
            user2 1/1/2015 1 65

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("unflatten_column.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c  d
            ===========================
            [0]  user1  1/1/2015  1  70
            [1]  user1  1/1/2015  2  60
            [2]  user2  1/1/2015  1  65


        Unflatten the data using columns a & b:

        .. code::

            >>> frame.unflatten_columns(['a','b'])
            [===Job Progress===]

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c    d
            ================================
            [0]  user2  1/1/2015  1    65
            [1]  user1  1/1/2015  1,2  70,60

        Alternatively, unflatten_columns() also accepts a single column like:


        .. code::

            >>> frame.unflatten_columns('a')
            [===Job Progress===]

            >>> frame.inspect()
            [#]  a      b                  c    d
            =========================================
            [0]  user1  1/1/2015,1/1/2015  1,2  70,60
            [1]  user2  1/1/2015           1    65


        :param columns: Name of the column(s) to be used as keys
            for unflattening.
        :type columns: list
        :param delimiter: (default=None)  Separator for the data in the result columns.
            Default is comma (,).
        :type delimiter: unicode

        :returns: 
        :rtype: _Unit
        """
        return None



@doc_stub
class _DocStubsFrame(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, source=None, name=None):
        """
            Create a Frame/frame.

        Notes
        -----
        A frame with no name is subject to garbage collection.

        If a string in the CSV file starts and ends with a double-quote (")
        character, the character is stripped off of the data before it is put into
        the field.
        Anything, including delimiters, between the double-quote characters is
        considered part of the str.
        If the first character after the delimiter is anything other than a
        double-quote character, the string will be composed of all the characters
        between the delimiters, including double-quotes.
        If the first field type is str, leading spaces on each row are
        considered part of the str.
        If the last field type is str, trailing spaces on each row are
        considered part of the str.

        Examples
        --------
        Create a new frame based upon the data described in the CsvFile object
        *my_csv_schema*.
        Name the frame "myframe".
        Create a Frame *my_frame* to access the data:

        .. code::

            >>> my_frame = ta.Frame(my_csv_schema, "myframe")

        A Frame object has been created and *my_frame* is its proxy.
        It brought in the data described by *my_csv_schema*.
        It is named *myframe*.

        Create an empty frame; name it "yourframe":

        .. code::

            >>> your_frame = ta.Frame(name='yourframe')

        A frame has been created and Frame *your_frame* is its proxy.
        It has no data yet, but it does have the name *yourframe*.



        :param source: (default=None)  A source of initial data.
        :type source: CsvFile | Frame
        :param name: (default=None)  The name of the newly created frame.
            Default is None.
        :type name: str
        """
        raise DocStubCalledError("frame:/__init__")


    @doc_stub
    def add_columns(self, func, schema, columns_accessed=None):
        """
        Add columns to current frame.

        Assigns data to column based on evaluating a function for each row.

        Notes
        -----
        1)  The row |UDF| ('func') must return a value in the same format as
            specified by the schema.
            See :doc:`/ds_apir`.
        2)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!

        Examples
        --------
        Given our frame, let's add a column which has how many years the person has been over 18

        .. code::


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183

            >>> frame.add_columns(lambda row: row.age - 18, ('adult_years', ta.int32))
            [===Job Progress===]

            >>> frame.inspect()
            [#]  name      age  tenure  phone     adult_years
            =================================================
            [0]  Fred       39      16  555-1234           21
            [1]  Susan      33       3  555-0202           15
            [2]  Thurston   65      26  555-4510           47
            [3]  Judy       44      14  555-2183           26


        Multiple columns can be added at the same time.  Let's add percentage of
        life and percentage of adult life in one call, which is more efficient.

        .. code::

            >>> frame.add_columns(lambda row: [row.tenure / float(row.age), row.tenure / float(row.adult_years)], [("of_age", ta.float32), ("of_adult", ta.float32)])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54

        Note that the function returns a list, and therefore the schema also needs to be a list.

        It is not necessary to use lambda syntax, any function will do, as long as it takes a single row argument.  We
        can also call other local functions within.

        Let's add a column which shows the amount of person's name based on their adult tenure percentage.

            >>> def percentage_of_string(string, percentage):
            ...     '''returns a substring of the given string according to the given percentage'''
            ...     substring_len = int(percentage * len(string))
            ...     return string[:substring_len]

            >>> def add_name_by_adult_tenure(row):
            ...     return percentage_of_string(row.name, row.of_adult)

            >>> frame.add_columns(add_name_by_adult_tenure, ('tenured_name', unicode))
            [===Job Progress===]

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame.inspect(columns=['name', 'of_adult', 'tenured_name'], round=2)
            [#]  name      of_adult  tenured_name
            =====================================
            [0]  Fred          0.76  Fre
            [1]  Susan         0.20  S
            [2]  Thurston      0.55  Thur
            [3]  Judy          0.54  Ju


        **Optimization** - If we know up front which columns our row function will access, we
        can tell add_columns to speed up the execution by working on only the limited feature
        set rather than the entire row.

        Let's add a name based on tenure percentage of age.  We know we're only going to use
        columns 'name' and 'of_age'.

        .. code::

            >>> frame.add_columns(lambda row: percentage_of_string(row.name, row.of_age),
            ...                   ('tenured_name_age', unicode),
            ...                   columns_accessed=['name', 'of_age'])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54
            <BLANKLINE>
            [#]  tenured_name  tenured_name_age
            ===================================
            [0]  Fre           F
            [1]  S
            [2]  Thur          Thu
            [3]  Ju            J

        More information on a row |UDF| can be found at :doc:`/ds_apir`



        :param func: User-Defined Function (|UDF|) which takes the values in the row and produces a value, or collection of values, for the new cell(s).
        :type func: UDF
        :param schema: The schema for the results of the |UDF|, indicating the new column(s) to add.  Each tuple provides the column name and data type, and is of the form (str, type).
        :type schema: tuple | list of tuples
        :param columns_accessed: (default=None)  List of columns which the |UDF| will access.  This adds significant performance benefit if we know which column(s) will be needed to execute the |UDF|, especially when the frame has significantly more columns than those being used to evaluate the |UDF|.
        :type columns_accessed: list
        """
        return None


    @doc_stub
    def append(self, data):
        """
        Adds more data to the current frame.

        Examples
        --------

        .. code::

            >>> animals = ta.Frame(ta.UploadRows([['dog', 'snoopy'],
            ...                                    ['cat', 'tom'],
            ...                                    ['bear', 'yogi'],
            ...                                    ['mouse', 'jerry']],
            ...                                    [('animal', str), ('name', str)]))
            [===Job Progress===]
            >>> animals.append(ta.UploadRows([['donkey'],
            ...                                ['elephant'],
            ...                                ['ostrich']],
            ...                                [('animal', str)]))
            [===Job Progress===]

            >>> animals.inspect()
            [#]  animal    name
            =====================
            [0]  dog       snoopy
            [1]  cat       tom
            [2]  bear      yogi
            [3]  mouse     jerry
            [4]  donkey    None
            [5]  elephant  None
            [6]  ostrich   None


        The data we added didn't have names, so None values were inserted for the new rows.


        :param data: Data source, see :doc:`Data Sources </python_api/datasources/index>`
        :type data: Data source
        """
        return None


    @doc_stub
    def assign_sample(self, sample_percentages, sample_labels=None, output_column=None, random_seed=None):
        """
        Randomly group rows into user-defined classes.

        Randomly assign classes to rows given a vector of percentages.
        The table receives an additional column that contains a random label.
        The random label is generated by a probability distribution function.
        The distribution function is specified by the sample_percentages, a list of
        floating point values, which add up to 1.
        The labels are non-negative integers drawn from the range
        :math:`[ 0, len(S) - 1]` where :math:`S` is the sample_percentages.

        **Notes**

        The sample percentages provided by the user are preserved to at least eight
        decimal places, but beyond this there may be small changes due to floating
        point imprecision.

        In particular:

        #)  The engine validates that the sum of probabilities sums to 1.0 within
            eight decimal places and returns an error if the sum falls outside of this
            range.
        #)  The probability of the final class is clamped so that each row receives a
            valid label with probability one.


        Consider this simple frame.

        >>> frame.inspect()
        [#]  blip  id
        =============
        [0]  abc    0
        [1]  def    1
        [2]  ghi    2
        [3]  jkl    3
        [4]  mno    4
        [5]  pqr    5
        [6]  stu    6
        [7]  vwx    7
        [8]  yza    8
        [9]  bcd    9

        We'll assign labels to each row according to a rough 40-30-30 split, for
        "train", "test", and "validate".

        >>> frame.assign_sample([0.4, 0.3, 0.3])
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin
        =========================
        [0]  abc    0  VA
        [1]  def    1  TR
        [2]  ghi    2  TE
        [3]  jkl    3  TE
        [4]  mno    4  TE
        [5]  pqr    5  TR
        [6]  stu    6  TR
        [7]  vwx    7  VA
        [8]  yza    8  VA
        [9]  bcd    9  VA


        Now the frame  has a new column named "sample_bin" with a string label.
        Values in the other columns are unaffected.

        Here it is again, this time specifying labels, output column and random seed

        >>> frame.assign_sample([0.2, 0.2, 0.3, 0.3],
        ...                     ["cat1", "cat2", "cat3", "cat4"],
        ...                     output_column="cat",
        ...                     random_seed=12)
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin  cat
        ===============================
        [0]  abc    0  VA          cat4
        [1]  def    1  TR          cat2
        [2]  ghi    2  TE          cat3
        [3]  jkl    3  TE          cat4
        [4]  mno    4  TE          cat1
        [5]  pqr    5  TR          cat3
        [6]  stu    6  TR          cat2
        [7]  vwx    7  VA          cat3
        [8]  yza    8  VA          cat3
        [9]  bcd    9  VA          cat4



        :param sample_percentages: Entries are non-negative and sum to 1. (See the note below.)
            If the *i*'th entry of the  list is *p*,
            then then each row receives label *i* with independent probability *p*.
        :type sample_percentages: list
        :param sample_labels: (default=None)  Names to be used for the split classes.
            Defaults to "TR", "TE", "VA" when the length of *sample_percentages* is 3,
            and defaults to Sample_0, Sample_1, ... otherwise.
        :type sample_labels: list
        :param output_column: (default=None)  Name of the new column which holds the labels generated by the
            function.
        :type output_column: unicode
        :param random_seed: (default=None)  Random seed used to generate the labels.
            Defaults to 0.
        :type random_seed: int32

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column(self, column_name, cutoffs, include_lowest=None, strict_binning=None, bin_column_name=None):
        """
        Classify data into user-defined groups.

        Summarize rows of data based on the value in a single column by sorting them
        into bins, or groups, based on a list of bin cutoff points.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  Bins IDs are 0-index, in other words, the lowest bin number is 0.
        #)  The first and last cutoffs are always included in the bins.
            When *include_lowest* is ``True``, the last bin includes both cutoffs.
            When *include_lowest* is ``False``, the first bin (bin 0) includes both
            cutoffs.

        Examples
        --------
        For these examples, we will use a frame with column *a* accessed by a Frame
        object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame with a column showing what bin the data is in.
        The data values should use strict_binning:

        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1      -1
        [1]    1      -1
        [2]    2      -1
        [3]    3      -1
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89      -1

        Modify the frame with a column showing what bin the data is in.
        The data value should not use strict_binning:


        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89       2

        Modify the frame with a column showing what bin the data is in.
        The bins should be lower inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       1
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       3
        [10]  89       3

        Modify the frame with a column showing what bin the data is in.
        The bins should be upper inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=False,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       1
        [9]   55       2
        [10]  89       3



        :param column_name: Name of the column to bin.
        :type column_name: unicode
        :param cutoffs: Array of values containing bin cutoff points.
            Array can be list or tuple.
            Array values must be progressively increasing.
            All bin boundaries must be included, so, with N bins, you need N+1 values.
        :type cutoffs: list
        :param include_lowest: (default=None)  Specify how the boundary conditions are handled.
            ``True`` indicates that the lower bound of the bin is inclusive.
            ``False`` indicates that the upper bound is inclusive.
            Default is ``True``.
        :type include_lowest: bool
        :param strict_binning: (default=None)  Specify how values outside of the cutoffs array should be binned.
            If set to ``True``, each value less than cutoffs[0] or greater than
            cutoffs[-1] will be assigned a bin value of -1.
            If set to ``False``, values less than cutoffs[0] will be included in the first
            bin while values greater than cutoffs[-1] will be included in the final
            bin.
        :type strict_binning: bool
        :param bin_column_name: (default=None)  The name for the new binned column.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column_equal_depth(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into groups with the same frequency.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal depth binning attempts to label rows such that each bin contains the
        same number of elements.
        For :math:`n` bins of a column :math:`C` of length :math:`m`, the bin
        number is determined by:

        .. math::

            \lceil n * \frac { f(C) }{ m } \rceil

        where :math:`f` is a tie-adjusted ranking function over values of
        :math:`C`.
        If there are multiples of the same value in :math:`C`, then their
        tie-adjusted rank is the average of their ordered rank values.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has a quantity of :math"`X`
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89


        Modify the frame, adding a column showing what bin the data is in.
        The data should be grouped into a maximum of five bins.
        Note that each bin will have the same quantity of members (as much as
        possible):

        >>> cutoffs = my_frame.bin_column_equal_depth('a', 5, 'aEDBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEDBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          1
        [3]    3          1
        [4]    5          2
        [5]    8          2
        [6]   13          3
        [7]   21          3
        [8]   34          4
        [9]   55          4
        [10]  89          4

        >>> print cutoffs
        [1.0, 2.0, 5.0, 13.0, 34.0, 89.0]


        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list containing the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def bin_column_equal_width(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into same-width groups.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal width binning places column values into groups such that the values
        in each group fall within the same interval and the interval width for each
        group is equal.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has 10
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the number of actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame, adding a column showing what bin the data is in.
        The data should be separated into a maximum of five bins and the bin cutoffs
        should be evenly spaced.
        Note that there may be bins with no members:

        >>> cutoffs = my_frame.bin_column_equal_width('a', 5, 'aEWBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEWBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          0
        [3]    3          0
        [4]    5          0
        [5]    8          0
        [6]   13          0
        [7]   21          1
        [8]   34          1
        [9]   55          3
        [10]  89          4

        The method returns a list of 6 cutoff values that define the edges of each bin.
        Note that difference between the cutoff values is constant:

        >>> print cutoffs
        [1.0, 18.6, 36.2, 53.8, 71.4, 89.0]



        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list of the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def categorical_summary(self, *column_inputs):
        """
        Compute a summary of the data in a column(s) for categorical or numerical data types.

        The returned value is a Map containing categorical summary for each specified column.

        For each column, levels which satisfy the top k and/or threshold cutoffs are displayed along
        with their frequency and percentage occurrence with respect to the total rows in the dataset.

        Missing data is reported when a column value is empty ("") or null.

        All remaining data is grouped together in the Other category and its frequency and percentage are reported as well.

        User must specify the column name and can optionally specify top_k and/or threshold.

        Optional parameters:

            top_k
                Displays levels which are in the top k most frequently occurring values for that column.

            threshold
                Displays levels which are above the threshold percentage with respect to the total row count.

            top_k and threshold
                Performs level pruning first based on top k and then filters out levels which satisfy the threshold criterion.

            defaults
                Displays all levels which are in Top 10.


        Examples
        --------


        .. code::

            >>> frame.categorical_summary('source','target')
            >>> frame.categorical_summary(('source', {'top_k' : 2}))
            >>> frame.categorical_summary(('source', {'threshold' : 0.5}))
            >>> frame.categorical_summary(('source', {'top_k' : 2}), ('target',
            ... {'threshold' : 0.5}))

        Sample output (for last example above):

            >>> {u'categorical_summary': [{u'column': u'source', u'levels': [
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'thing'},
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'abstraction'},
            ... {u'percentage': 0.25, u'frequency': 7, u'level': u'physical_entity'},
            ... {u'percentage': 0.10714285714285714, u'frequency': 3, u'level': u'entity'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Other'}]},
            ... {u'column': u'target', u'levels': [
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'thing'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2,
            ...  u'level': u'physical_entity'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'entity'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'variable'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'unit'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'substance'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'subject'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'set'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'reservoir'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'relation'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.5357142857142857, u'frequency': 15, u'level': u'Other'}]}]}



        :param *column_inputs: (default=None)  Comma-separated column names to summarize or tuple containing column name and dictionary of optional parameters. Optional parameters (see below for details): top_k (default = 10), threshold (default = 0.0)
        :type *column_inputs: str | tuple(str, dict)

        :returns: Summary for specified column(s) consisting of levels with their frequency and percentage
        :rtype: dict
        """
        return None


    @doc_stub
    def classification_metrics(self, label_column, pred_column, pos_label=None, beta=None, frequency_column=None):
        """
        Model statistics of accuracy, precision, and others.

        Calculate the accuracy, precision, confusion_matrix, recall and
        :math:`F_{ \beta}` measure for a classification model.

        *   The **f_measure** result is the :math:`F_{ \beta}` measure for a
            classification model.
            The :math:`F_{ \beta}` measure of a binary classification model is the
            harmonic mean of precision and recall.
            If we let:

            * beta :math:`\equiv \beta`,
            * :math:`T_{P}` denotes the number of true positives,
            * :math:`F_{P}` denotes the number of false positives, and
            * :math:`F_{N}` denotes the number of false negatives

            then:

            .. math::

                F_{ \beta} = (1 + \beta ^ 2) * \frac{ \frac{T_{P}}{T_{P} + F_{P}} * \
                \frac{T_{P}}{T_{P} + F_{N}}}{ \beta ^ 2 * \frac{T_{P}}{T_{P} + \
                F_{P}}  + \frac{T_{P}}{T_{P} + F_{N}}}

            The :math:`F_{ \beta}` measure for a multi-class classification model is
            computed as the weighted average of the :math:`F_{ \beta}` measure for
            each label, where the weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **recall** result of a binary classification model is the proportion
            of positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{N}` denote the number of false negatives, then the model
            recall is given by :math:`\frac {T_{P}} {T_{P} + F_{N}}`.

            For multi-class classification models, the recall measure is computed as
            the weighted average of the recall for each label, where the weight is
            the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **precision** of a binary classification model is the proportion of
            predicted positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{P}` denote the number of false positives, then the model
            precision is given by: :math:`\frac {T_{P}} {T_{P} + F_{P}}`.

            For multi-class classification models, the precision measure is computed
            as the weighted average of the precision for each label, where the
            weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **accuracy** of a classification model is the proportion of
            predictions that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives,
            :math:`T_{N}` denote the number of true negatives, and :math:`K` denote
            the total number of classified instances, then the model accuracy is
            given by: :math:`\frac{T_{P} + T_{N}}{K}`.

            This measure applies to binary and multi-class classifiers.

        *   The **confusion_matrix** result is a confusion matrix for a
            binary classifier model, formatted for human readability.

        Notes
        -----
        The **confusion_matrix** is not yet implemented for multi-class classifiers.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  a      b  labels  predictions
            ==================================
            [0]  red    1       0            0
            [1]  blue   3       1            0
            [2]  green  1       0            0
            [3]  green  0       1            1


            >>> cm = my_frame.classification_metrics('labels', 'predictions', 1, 1)
            [===Job Progress===]

            >>> cm.f_measure
            0.6666666666666666

            >>> cm.recall
            0.5

            >>> cm.accuracy
            0.75

            >>> cm.precision
            1.0

            >>> cm.confusion_matrix
                        Predicted_Pos  Predicted_Neg
            Actual_Pos              1              1
            Actual_Neg              0              2





        :param label_column: The name of the column containing the
            correct label for each instance.
        :type label_column: unicode
        :param pred_column: The name of the column containing the
            predicted label for each instance.
        :type pred_column: unicode
        :param pos_label: (default=None)  
        :type pos_label: None
        :param beta: (default=None)  This is the beta value to use for
            :math:`F_{ \beta}` measure (default F1 measure is computed); must be greater than zero.
            Defaults is 1.
        :type beta: float64
        :param frequency_column: (default=None)  The name of an optional column containing the
            frequency of observations.
        :type frequency_column: unicode

        :returns: The data returned is composed of multiple components\:

            |   <object>.accuracy : double
            |   <object>.confusion_matrix : table
            |   <object>.f_measure : double
            |   <object>.precision : double
            |   <object>.recall : double
        :rtype: dict
        """
        return None


    @doc_stub
    def column_median(self, data_column, weights_column=None):
        """
        Calculate the (weighted) median of a column.

        The median is the least value X in the range of the distribution so that
        the cumulative weight of values strictly below X is strictly less than half
        of the total weight and the cumulative weight of values up to and including X
        is greater than or equal to one-half of the total weight.

        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If a weight column is provided and no weights are finite numbers greater
        than 0, None is returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return middle number of values in column *a*:

        .. code::

           >>> median = my_frame.column_median('a')
           [===Job Progress===]
           >>> print median
           5

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return middle number of values in column 'a' with weights 'w':

        .. code::

           >>> median = my_frame.column_median('a', weights_column='w')
           [===Job Progress===]
           >>> print median
           3


        :param data_column: The column whose median is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies)
            for the median calculation.
            Must contain numerical data.
            Default is all items have a weight of 1.
        :type weights_column: unicode

        :returns: varies
                The median of the values.
                If a weight column is provided and no weights are finite numbers greater
                than 0, None is returned.
                The type of the median returned is the same as the contents of the data
                column, so a column of Longs will result in a Long median and a column of
                Floats will result in a Float median.
        :rtype: None
        """
        return None


    @doc_stub
    def column_mode(self, data_column, weights_column=None, max_modes_returned=None):
        """
        Evaluate the weights assigned to rows.

        Calculate the modes of a column.
        A mode is a data element of maximum weight.
        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight greater than 0,
        no mode is returned.

        Because data distributions often have multiple modes, it is possible for a
        set of modes to be returned.
        By default, only one is returned, but by setting the optional parameter
        max_modes_returned, a larger number of modes can be returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30
           

        Compute and return a dictionary containing summary statistics of column *a*:

        .. code::

           >>> mode = my_frame.column_mode('a')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 1), (u'modes', [3]), (u'total_weight', 7.0), (u'weight_of_mode', 2.0)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149
           

        Compute and return dictionary containing summary statistics of column 'a' with weights 'w':

        .. code::

           >>> mode = my_frame.column_mode('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 2), (u'modes', [2]), (u'total_weight', 6.200000144541264), (u'weight_of_mode', 1.7000000476837158)]



        :param data_column: Name of the column supplying the data.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of the column supplying the weights.
            Default is all items have weight of 1.
        :type weights_column: unicode
        :param max_modes_returned: (default=None)  Maximum number of modes returned.
            Default is 1.
        :type max_modes_returned: int32

        :returns: Dictionary containing summary statistics.
                The data returned is composed of multiple components\:

            mode : A mode is a data element of maximum net weight.
                A set of modes is returned.
                The empty set is returned when the sum of the weights is 0.
                If the number of modes is less than or equal to the parameter
                max_modes_returned, then all modes of the data are
                returned.
                If the number of modes is greater than the max_modes_returned
                parameter, only the first max_modes_returned many modes (per a
                canonical ordering) are returned.
            weight_of_mode : Weight of a mode.
                If there are no data elements of finite weight greater than 0,
                the weight of the mode is 0.
                If no weights column is given, this is the number of appearances
                of each mode.
            total_weight : Sum of all weights in the weight column.
                This is the row count if no weights are given.
                If no weights column is given, this is the number of rows in
                the table with non-zero weight.
            mode_count : The number of distinct modes in the data.
                In the case that the data is very multimodal, this number may
                exceed max_modes_returned.


        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def column_names(self):
        """
        Column identifications in the current frame.

        Returns the names of the columns of the current frame.

        Examples
        --------

        .. code::


            >>> frame.column_names
            [u'name', u'age', u'tenure', u'phone']





        :returns: list of names of all the frame's columns
        :rtype: list
        """
        return None


    @doc_stub
    def column_summary_statistics(self, data_column, weights_column=None, use_population_variance=None):
        """
        Calculate multiple statistics for a column.

        Notes
        -----
        Sample Variance
            Sample Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W - 1} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Population Variance
            Population Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Standard Deviation
            The square root of the variance.

        Logging Invalid Data
            A row is bad when it contains a NaN or infinite value in either
            its data or weights column.
            In this case, it contributes to bad_row_count; otherwise it
            contributes to good row count.

            A good row can be skipped because the value in its weight
            column is less than or equal to 0.
            In this case, it contributes to non_positive_weight_count, otherwise
            (when the weight is greater than 0) it contributes to
            valid_data_weight_pair_count.

        **Equations**

            .. code::

                bad_row_count + good_row_count = # rows in the frame
                positive_weight_count + non_positive_weight_count = good_row_count

            In particular, when no weights column is provided and all weights are 1.0:

            .. code::

                non_positive_weight_count = 0 and
                positive_weight_count = good_row_count

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return summary statistics for values in column *a*:

        .. code::

           >>> summary_statistics = my_frame.column_summary_statistics('a')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 5.6725751451901045), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 8.571428571428571), (u'mean_confidence_lower', 1.277083729932067), (u'mean_confidence_upper', 15.865773412925076), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 9.846440014156434), (u'total_weight', 7.0), (u'variance', 96.95238095238095)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return summary statistics values in column 'a' with weights 'w':

        .. code::
           >>> summary_statistics = my_frame.column_summary_statistics('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 4.039682869616821), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 5.032258048622591), (u'mean_confidence_lower', 1.4284724667085964), (u'mean_confidence_upper', 8.636043630536586), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 4.578241754132706), (u'total_weight', 6.200000144541264), (u'variance', 20.96029755928412)]


        :param data_column: The column to be statistically summarized.
            Must contain numerical data; all NaNs and infinite values are excluded
            from the calculation.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of column holding weights of
            column values.
        :type weights_column: unicode
        :param use_population_variance: (default=None)  If true, the variance is calculated
            as the population variance.
            If false, the variance calculated as the sample variance.
            Because this option affects the variance, it affects the standard
            deviation and the confidence intervals as well.
            Default is false.
        :type use_population_variance: bool

        :returns: Dictionary containing summary statistics.
            The data returned is composed of multiple components\:

            |   mean : [ double | None ]
            |       Arithmetic mean of the data.
            |   geometric_mean : [ double | None ]
            |       Geometric mean of the data. None when there is a data element <= 0, 1.0 when there are no data elements.
            |   variance : [ double | None ]
            |       None when there are <= 1 many data elements. Sample variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight minus 1. None when the sum of the weights is <= 1. Population variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight.
            |   standard_deviation : [ double | None ]
            |       The square root of the variance. None when  sample variance is being used and the sum of weights is <= 1.
            |   total_weight : long
            |       The count of all data elements that are finite numbers. In other words, after excluding NaNs and infinite values.
            |   minimum : [ double | None ]
            |       Minimum value in the data. None when there are no data elements.
            |   maximum : [ double | None ]
            |       Maximum value in the data. None when there are no data elements.
            |   mean_confidence_lower : [ double | None ]
            |       Lower limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   mean_confidence_upper : [ double | None ]
            |       Upper limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   bad_row_count : [ double | None ]
            |       The number of rows containing a NaN or infinite value in either the data or weights column.
            |   good_row_count : [ double | None ]
            |       The number of rows not containing a NaN or infinite value in either the data or weights column.
            |   positive_weight_count : [ double | None ]
            |       The number of valid data elements with weight > 0. This is the number of entries used in the statistical calculation.
            |   non_positive_weight_count : [ double | None ]
            |       The number valid data elements with finite weight <= 0.
        :rtype: dict
        """
        return None


    @doc_stub
    def copy(self, columns=None, where=None, name=None):
        """
        Create new frame from current frame.

        Copy frame or certain frame columns entirely or filtered.
        Useful for frame query.

        Examples
        --------

        .. code::

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode, tenured_name_age:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame2 = frame.copy()  # full copy of the frame
            [===Job Progress===]

            >>> frame3 = frame.copy(['name', 'age'])  # copy only two columns
            [===Job Progress===]
            >>> frame3
            Frame  <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32]
            status = ACTIVE  (last_read_date = -etc-)

        .. code::

            >>> frame4 = frame.copy({'name': 'name', 'age': 'age', 'tenure': 'years'},
            ...                     where=lambda row: row.age > 40)
            [===Job Progress===]
            >>> frame4.inspect()
            [#]  name      age  years
            =========================
            [0]  Thurston   65     26
            [1]  Judy       44     14



        :param columns: (default=None)  If not None, the copy will only include the columns specified. If dict, the string pairs represent a column renaming, {source_column_name: destination_column_name}
        :type columns: str | list of str | dict
        :param where: (default=None)  If not None, only those rows for which the UDF evaluates to True will be copied.
        :type where: function
        :param name: (default=None)  Name of the copied frame
        :type name: str

        :returns: A new Frame of the copied data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def correlation(self, data_column_names):
        """
        Calculate correlation for two columns of current frame.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation computes the common correlation coefficient (Pearson's) on the pair
        of columns provided.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051 .


            >>> my_frame.correlation(["x1", "x2"])
            [===Job Progress===]

                -1.0
            >>> my_frame.correlation(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.correlation(["x2", "x3"])
            [===Job Progress===]

                -0.948683298051




        :param data_column_names: The names of 2 columns from which
            to compute the correlation.
        :type data_column_names: list

        :returns: Pearson correlation coefficient of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def correlation_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate correlation matrix for two or more columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation_matrix computes the common correlation coefficient (Pearson's) on each pair
        of columns in the user-provided list.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051

            >>> corr_matrix = my_frame.correlation_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> corr_matrix.inspect()
            [#]  idnum           x1              x2               x3               x4
            ==========================================================================
            [0]             1.0             1.0             -1.0   0.948683298051  0.0
            [1]             1.0             1.0             -1.0   0.948683298051  0.0
            [2]            -1.0            -1.0              1.0  -0.948683298051  0.0
            [3]  0.948683298051  0.948683298051  -0.948683298051              1.0  0.0
            [4]             0.0             0.0              0.0              0.0  1.0





        :param data_column_names: The names of the columns from
            which to compute the matrix.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name for the returned
            matrix Frame.
        :type matrix_name: unicode

        :returns: A Frame with the matrix of the correlation values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def count(self, where):
        """
        Counts the number of rows which meet given criteria.

        Examples
        --------


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.count(lambda row: row.age > 35)
            [===Job Progress===]
            3



        :param where: |UDF| which evaluates a row to a boolean
        :type where: function

        :returns: number of rows for which the where |UDF| evaluated to True.
        :rtype: int
        """
        return None


    @doc_stub
    def covariance(self, data_column_names):
        """
        Calculate covariance for exactly two columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance computes the covariance on the pair of columns provided.

            >>> my_frame.covariance(["x1", "x2"])
            [===Job Progress===]

                -2.5
            >>> my_frame.covariance(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.covariance(["x2", "x3"])
            [===Job Progress===]

                -1.5




        :param data_column_names: The names of two columns from which
            to compute the covariance.
        :type data_column_names: list

        :returns: Covariance of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def cumulative_percent(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative percent sum is computed by sequentially stepping through the
        rows, observing the column values and keeping track of the current percentage of the total sum
        accounted for at the current value.


        Notes
        -----
        This method applies only to columns containing numerical data.
        Although this method will execute for columns containing negative
        values, the interpretation of the result will change (for example,
        negative percentages).

        Examples
        --------
        Consider Frame *my_frame* accessing a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent sum for column *obs* is obtained by:

            >>> my_frame.cumulative_percent('obs')
            [===Job Progress===]

        The Frame *my_frame* now contains two columns *obs* and
        *obsCumulativePercentSum*.
        They contain the original data and the cumulative percent sum,
        respectively:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_percent
            ================================
            [0]    0                     0.0
            [1]    1          0.166666666667
            [2]    2                     0.5
            [3]    0                     0.5
            [4]    1          0.666666666667
            [5]    2                     1.0


        :param sample_col: The name of the column from which to compute
            the cumulative percent sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def cumulative_sum(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative sum is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the cumulative sum for each value.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative sum for column *obs* is obtained by:

            >>> my_frame.cumulative_sum('obs')
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativeSum* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_sum
            ============================
            [0]    0                 0.0
            [1]    1                 1.0
            [2]    2                 3.0
            [3]    0                 3.0
            [4]    1                 4.0
            [5]    2                 6.0

        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def daal_covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Uses Intel Data Analytics and Acceleration Library (DAAL) to compute covariance matrix.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.daal_covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.daal_covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def dot_product(self, left_column_names, right_column_names, dot_product_column_name, default_left_values=None, default_right_values=None):
        """
        Calculate dot product for each row in current frame.

        Calculate the dot product for each row in a frame using values from two
        equal-length sequences of columns.

        Dot product is computed by the following formula:

        The dot product of two vectors :math:`A=[a_1, a_2, ..., a_n]` and
        :math:`B =[b_1, b_2, ..., b_n]` is :math:`a_1*b_1 + a_2*b_2 + ...+ a_n*b_n`.
        The dot product for each row is stored in a new column in the existing frame.

        Notes
        -----
        If default_left_values or default_right_values are not specified, any null
        values will be replaced by zeros.

        Examples
        --------
        Calculate the dot product for a sequence of columns in Frame object *my_frame*:

        .. code::

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3
            ===============================
            [0]      1    0.2     -2      5
            [1]      2    0.4     -1      6
            [2]      3    0.6      0      7
            [3]      4    0.8      1      8


        Modify the frame by computing the dot product for a sequence of columns:

        .. code::

             >>> my_frame.dot_product(['col_0','col_1'], ['col_2', 'col_3'], 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3  dot_product
            ============================================
            [0]      1    0.2     -2      5         -1.0
            [1]      2    0.4     -1      6          0.4
            [2]      3    0.6      0      7          4.2
            [3]      4    0.8      1      8         10.4


        Calculate the dot product for columns of vectors in Frame object *my_frame*:


        .. code::
             >>> my_frame.dot_product('col_4', 'col_5', 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_4       col_5        dot_product
            =========================================
            [0]  [1.0, 0.2]  [-2.0, 5.0]         -1.0
            [1]  [2.0, 0.4]  [-1.0, 6.0]          0.4
            [2]  [3.0, 0.6]  [0.0, 7.0]           4.2
            [3]  [4.0, 0.8]  [1.0, 8.0]          10.4


        :param left_column_names: Names of columns used to create the left vector (A) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type left_column_names: list
        :param right_column_names: Names of columns used to create right vector (B) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type right_column_names: list
        :param dot_product_column_name: Name of column used to store the
            dot product.
        :type dot_product_column_name: unicode
        :param default_left_values: (default=None)  Default values used to substitute null values in left vector.
            Default is None.
        :type default_left_values: list
        :param default_right_values: (default=None)  Default values used to substitute null values in right vector.
            Default is None.
        :type default_right_values: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def download(self, n=100, offset=0, columns=None):
        """
        Download frame data from the server into client workspace as a pandas dataframe

        Similar to the 'take' function, but puts the data in a pandas dataframe.

        Examples
        --------

        .. code::

            >>> pandas_frame = frame.download(columns=['name', 'phone'])
            >>> pandas_frame
                   name     phone
            0      Fred  555-1234
            1     Susan  555-0202
            2  Thurston  555-4510
            3      Judy  555-2183



        :param n: (default=100)  The number of rows to download to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before copying
        :type offset: int
        :param columns: (default=None)  Column filter, the names of columns to be included (default is all columns)
        :type columns: list

        :returns: A new pandas dataframe object containing the downloaded frame data
        :rtype: pandas.DataFrame
        """
        return None


    @doc_stub
    def drop_columns(self, columns):
        """
        Remove columns from the frame.

        The data from the columns is lost.

        Notes
        -----
        It is not possible to delete all columns from a frame.
        At least one column needs to remain.
        If it is necessary to delete all columns, then delete the frame.

        Examples
        --------
        For this example, the Frame object *my_frame* accesses a frame with 4 columns
        columns *column_a*, *column_b*, *column_c* and *column_d* and drops 2 columns *column_b* and *column_d* using drop columns.



            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_b', <type 'numpy.int32'>), (u'column_c', <type 'unicode'>), (u'column_d', <type 'numpy.int32'>)]


        Eliminate columns *column_b* and *column_d*:

            >>> my_frame.drop_columns(["column_b", "column_d"])
            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_c', <type 'unicode'>)]

        Now the frame only has the columns *column_a* and *column_c*.
        For further examples, see: ref:`example_frame.drop_columns`.




        :param columns: Column name OR list of column names to be removed from the frame.
        :type columns: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_duplicates(self, unique_columns=None):
        """
        Modify the current frame, removing duplicate rows.

        Remove data rows which are the same as other rows.
        The entire row can be checked for duplication, or the search for duplicates
        can be limited to one or more columns.
        This modifies the current frame.

        Given a frame with data:

        .. code::


            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  200  4  25
            [1]  200  5  25
            [2]  200  4  25
            [3]  200  5  35
            [4]  200  6  25
            [5]  200  8  35
            [6]  200  4  45
            [7]  200  4  25
            [8]  200  5  25
            [9]  201  4  25

        Remove any rows that are identical to a previous row.
        The result is a frame of unique rows.
        Note that row order may change.

        .. code::

            >>> frame.drop_duplicates()
            [===Job Progress===]
            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  201  4  25
            [1]  200  4  25
            [2]  200  5  25
            [3]  200  8  35
            [4]  200  6  25
            [5]  200  5  35
            [6]  200  4  45


        Now remove any rows that have the same data in columns *a* and
        *c* as a previously checked row:

        .. code::

            >>> frame.drop_duplicates([ "a", "c"])
            [===Job Progress===]

        The result is a frame with unique values for the combination of columns *a*
        and *c*.

        .. code::

            >>> frame.inspect()
            [#]  a    b  c
            ===============
            [0]  201  4  25
            [1]  200  4  45
            [2]  200  4  25
            [3]  200  8  35


        :param unique_columns: (default=None)  
        :type unique_columns: None

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_rows(self, predicate):
        """
        Erase any row in the current frame which qualifies.

        Examples
        --------

        .. code::


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.drop_rows(lambda row: row.name[-1] == 'n')  # drop people whose name ends in 'n'
            [===Job Progress===]
            >>> frame.inspect()
            [#]  name  age  tenure  phone
            ================================
            [0]  Fred   39      16  555-1234
            [1]  Judy   44      14  555-2183

        More information on a |UDF| can be found at :doc:`/ds_apir`.


        :param predicate: |UDF| which evaluates a row to a boolean; rows that answer True are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def ecdf(self, column, result_frame_name=None):
        """
        Builds new frame with columns for data and distribution.

        Generates the empirical cumulative distribution for the input column.

        Consider the following sample data set in *frame* 'frame' containing several numbers.


        >>> frame.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        4
        [7]        3
        >>> ecdf_frame = frame.ecdf('numbers')
        [===Job Progress===]
        >>> ecdf_frame.inspect()
        [#]  numbers  numbers_ECDF
        ==========================
        [0]        0         0.125
        [1]        1           0.5
        [2]        2         0.625
        [3]        3         0.875
        [4]        4           1.0



        :param column: The name of the input column containing sample.
        :type column: unicode
        :param result_frame_name: (default=None)  A name for the resulting frame which is created
            by this operation.
        :type result_frame_name: unicode

        :returns: A new Frame containing each distinct value in the sample and its corresponding ECDF value.
        :rtype: Frame
        """
        return None


    @doc_stub
    def entropy(self, data_column, weights_column=None):
        """
        Calculate the Shannon entropy of a column.

        The data column is weighted via the weights column.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements with a finite weight greater than 0,
        the entropy is zero.

        Consider the following sample data set in *frame* 'frame' containing several numbers.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data  weight
        =================
        [0]     0       1
        [1]     1       2
        [2]     2       4
        [3]     4       8
        >>> entropy = frame.entropy("data", "weight")
        [===Job Progress===]

        >>> "%0.8f" % entropy
        '1.13691659'



        If we have more choices and weights, the computation is not as simple.
        An on-line search for "Shannon Entropy" will provide more detail.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data
        =========
        [0]  H
        [1]  T
        [2]  H
        [3]  T
        [4]  H
        [5]  T
        [6]  H
        [7]  T
        [8]  H
        [9]  T
        >>> entropy = frame.entropy("data")
        [===Job Progress===]
        >>> "%0.8f" % entropy
        '0.69314718'



        :param data_column: The column whose entropy is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the entropy calculation.
            Must contain numerical data.
            Default is using uniform weights of 1 for all items.
        :type weights_column: unicode

        :returns: Entropy.
        :rtype: float64
        """
        return None


    @doc_stub
    def export_to_csv(self, folder_name, separator=',', count=-1, offset=0):
        """
        Write current frame to HDFS in csv format.

        Export the frame to a file in csv format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_csv('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"



        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param separator: (default=,)  The separator for separating the values.
            Default is comma (,).
        :type separator: unicode
        :param count: (default=-1)  The number of records you want.
            Default, or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def export_to_hbase(self, table_name, key_column_name=None, family_name='familyColumn'):
        """
        Write current frame to HBase table.

        Table must exist in HBase.
        Export of Vectors is not currently supported.

        Examples
        --------

        Overwrite/append scenarios (see below):

        1. create a simple hbase table from csv
               load csv into a frame using existing frame api
               save the frame into hbase (it creates a table - lets call it table1)

        2. overwrite existing table with new data
               do scenario 1 and create table1
               load the second csv into a frame
               save the frame into table1 (old data is gone)

        3. append data to the existing table 1
               do scenario 1 and create table1
               load table1 into frame1
               load csv into frame2
               let frame1 = frame1 + frame2 (concatenate frame2 into frame1)
               save frame1 into base as table1 (overwrite with initial + appended data)


        Vector scenarios (see below):

        Vectors are not directly supported by HBase (which represents data as byte arrays) or the plugin.
        While is true that a vector can be saved because of the byte array conversion for hbase, the following
        is actually the recommended practice:

        1. Convert the vector to csv (in python, outside ATK)
        2. save the csv as string in the database (using ATK export_to_hbase)
        3. read the cell as string (using ATK, read from hbase
        4. convert the csv to vector (in python, outside ATK)




        :param table_name: The name of the HBase table that will contain the exported frame
        :type table_name: unicode
        :param key_column_name: (default=None)  The name of the column to be used as row key in hbase table
        :type key_column_name: unicode
        :param family_name: (default=familyColumn)  The family name of the HBase table that will contain the exported frame
        :type family_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_hive(self, table_name):
        """
        Write  current frame to Hive table.

        Table must not exist in Hive. Hive does not support case sensitive table names and columns names. Hence column names with uppercase letters will be converted to lower case by Hive.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_hive('covarianceresults')

        :param table_name: The name of the Hive table that will contain the exported frame
        :type table_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_jdbc(self, table_name, connector_type='postgres'):
        """
        Write current frame to JDBC table.

        Table will be created or appended to.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_jdbc('covarianceresults')



        :param table_name: JDBC table name
        :type table_name: unicode
        :param connector_type: (default=postgres)  (optional) JDBC connector, either mysql or postgres. Default is postgres
        :type connector_type: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_json(self, folder_name, count=0, offset=0):
        """
        Write current frame to HDFS in JSON format.

        Export the frame to a file in JSON format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_json('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"


        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param count: (default=0)  The number of records you want.
            Default (0), or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def filter(self, predicate):
        """
        Select all rows which satisfy a predicate.

        Modifies the current frame to save defined rows and delete everything
        else.

        Examples
        --------

            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.filter(lambda row: row.tenure >= 15)  # keep only people with 15 or more years tenure
            [===Job Progress===]
            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Thurston   65      26  555-4510

        More information on a |UDF| can be found at :doc:`/ds_apir`.


        :param predicate: |UDF| which evaluates a row to a boolean; rows that answer False are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def flatten_columns(self, columns, delimiters=None):
        """
        Spread data to multiple rows based on cell data.

        Splits cells in the specified columns into multiple rows according to a string
        delimiter.
        New rows are a full copy of the original row, but the specified columns only
        contain one value.
        The original row is deleted.

        Examples
        --------

        Given a data file::

            1-solo,mono,single-green,yellow,red
            2-duo,double-orange,black

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32), ('b', str),('c',str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32),
                ... ('b', str),('c', str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)


        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a  b                 c
            ==========================================
            [0]  1  solo,mono,single  green,yellow,red
            [1]  2  duo,double        orange,black

        Now, spread out those sub-strings in column *b* and *c*:

        .. code::

            >>> frame.flatten_columns(['b','c'], ',')
            [===Job Progress===]

        Note that the delimiters parameter is optional, and if no delimiter is specified, the default
        is a comma (,).  So, in the above example, the delimiter parameter could be omitted.  Also, if
        the delimiters are different for each column being flattened, a list of delimiters can be
        provided.  If a single delimiter is provided, it's assumed that we are using the same delimiter
        for all columns that are being flattened.  If more than one delimiter is provided, the number of
        delimiters must match the number of string columns being flattened.

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a  b       c
            ======================
            [0]  1  solo    green
            [1]  1  mono    yellow
            [2]  1  single  red
            [3]  2  duo     orange
            [4]  2  double  black


        Alternatively, flatten_columns also accepts a single column name (instead of a list) if just one
        column is being flattened.  For example, we could have called flatten_column on just column *b*:


        .. code::

            >>> frame.flatten_columns('b', ',')
            [===Job Progress===]

        Check again:

        .. code ::

            >>> frame.inspect()
            [#]  a  b       c
            ================================
            [0]  1  solo    green,yellow,red
            [1]  1  mono    green,yellow,red
            [2]  1  single  green,yellow,red
            [3]  2  duo     orange,black
            [4]  2  double  orange,black





        :param columns: The columns to be flattened.
        :type columns: list
        :param delimiters: (default=None)  The list of delimiter strings for each column.
            Default is comma (,).
        :type delimiters: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def get_error_frame(self):
        """
        Get a frame with error recordings.

        When a frame is created, another frame is transparently
        created to capture parse errors.

        Returns
        -------
        Frame : error frame object
            A new object accessing a frame that contains the parse errors of
            the currently active Frame or None if no error frame exists.



        """
        return None


    @doc_stub
    def group_by(self, group_by_columns, *aggregation_arguments):
        """
        Create summarized frame.

        Creates a new frame and returns a Frame object to access it.
        Takes a column or group of columns, finds the unique combination of
        values, and creates unique rows with these column values.
        The other columns are combined according to the aggregation
        argument(s).

        Notes
        -----
        *   Column order is not guaranteed when columns are added
        *   The column names created by aggregation functions in the new frame
            are the original column name appended with the '_' character and
            the aggregation function.
            For example, if the original field is *a* and the function is
            *avg*, the resultant column is named *a_avg*.
        *   An aggregation argument of *count* results in a column named
            *count*.
        *   The aggregation function *agg.count* is the only full row
            aggregation function supported at this time.
        *   Aggregation currently supports using the following functions:

            *   avg
            *   count
            *   count_distinct
            *   max
            *   min
            *   stdev
            *   sum
            *   var (see glossary Bias vs Variance)
            *   The aggregation arguments also accepts the User Defined function(UDF). UDF acts on each row

        Examples
        --------
        For setup, we will use a Frame *my_frame* accessing a frame with a
        column *a*:

        .. code::


            >>> frame.inspect()
            [#]  a  b        c     d       e  f    g
            ========================================
            [0]  1  alpha     3.0  small   1  3.0  9
            [1]  1  bravo     5.0  medium  1  4.0  9
            [2]  1  alpha     5.0  large   1  8.0  8
            [3]  2  bravo     8.0  large   1  5.0  7
            [4]  2  charlie  12.0  medium  1  6.0  6
            [5]  2  bravo     7.0  small   1  8.0  5
            [6]  2  bravo    12.0  large   1  6.0  4

            Count the groups in column 'b'

            >>> b_count = frame.group_by('b', ta.agg.count)
            [===Job Progress===]
            >>> b_count.inspect()
            [#]  b        count
            ===================
            [0]  alpha        2
            [1]  bravo        4
            [2]  charlie      1

            >>> avg1 = frame.group_by(['a', 'b'], {'c' : ta.agg.avg})
            [===Job Progress===]
            >>> avg1.inspect()
            [#]  a  b        c_AVG
            ======================
            [0]  2  bravo      9.0
            [1]  1  alpha      4.0
            [2]  2  charlie   12.0
            [3]  1  bravo      5.0

            >>> mix_frame = frame.group_by('a', ta.agg.count, {'f': [ta.agg.avg, ta.agg.sum, ta.agg.min], 'g': ta.agg.max})
            [===Job Progress===]
            >>> mix_frame.inspect()
            [#]  a  count  g_MAX  f_AVG  f_SUM  f_MIN
            =========================================
            [0]  1      3      9    5.0   15.0    3.0
            [1]  2      4      7   6.25   25.0    5.0

            >>> def custom_agg(acc, row):
            ...     acc.c_sum = acc.c_sum + row.c
            ...     acc.c_prod= acc.c_prod*row.c

            >>> sum_prod_frame = frame.group_by(['a', 'b'], ta.agg.udf(aggregator=custom_agg,output_schema=[('c_sum', ta.float64),('c_prod', ta.float64)],init_values=[0,1]))
            [===Job Progress===]

            >>> sum_prod_frame.inspect()
            [#]  a  b        c_sum  c_prod
            ==============================
            [0]  2  bravo     27.0   672.0
            [1]  1  alpha      8.0    15.0
            [2]  2  charlie   12.0    12.0
            [3]  1  bravo      5.0     5.0

        For further examples, see :ref:`example_frame.group_by`.


        :param group_by_columns: Column name or list of column names
        :type group_by_columns: list
        :param *aggregation_arguments: (default=None)  Aggregation function based on entire row, and/or dictionaries (one or more) of { column name str : aggregation function(s) }.
        :type *aggregation_arguments: dict

        :returns: A new frame with the results of the group_by
        :rtype: Frame
        """
        return None


    @doc_stub
    def histogram(self, column_name, num_bins=None, weight_column_name=None, bin_type='equalwidth'):
        """
        Compute the histogram for a column in a frame.

        Compute the histogram of the data in a column.
        The returned value is a Histogram object containing 3 lists one each for:
        the cutoff points of the bins, size of each bin, and density of each bin.

        **Notes**

        The num_bins parameter is considered to be the maximum permissible number
        of bins because the data may dictate fewer bins.
        With equal depth binning, for example, if the column to be binned has 10
        elements with only 2 distinct values and the *num_bins* parameter is
        greater than 2, then the number of actual number of bins will only be 2.
        This is due to a restriction that elements with an identical value must
        belong to the same bin.

        Examples
        --------

        Consider the following sample data set\:

        .. code::

            >>> frame.inspect()
                [#]  a  b
                =========
                [0]  a  2
                [1]  b  7
                [2]  c  3
                [3]  d  9
                [4]  e  1

        A simple call for 3 equal-width bins gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3)
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 3.6666666666666665, 6.333333333333333, 9.0],
            hist: [3.0, 0.0, 2.0],
            density: [0.6, 0.0, 0.4]

        Switching to equal depth gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3, bin_type='equaldepth')
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 2.0, 7.0, 9.0],
            hist: [1.0, 2.0, 2.0],
            density: [0.2, 0.4, 0.4]

        .. only:: html

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - hist.cutoffs[0])
        .. only:: latex

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - 
                ... hist.cutoffs[0])


        :param column_name: Name of column to be evaluated.
        :type column_name: unicode
        :param num_bins: (default=None)  Number of bins in histogram.
            Default is Square-root choice will be used
            (in other words math.floor(math.sqrt(frame.row_count)).
        :type num_bins: int32
        :param weight_column_name: (default=None)  Name of column containing weights.
            Default is all observations are weighted equally.
        :type weight_column_name: unicode
        :param bin_type: (default=equalwidth)  The type of binning algorithm to use: ["equalwidth"|"equaldepth"]
            Defaults is "equalwidth".
        :type bin_type: unicode

        :returns: histogram
                A Histogram object containing the result set.
                The data returned is composed of multiple components:
            cutoffs : array of float
                A list containing the edges of each bin.
            hist : array of float
                A list containing count of the weighted observations found in each bin.
            density : array of float
                A list containing a decimal containing the percentage of
                observations found in the total set per bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def inspect(self, n=10, offset=0, columns=None, wrap='inspect_settings', truncate='inspect_settings', round='inspect_settings', width='inspect_settings', margin='inspect_settings', with_types='inspect_settings'):
        """
        Pretty-print of the frame data

        Essentially returns a string, but technically returns a RowInspection object which renders a string.
        The RowInspection object naturally converts to a str when needed, like when printed or when displayed
        by python REPL (i.e. using the object's __repr__).  If running in a script and want the inspect output
        to be printed, then it must be explicitly printed, then `print frame.inspect()`


        Examples
        --------
        To look at the first 4 rows of data in a frame:

        .. code::

            >>> frame.inspect(4)
            [#]  animal    name    age  weight
            ==================================
            [0]  human     George    8   542.5
            [1]  human     Ursula    6   495.0
            [2]  ape       Ape      41   400.0
            [3]  elephant  Shep      5  8630.0

        # For other examples, see :ref:`example_frame.inspect`.

        Note: if the frame data contains unicode characters, this method may raise a Unicode exception when
        running in an interactive REPL or otherwise which triggers the standard python repr().  To get around
        this problem, explicitly print the unicode of the returned object:

        .. code::

            >>> print unicode(frame.inspect())


        **Global Settings**

        If not specified, the arguments that control formatting receive default values from
        'trustedanalytics.inspect_settings'.  Make changes there to affect all calls to inspect.

        .. code::

            >>> import trustedanalytics as ta
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = 120  # changes inspect to use 120 width globally
            >>> ta.inspect_settings.truncate = 16  # changes inspect to always truncate strings to 16 chars
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width           120
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = None  # return value back to default
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.reset()  # set everything back to default
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False

        ..


        :param n: (default=10)  The number of rows to print (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before printing.
        :type offset: int
        :param columns: (default=None)  Filter columns to be included.  By default, all columns are included
        :type columns: int
        :param wrap: (default=inspect_settings)  If set to 'stripes' then inspect prints rows in stripes; if set to an integer N, rows will be printed in clumps of N columns, where the columns are wrapped
        :type wrap: int or 'stripes'
        :param truncate: (default=inspect_settings)  If set to integer N, all strings will be truncated to length N, including a tagged ellipses
        :type truncate: int
        :param round: (default=inspect_settings)  If set to integer N, all floating point numbers will be rounded and truncated to N digits
        :type round: int
        :param width: (default=inspect_settings)  If set to integer N, the print out will try to honor a max line width of N
        :type width: int
        :param margin: (default=inspect_settings)  ('stripes' mode only) If set to integer N, the margin for printing names in a stripe will be limited to N characters
        :type margin: int
        :param with_types: (default=inspect_settings)  If set to True, header will include the data_type of each column
        :type with_types: bool

        :returns: An object which naturally converts to a pretty-print string
        :rtype: RowsInspection
        """
        return None


    @doc_stub
    def join(self, right, left_on, right_on=None, how='inner', name=None):
        """
        Join operation on one or two frames, creating a new frame.

        Create a new frame from a SQL JOIN operation with another frame.
        The frame on the 'left' is the currently active frame.
        The frame on the 'right' is another frame.
        This method take column(s) in the left frame and matches its values
        with column(s) in the right frame.
        Using the default 'how' option ['inner'] will only allow data in the
        resultant frame if both the left and right frames have the same value
        in the matching column(s).
        Using the 'left' 'how' option will allow any data in the resultant
        frame if it exists in the left frame, but will allow any data from the
        right frame if it has a value in its column(s) which matches the value in
        the left frame column(s).
        Using the 'right' option works similarly, except it keeps all the data
        from the right frame and only the data from the left frame when it
        matches.
        The 'outer' option provides a frame with data from both frames where
        the left and right frames did not have the same value in the matching
        column(s).

        Notes
        -----
        When a column is named the same in both frames, it will result in two
        columns in the new frame.
        The column from the *left* frame (originally the current frame) will be
        copied and the column name will have the string "_L" added to it.
        The same thing will happen with the column from the *right* frame,
        except its name has the string "_R" appended. The order of columns
        after this method is called is not guaranteed.

        It is recommended that you rename the columns to meaningful terms prior
        to using the ``join`` method.
        Keep in mind that unicode in column names will likely cause the
        drop_frames() method (and others) to fail!

        Examples
        --------


        Consider two frames: codes and colors

        >>> codes.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        5
        [7]        3


        >>> colors.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        2  yellow
        [2]        3  green
        [3]        4  blue


        Join them on the 'numbers' column ('inner' join by default)

        >>> j = codes.join(colors, 'numbers')
        [===Job Progress===]

        >>> j.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        3  green
        [2]        1  red
        [3]        2  yellow
        [4]        1  red
        [5]        3  green

        (The join adds an extra column *_R which is the join column from the right frame; it may be disregarded)

        Try a 'left' join, which includes all the rows of the codes frame.

        >>> j_left = codes.join(colors, 'numbers', how='left')
        [===Job Progress===]

        >>> j_left.inspect()
        [#]  numbers_L  color
        ======================
        [0]          1  red
        [1]          3  green
        [2]          1  red
        [3]          0  None
        [4]          2  yellow
        [5]          1  red
        [6]          5  None
        [7]          3  green


        And an outer join:

        >>> j_outer = codes.join(colors, 'numbers', how='outer')
        [===Job Progress===]

        >>> j_outer.inspect()
        [#]  numbers_L  color
        ======================
        [0]          0  None
        [1]          1  red
        [2]          1  red
        [3]          1  red
        [4]          2  yellow
        [5]          3  green
        [6]          3  green
        [7]          4  blue
        [8]          5  None

        Consider two frames: country_codes_frame and country_names_frame

        >>> country_codes_frame.inspect()
        [#]  col_0  col_1  col_2
        ========================
        [0]      1    354  a
        [1]      2     91  a
        [2]      2    100  b
        [3]      3     47  a
        [4]      4    968  c
        [5]      5     50  c


        >>> country_names_frame.inspect()
        [#]  col_0  col_1     col_2
        ===========================
        [0]      1  Iceland   a
        [1]      1  Ice-land  a
        [2]      2  India     b
        [3]      3  Norway    a
        [4]      4  Oman      c
        [5]      6  Germany   c

        Join them on the 'col_0' and 'col_2' columns ('inner' join by default)

        >>> composite_join = country_codes_frame.join(country_names_frame, ['col_0', 'col_2'])
        [===Job Progress===]

        >>> composite_join.inspect()
        [#]  col_0  col_1_L  col_2  col_1_R
        ====================================
        [0]      1      354  a      Ice-land
        [1]      1      354  a      Iceland
        [2]      2      100  b      India
        [3]      3       47  a      Norway
        [4]      4      968  c      Oman

        More examples can be found in the :ref:`user manual
        <example_frame.join>`.


        :param right: Another frame to join with
        :type right: Frame
        :param left_on: Names of the columns in the left frame used to match up the two frames.
        :type left_on: list
        :param right_on: (default=None)  Names of the columns in the right frame used to match up the two frames. Default is the same as the left frame.
        :type right_on: list
        :param how: (default=inner)  How to qualify the data to be joined together.  Must be one of the following:  'left', 'right', 'inner', 'outer'.  Default is 'inner'
        :type how: str
        :param name: (default=None)  Name of the result grouped frame
        :type name: str

        :returns: A new frame with the results of the join
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def last_read_date(self):
        """
        Last time this frame's data was accessed.

        Examples
        --------

        .. code::

            >>> frame.last_read_date
            datetime.datetime(2015, 10, 8, 15, 48, 8, 791000, tzinfo=tzoffset(None, -25200))





        :returns: Date string of the last time this frame's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the frame object.

        Change or retrieve frame object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_frame.name
            "abc"

            >>> my_frame.name = "xyz"
            >>> my_frame.name
            "xyz"




        """
        return None


    @doc_stub
    def quantiles(self, column_name, quantiles):
        """
        New frame with Quantiles and their values.

        Calculate quantiles on the given column.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column *final_sale_price*:

        .. code::

            >>> my_frame.inspect()
            [#]  final_sale_price
            =====================
            [0]               100
            [1]               250
            [2]                95
            [3]               179
            [4]               315
            [5]               660
            [6]               540
            [7]               420
            [8]               250
            [9]               335

        To calculate 10th, 50th, and 100th quantile:

        .. code::

            >>> quantiles_frame = my_frame.quantiles('final_sale_price', [10, 50, 100])
            [===Job Progress===]

        A new Frame containing the requested Quantiles and their respective values
        will be returned :

        .. code::

           >>> quantiles_frame.inspect()
           [#]  Quantiles  final_sale_price_QuantileValue
           ==============================================
           [0]       10.0                            95.0
           [1]       50.0                           250.0
           [2]      100.0                           660.0


        :param column_name: The column to calculate quantiles.
        :type column_name: unicode
        :param quantiles: What is being requested.
        :type quantiles: list

        :returns: A new frame with two columns (float64): requested Quantiles and their respective values.
        :rtype: Frame
        """
        return None


    @doc_stub
    def rename_columns(self, names):
        """
        Rename columns

        Examples
        --------
        Start with a frame with columns *Black* and *White*.



            >>> print my_frame.schema
            [(u'Black', <type 'unicode'>), (u'White', <type 'unicode'>)]

        Rename the columns to *Mercury* and *Venus*:

            >>> my_frame.rename_columns({"Black": "Mercury", "White": "Venus"})

            >>> print my_frame.schema
            [(u'Mercury', <type 'unicode'>), (u'Venus', <type 'unicode'>)]



        :param names: Dictionary of old names to new names.
        :type names: dict

        :returns: 
        :rtype: _Unit
        """
        return None


    @property
    @doc_stub
    def row_count(self):
        """
        Number of rows in the current frame.

        Counts all of the rows in the frame.

        Examples
        --------
        Get the number of rows:

        .. code::

            >>> frame.row_count
            4





        :returns: The number of rows in the frame
        :rtype: int
        """
        return None


    @property
    @doc_stub
    def schema(self):
        """
        Current frame column names and types.

        The schema of the current frame is a list of column names and
        associated data types.
        It is retrieved as a list of tuples.
        Each tuple has the name and data type of one of the frame's columns.

        Examples
        --------

        .. code::

            >>> frame.schema
            [(u'name', <type 'unicode'>), (u'age', <type 'numpy.int32'>), (u'tenure', <type 'numpy.int32'>), (u'phone', <type 'unicode'>)]

        Note how the types shown are the raw, underlying types used in python.  To see the schema in a friendlier
        format, used the __repr__ presentation, invoke by simply entering the frame:
            >>> frame
            Frame "example_frame"
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode]
            status = ACTIVE  (last_read_date = -etc-)





        :returns: list of tuples of the form (<column name>, <data type>)
        :rtype: list
        """
        return None


    @doc_stub
    def sort(self, columns, ascending=True):
        """
        Sort the data in a frame.

        Sort a frame by column values either ascending or descending.

        Examples
        --------


        Consider the frame
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     1  charlie
            [2]     3  bravo
            [3]     2  echo
            [4]     4  delta
            [5]     3  alpha

        Sort a single column:

        .. code::

            >>> frame.sort('col1')
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  foxtrot
            [3]     3  bravo
            [4]     3  alpha
            [5]     4  delta

        Sort a single column descending:

        .. code::

            >>> frame.sort('col2', False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     2  echo
            [2]     4  delta
            [3]     1  charlie
            [4]     3  bravo
            [5]     3  alpha

        Sort multiple columns:

        .. code::

            >>> frame.sort(['col1', 'col2'])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  alpha
            [3]     3  bravo
            [4]     3  foxtrot
            [5]     4  delta


        Sort multiple columns descending:

        .. code::

            >>> frame.sort(['col1', 'col2'], False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  foxtrot
            [2]     3  bravo
            [3]     3  alpha
            [4]     2  echo
            [5]     1  charlie

        Sort multiple columns: 'col1' decending and 'col2' ascending:

        .. code::

            >>> frame.sort([ ('col1', False), ('col2', True) ])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  alpha
            [2]     3  bravo
            [3]     3  foxtrot
            [4]     2  echo
            [5]     1  charlie



        :param columns: Either a column name, a list of column names, or a list of tuples where each tuple is a name and an ascending bool value.
        :type columns: str | list of str | list of tuples
        :param ascending: (default=True)  True for ascending, False for descending.
        :type ascending: bool
        """
        return None


    @doc_stub
    def sorted_k(self, k, column_names_and_ascending, reduce_tree_depth=None):
        """
        Get a sorted subset of the data.

        Take a number of rows and return them
        sorted in either ascending or descending order.

        Sorting a subset of rows is more efficient than sorting the entire frame when
        the number of sorted rows is much less than the total number of rows in the frame.

        Notes
        -----
        The number of sorted rows should be much smaller than the number of rows
        in the original frame.

        In particular:

        #)  The number of sorted rows returned should fit in Spark driver memory.
            The maximum size of serialized results that can fit in the Spark driver is
            set by the Spark configuration parameter *spark.driver.maxResultSize*.
        #)  If you encounter a Kryo buffer overflow exception, increase the Spark
            configuration parameter *spark.kryoserializer.buffer.max.mb*.
        #)  Use Frame.sort() instead if the number of sorted rows is very large (in
            other words, it cannot fit in Spark driver memory).

        Examples
        --------
        These examples deal with the most recently-released movies in a private collection.
        Consider the movie collection already stored in the frame below:

            >>> my_frame.inspect()
            [#]  genre      year  title
            ========================================================
            [0]  Drama      1957  12 Angry Men
            [1]  Crime      1946  The Big Sleep
            [2]  Western    1969  Butch Cassidy and the Sundance Kid
            [3]  Drama      1971  A Clockwork Orange
            [4]  Drama      2008  The Dark Knight
            [5]  Animation  2013  Frozen
            [6]  Drama      1972  The Godfather
            [7]  Animation  1994  The Lion King
            [8]  Animation  2010  Tangled
            [9]  Fantasy    1939  The WOnderful Wizard of Oz


        This example returns the top 3 rows sorted by a single column: 'year' descending:

            >>> topk_frame = my_frame.sorted_k(3, [ ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Drama      2008  The Dark Knight

        This example returns the top 5 rows sorted by multiple columns: 'genre' ascending, then 'year' descending:

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Animation  1994  The Lion King
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      2008  The Dark Knight


        This example returns the top 5 rows sorted by multiple columns: 'genre'
        ascending, then 'year' ascending.
        It also illustrates the optional tuning parameter for reduce-tree depth
        (which does not affect the final result).

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', True) ], reduce_tree_depth=1)
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            ===================================
            [0]  Animation  1994  The Lion King
            [1]  Animation  2010  Tangled
            [2]  Animation  2013  Frozen
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      1957  12 Angry Men




        :param k: Number of sorted records to return.
        :type k: int32
        :param column_names_and_ascending: Column names to sort by, and true to sort column by ascending order,
            or false for descending order.
        :type column_names_and_ascending: list
        :param reduce_tree_depth: (default=None)  Advanced tuning parameter which determines the depth of the
            reduce-tree (uses Spark's treeReduce() for scalability.)
            Default is 2.
        :type reduce_tree_depth: int32

        :returns: A new frame with a subset of sorted rows from the original frame.
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Current frame life cycle status.

        One of three statuses: ACTIVE, DROPPED, FINALIZED
           ACTIVE:    Entity is available for use
           DROPPED:   Entity has been dropped by user or by garbage collection which found it stale
           FINALIZED: Entity's data has been deleted

        Examples
        --------

        .. code::

            >>> frame.status
            u'ACTIVE'





        :returns: Status of the frame
        :rtype: str
        """
        return None


    @doc_stub
    def take(self, n, offset=0, columns=None):
        """
        Get data subset.

        Take a subset of the currently active Frame.

        Examples
        --------
        .. code::

            >>> frame.take(2)
            [[u'Fred', 39, 16, u'555-1234'], [u'Susan', 33, 3, u'555-0202']]

            >>> frame.take(2, offset=2)
            [[u'Thurston', 65, 26, u'555-4510'], [u'Judy', 44, 14, u'555-2183']]



        :param n: The number of rows to copy to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before starting to copy
        :type offset: int
        :param columns: (default=None)  If not None, only the given columns' data will be provided.  By default, all columns are included
        :type columns: str | iterable of str

        :returns: A list of lists, where each contained list is the data for one row.
        :rtype: list
        """
        return None


    @doc_stub
    def tally(self, sample_col, count_val):
        """
        Count number of times a value is seen.

        A cumulative count is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the number of times the specified
        *count_value* has been seen.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally
            ===================
            [0]    0        0.0
            [1]    1        1.0
            [2]    2        1.0
            [3]    0        1.0
            [4]    1        2.0
            [5]    2        2.0

        :param sample_col: The name of the column from which to compute the cumulative count.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def tally_percent(self, sample_col, count_val):
        """
        Compute a cumulative percent count.

        A cumulative percent count is computed by sequentially stepping through
        the rows, observing the column values and keeping track of the percentage of the
        total number of times the specified *count_value* has been seen up to
        the current value.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally_percent("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally_percent
            ===========================
            [0]    0                0.0
            [1]    1                0.5
            [2]    2                0.5
            [3]    0                0.5
            [4]    1                1.0
            [5]    2                1.0



        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def timeseries_from_observations(self, date_time_index, timestamp_column, key_column, value_column):
        """
        Returns a frame that has the observations formatted as a time series.

        Uses the specified timestamp, key, and value columns and the date/time
                        index provided to format the observations as a time series.  The time series
                        frame will have columns for the key and a vector of the observed values that
                        correspond to the date/time index.

        Examples
        --------
        In this example, we will use a frame of observations of resting heart rate for
        three individuals over three days.  The data is accessed from Frame object
        called *my_frame*:


        .. code::

         >>> my_frame.inspect( my_frame.row_count )
         [#]  name     date                      resting_heart_rate
         ==========================================================
         [0]  Edward   2016-01-01T12:00:00.000Z                62.0
         [1]  Stanley  2016-01-01T12:00:00.000Z                57.0
         [2]  Edward   2016-01-02T12:00:00.000Z                63.0
         [3]  Sarah    2016-01-02T12:00:00.000Z                64.0
         [4]  Stanley  2016-01-02T12:00:00.000Z                57.0
         [5]  Edward   2016-01-03T12:00:00.000Z                62.0
         [6]  Sarah    2016-01-03T12:00:00.000Z                64.0
         [7]  Stanley  2016-01-03T12:00:00.000Z                56.0


        We then need to create an array that contains the date/time index,
        which will be used when creating the time series.  Since our data
        is for three days, our date/time index will just contain those
        three dates:

        .. code::

         >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z"]

        Then we can create our time series frame by specifying our date/time
        index along with the name of our timestamp column (in this example, it's
         "date"), key column (in this example, it's "name"), and value column (in
        this example, it's "resting_heart_rate").

        .. code::

         >>> ts = my_frame.timeseries_from_observations(datetimeindex, "date", "name", "resting_heart_rate")
         [===Job Progress===]

        Take a look at the resulting time series frame schema and contents:

        .. code::

         >>> ts.schema
         [(u'name', <type 'unicode'>), (u'resting_heart_rate', vector(3))]

         >>> ts.inspect()
         [#]  name     resting_heart_rate
         ================================
         [0]  Stanley  [57.0, 57.0, 56.0]
         [1]  Edward   [62.0, 63.0, 62.0]
         [2]  Sarah    [None, 64.0, 64.0]



        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param timestamp_column: The name of the column telling when the observation occurred.
        :type timestamp_column: unicode
        :param key_column: The name of the column that contains which string key the observation belongs to.
        :type key_column: unicode
        :param value_column: The name of the column that contains the observed value.
        :type value_column: unicode

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def timeseries_slice(self, date_time_index, start, end):
        """
        Returns a frame that is a sub-slice of the given series.

        Splits a time series frame on the specified start and end date/times.

        Examples
        --------
        For this example, we start with a frame that has already been formatted as a time series.
        This means that the frame has a string column for key and a vector column that contains
        a series of the observed values.  We must also know the date/time index that corresponds
        to the time series.

        The time series is in a Frame object called *ts_frame*.


        .. code::

            >>> ts_frame.inspect()
            [#]  key  series
            ==============================================
            [0]  A    [62.0, 55.0, 60.0, 61.0, 60.0, 59.0]
            [1]  B    [60.0, 58.0, 61.0, 62.0, 60.0, 61.0]
            [2]  C    [69.0, 68.0, 68.0, 70.0, 71.0, 69.0]

        Next, we define the date/time index.  In this example, it is one day intervals from
        2016-01-01 to 2016-01-06:

        .. code::

            >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z","2016-01-04T12:00:00.000Z","2016-01-05T12:00:00.000Z","2016-01-06T12:00:00.000Z"]

        Get a slice of our time series from 2016-01-02 to 2016-01-04:

        .. code::
            >>> slice_start = "2016-01-02T12:00:00.000Z"
            >>> slice_end = "2016-01-04T12:00:00.000Z"

            >>> sliced_frame = ts_frame.timeseries_slice(datetimeindex, slice_start, slice_end)
            [===Job Progress===]

        Take a look at our sliced time series:

        .. code::

            >>> sliced_frame.inspect()
            [#]  key  series
            ============================
            [0]  A    [55.0, 60.0, 61.0]
            [1]  B    [58.0, 61.0, 62.0]
            [2]  C    [68.0, 68.0, 70.0]


        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param start: The start date for the slice in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ 
        :type start: datetime
        :param end: The end date for the slice (inclusive) in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ.
        :type end: datetime

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def top_k(self, column_name, k, weights_column=None):
        """
        Most or least frequent column values.

        Calculate the top (or bottom) K distinct values by count of a column.
        The column can be weighted.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight > 0, then topK is empty.

        Examples
        --------
        For this example, we calculate the top 5 movie genres in a data frame:
        Consider the following frame containing four columns.

        >>> frame.inspect()
            [#]  rank  city         population_2013  population_2010  change  county
            ============================================================================
            [0]     1  Portland              609456           583776  4.40%   Multnomah
            [1]     2  Salem                 160614           154637  3.87%   Marion
            [2]     3  Eugene                159190           156185  1.92%   Lane
            [3]     4  Gresham               109397           105594  3.60%   Multnomah
            [4]     5  Hillsboro              97368            91611  6.28%   Washington
            [5]     6  Beaverton              93542            89803  4.16%   Washington
            [6]    15  Grants Pass            35076            34533  1.57%   Josephine
            [7]    16  Oregon City            34622            31859  8.67%   Clackamas
            [8]    17  McMinnville            33131            32187  2.93%   Yamhill
            [9]    18  Redmond                27427            26215  4.62%   Deschutes
        >>> top_frame = frame.top_k("county", 2)
        [===Job Progress===]
        >>> top_frame.inspect()
            [#]  county      count
                ======================
                [0]  Washington    4.0
                [1]  Clackamas     3.0

















        :param column_name: The column whose top (or bottom) K distinct values are
            to be calculated.
        :type column_name: unicode
        :param k: Number of entries to return (If k is negative, return bottom k).
        :type k: int32
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the topK calculation.
            Must contain numerical data.
            Default is 1 for all items.
        :type weights_column: unicode

        :returns: An object with access to the frame of data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def unflatten_columns(self, columns, delimiter=None):
        """
        Compacts data from multiple rows based on cell data.

        Groups together cells in all columns (less the composite key) using "," as string delimiter.
        The original rows are deleted.
        The grouping takes place based on a composite key created from cell values.
        The column datatypes are changed to string.

        Examples
        --------
        Given a data file::

            user1 1/1/2015 1 70
            user1 1/1/2015 2 60
            user2 1/1/2015 1 65

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("unflatten_column.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c  d
            ===========================
            [0]  user1  1/1/2015  1  70
            [1]  user1  1/1/2015  2  60
            [2]  user2  1/1/2015  1  65


        Unflatten the data using columns a & b:

        .. code::

            >>> frame.unflatten_columns(['a','b'])
            [===Job Progress===]

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c    d
            ================================
            [0]  user2  1/1/2015  1    65
            [1]  user1  1/1/2015  1,2  70,60

        Alternatively, unflatten_columns() also accepts a single column like:


        .. code::

            >>> frame.unflatten_columns('a')
            [===Job Progress===]

            >>> frame.inspect()
            [#]  a      b                  c    d
            =========================================
            [0]  user1  1/1/2015,1/1/2015  1,2  70,60
            [1]  user2  1/1/2015           1    65


        :param columns: Name of the column(s) to be used as keys
            for unflattening.
        :type columns: list
        :param delimiter: (default=None)  Separator for the data in the result columns.
            Default is comma (,).
        :type delimiter: unicode

        :returns: 
        :rtype: _Unit
        """
        return None



@doc_stub
class _DocStubsGraph(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, source=None, name=None):
        """
            Initialize the graph.

        Examples
        --------
        This example uses a single source data frame and creates a graph of 'user'
        and 'movie' vertices connected by 'rating' edges.

        The first step is to bring in some data to create a frame as the source
        for a graph:

        >>> schema = [('viewer', str), ('profile', ta.int32), ('movie', str), ('rating', ta.int32)]
        >>> data1 = [['fred',0,'Croods',5],
        ...          ['fred',0,'Jurassic Park',5],
        ...          ['fred',0,'2001',2],
        ...          ['fred',0,'Ice Age',4],
        ...          ['wilma',0,'Jurassic Park',3],
        ...          ['wilma',0,'2001',5],
        ...          ['wilma',0,'Ice Age',4],
        ...          ['pebbles',1,'Croods',4],
        ...          ['pebbles',1,'Land Before Time',3],
        ...          ['pebbles',1,'Ice Age',5]]
        >>> data2 = [['betty',0,'Croods',5],
        ...          ['betty',0,'Jurassic Park',3],
        ...          ['betty',0,'Land Before Time',4],
        ...          ['betty',0,'Ice Age',3],
        ...          ['barney',0,'Croods',5],
        ...          ['barney',0,'Jurassic Park',5],
        ...          ['barney',0,'Land Before Time',3],
        ...          ['barney',0,'Ice Age',5],
        ...          ['bamm bamm',1,'Croods',5],
        ...          ['bamm bamm',1,'Land Before Time',3]]
        >>> frame = ta.Frame(ta.UploadRows(data1, schema))
        [===Job Progress===]

        >>> frame2 = ta.Frame(ta.UploadRows(data2, schema))
        [===Job Progress===]

        >>> frame.inspect()
        [#]  viewer   profile  movie             rating
        ===============================================
        [0]  fred           0  Croods                 5
        [1]  fred           0  Jurassic Park          5
        [2]  fred           0  2001                   2
        [3]  fred           0  Ice Age                4
        [4]  wilma          0  Jurassic Park          3
        [5]  wilma          0  2001                   5
        [6]  wilma          0  Ice Age                4
        [7]  pebbles        1  Croods                 4
        [8]  pebbles        1  Land Before Time       3
        [9]  pebbles        1  Ice Age                5


        Now, make an empty graph object:

        >>> graph = ta.Graph()

        Then, define the types of vertices and edges this graph will be made of:

        >>> graph.define_vertex_type('viewer')
        [===Job Progress===]
        >>> graph.define_vertex_type('film')
        [===Job Progress===]
        >>> graph.define_edge_type('rating', 'viewer', 'film')
        [===Job Progress===]

        And finally, add the data to the graph:

        >>> graph.vertices['viewer'].add_vertices(frame, 'viewer', ['profile'])
        [===Job Progress===]
        >>> graph.vertices['viewer'].inspect()
        [#]  _vid  _label  viewer   profile
        ===================================
        [0]     1  viewer  fred           0
        [1]     8  viewer  pebbles        1
        [2]     5  viewer  wilma          0

        >>> graph.vertices['film'].add_vertices(frame, 'movie')
        [===Job Progress===]
        >>> graph.vertices['film'].inspect()
        [#]  _vid  _label  movie
        ===================================
        [0]    19  film    Land Before Time
        [1]    14  film    Ice Age
        [2]    12  film    Jurassic Park
        [3]    11  film    Croods
        [4]    13  film    2001

        >>> graph.edges['rating'].add_edges(frame, 'viewer', 'movie', ['rating'])
        [===Job Progress===]
        >>> graph.edges['rating'].inspect()
        [#]  _eid  _src_vid  _dest_vid  _label  rating
        ==============================================
        [0]    24         1         14  rating       4
        [1]    22         1         12  rating       5
        [2]    21         1         11  rating       5
        [3]    23         1         13  rating       2
        [4]    29         8         19  rating       3
        [5]    30         8         14  rating       5
        [6]    28         8         11  rating       4
        [7]    27         5         14  rating       4
        [8]    25         5         12  rating       3
        [9]    26         5         13  rating       5

        Explore basic graph properties:

        >>> graph.vertex_count
        [===Job Progress===]
        8

        >>> graph.vertices
        viewer : [viewer, profile], count = 3
        film : [movie], count = 5

        >>> graph.edge_count
        [===Job Progress===]
        10

        >>> graph.edges
        rating : [rating], count = 10

        >>> graph.status
        u'ACTIVE'

        >>> graph.last_read_date
        datetime.datetime(2016, 6, 2, 20, 59, 28, 464004)

        >>> graph
        Graph <unnamed>
        status = ACTIVE  (last_read_date = -etc-)
        vertices =
          viewer : [viewer, profile], count = 3
          film : [movie], count = 5
        edges =
          rating : [rating], count = 10

        Data from other frames can be added to the graph by making more calls
        to `add_vertices` and `add_edges`.

        >>> frame2 = ta.Frame(ta.CsvFile("/datasets/extra-movie-data.csv", frame.schema))
        [===Job Progress===]

        >>> graph.vertices['viewer'].add_vertices(frame2, 'viewer', ['profile'])
        [===Job Progress===]
        >>> graph.vertices['viewer'].inspect()
        [#]  _vid  _label  viewer     profile
        =====================================
        [0]     5  viewer  wilma            0
        [1]     1  viewer  fred             0
        [2]    31  viewer  betty            0
        [3]    35  viewer  barney           0
        [4]     8  viewer  pebbles          1
        [5]    39  viewer  bamm bamm        1

        >>> graph.vertices['film'].add_vertices(frame2, 'movie')
        [===Job Progress===]
        >>> graph.vertices['film'].inspect()
        [#]  _vid  _label  movie
        ===================================
        [0]    13  film    2001
        [1]    14  film    Ice Age
        [2]    11  film    Croods
        [3]    19  film    Land Before Time
        [4]    12  film    Jurassic Park

        >>> graph.vertex_count
        [===Job Progress===]
        11

        >>> graph.edges['rating'].add_edges(frame2, 'viewer', 'movie', ['rating'])
        [===Job Progress===]

        >>> graph.edges['rating'].inspect(20)
        [##]  _eid  _src_vid  _dest_vid  _label  rating
        ===============================================
        [0]     24         1         14  rating       4
        [1]     22         1         12  rating       5
        [2]     21         1         11  rating       5
        [3]     23         1         13  rating       2
        [4]     29         8         19  rating       3
        [5]     30         8         14  rating       5
        [6]     28         8         11  rating       4
        [7]     27         5         14  rating       4
        [8]     25         5         12  rating       3
        [9]     26         5         13  rating       5
        [10]    60        39         19  rating       3
        [11]    59        39         11  rating       5
        [12]    53        31         19  rating       4
        [13]    54        31         14  rating       3
        [14]    52        31         12  rating       3
        [15]    51        31         11  rating       5
        [16]    57        35         19  rating       3
        [17]    58        35         14  rating       5
        [18]    56        35         12  rating       5
        [19]    55        35         11  rating       5

        >>> graph.edge_count
        [===Job Progress===]
        20

        Now we'll copy the graph and then change it.

        >>> graph2 = graph.copy()
        [===Job Progress===]

        >>> graph2
        Graph <unnamed>
        status = ACTIVE  (last_read_date = -etc-)
        vertices =
          viewer : [viewer, profile], count = 6
          film : [movie], count = 5
        edges =
          rating : [rating], count = 20

        We can rename the columns in the frames representing the vertices and edges,
        similar to regular frame operations.

        >>> graph2.vertices['viewer'].rename_columns({'viewer': 'person'})
        [===Job Progress===]

        >>> graph2.vertices
        viewer : [person, profile], count = 6
        film : [movie], count = 5

        >>> graph2.edges['rating'].rename_columns({'rating': 'score'})
        [===Job Progress===]

        >>> graph2.edges
        rating : [score], count = 20

        We can apply filter and drop functions to the vertex and edge frames.

        >>> graph2.vertices['viewer'].filter(lambda v: v.person.startswith("b"))
        [===Job Progress===]

        >>> graph2.vertices['viewer'].inspect()
        [#]  _vid  _label  person     profile
        =====================================
        [0]    31  viewer  betty            0
        [1]    35  viewer  barney           0
        [2]    39  viewer  bamm bamm        1

        >>> graph2.vertices['viewer'].drop_duplicates("profile")
        [===Job Progress===]

        >>> graph2.vertices['viewer'].inspect()
        [#]  _vid  _label  person     profile
        =====================================
        [0]    31  viewer  betty            0
        [1]    39  viewer  bamm bamm        1

        Now check our edges to see that they have also be filtered.

        >>> graph2.edges['rating'].inspect()
        [#]  _eid  _src_vid  _dest_vid  _label  score
        =============================================
        [0]    60        39         19  rating      3
        [1]    59        39         11  rating      5
        [2]    53        31         19  rating      4
        [3]    54        31         14  rating      3
        [4]    52        31         12  rating      3
        [5]    51        31         11  rating      5

        Only source vertices 31 and 39 remain.

        Drop row for the movie 'Croods' (vid 41) from the film VertexFrame.

        >>> graph2.vertices['film'].inspect()
        [#]  _vid  _label  movie
        ===================================
        [0]    13  film    2001
        [1]    14  film    Ice Age
        [2]    11  film    Croods
        [3]    19  film    Land Before Time
        [4]    12  film    Jurassic Park

        >>> graph2.vertices['film'].drop_rows(lambda row: row.movie=='Croods')
        [===Job Progress===]

        >>> graph2.vertices['film'].inspect()
        [#]  _vid  _label  movie
        ===================================
        [0]    13  film    2001
        [1]    14  film    Ice Age
        [2]    19  film    Land Before Time
        [3]    12  film    Jurassic Park

        Dangling edges (edges that correspond to the movie 'Croods', vid 41) were also removed:

        >>> graph2.edges['rating'].inspect()
        [#]  _eid  _src_vid  _dest_vid  _label  score
        =============================================
        [0]    52        31         12  rating      3
        [1]    54        31         14  rating      3
        [2]    60        39         19  rating      3
        [3]    53        31         19  rating      4


            

        :param source: (default=None)  A source of initial data.
        :type source: OrientDBGraph | None
        :param name: (default=None)  Name for the new graph.
            Default is None.
        :type name: str
        """
        raise DocStubCalledError("graph:/__init__")


    @doc_stub
    def annotate_degrees(self, output_property_name, degree_option=None, input_edge_labels=None):
        """
        Make new graph with degrees.

        Creates a new graph which is the same as the input graph, with the addition
        that every vertex of the graph has its degree stored in a user-specified property.

        **Degree Calculation**

        A fundamental quantity in graph analysis is the degree of a vertex:
        The degree of a vertex is the number of edges adjacent to it.

        For a directed edge relation, a vertex has both an out-degree (the number of
        edges leaving the vertex) and an in-degree (the number of edges entering the
        vertex).

        The |PACKAGE| routine ``annotate_degrees`` can be executed at distributed scale.

        In the presence of edge weights, vertices can have weighted degrees: The
        weighted degree of a vertex is the sum of weights of edges adjacent to it.
        Analogously, the weighted in-degree of a vertex is the sum of the weights of
        the edges entering it, and the weighted out-degree is the sum
        of the weights of the edges leaving the vertex.

        The toolkit provides :ref:`annotate_weighted_degrees <python_api/graphs/graph-/annotate_weighted_degrees>`
        for the distributed calculation of weighted vertex degrees.

        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.annotate_degrees("outEdgesCount",degree_option="out")
        [===Job Progress===]
        >>> result['source'].inspect()
        [#]  _vid  _label  source  label  outEdgesCount
        ===============================================
        [0]     1  source       1    1.0              3
        [1]     2  source       2    1.0              2
        [2]     3  source       3    5.0              2
        [3]     4  source       4    5.0              2
        [4]     5  source       5    5.0              1
        >>> result = graph.annotate_degrees("inEdgesCount",degree_option="in")
        [===Job Progress===]
        >>> result['source'].inspect()
        [#]  _vid  _label  source  label  inEdgesCount
        ==============================================
        [0]     1  source       1    1.0             3
        [1]     2  source       2    1.0             2
        [2]     3  source       3    5.0             2
        [3]     4  source       4    5.0             2
        [4]     5  source       5    5.0             1


        :param output_property_name: The name of the new property.
            The degree is stored in this property.
        :type output_property_name: unicode
        :param degree_option: (default=None)  Indicator for the definition of degree to be used for the
            calculation.
            Permitted values:

            *   "out" (default value) : Degree is calculated as the out-degree.
            *   "in" : Degree is calculated as the in-degree.
            *   "undirected" : Degree is calculated as the undirected degree.
                (Assumes that the edges are all undirected.)
               
            Any prefix of the strings "out", "in", "undirected" will select the
            corresponding option.
        :type degree_option: unicode
        :param input_edge_labels: (default=None)  If this list is provided, only edges whose labels are
            included in the given set will be considered in the degree calculation.
            In the default situation (when no list is provided), all edges will be used
            in the degree calculation, regardless of label.
        :type input_edge_labels: list

        :returns: Dictionary containing the vertex type as the key and the corresponding
            vertex's frame with a column storing the annotated degree for the vertex
            in a user specified property.
            Call dictionary_name['vertex type'] to get the handle to frame of that 'vertex type' 
        :rtype: dict
        """
        return None


    @doc_stub
    def annotate_weighted_degrees(self, output_property_name, degree_option=None, input_edge_labels=None, edge_weight_property=None, edge_weight_default=None):
        """
        Calculates the weighted degree of each vertex with respect to an (optional) set of labels.

        Pulls graph from underlying store, calculates weighted degrees and writes them into the property
        specified, and then writes the output graph to the underlying store.

        **Degree Calculation**

        A fundamental quantity in graph analysis is the degree of a vertex:
        The degree of a vertex is the number of edges adjacent to it.

        For a directed edge relation, a vertex has both an out-degree (the number of
        edges leaving the vertex) and an in-degree (the number of edges entering the
        vertex).

        The toolkit provides a routine :ref:`annotate_degrees
        <python_api/graphs/graph-/annotate_weighted_degrees>`
        for calculating the degrees of vertices.
        The |PACKAGE| routine ``annotate_degrees`` can be executed at distributed scale.

        In the presence of edge weights, vertices can have weighted degrees: The
        weighted degree of a vertex is the sum of weights of edges adjacent to it.
        Analogously, the weighted in-degree of a vertex is the sum of the weights of
        the edges entering it, and the weighted out-degree is the sum
        of the weights of the edges leaving the vertex.

        The toolkit provides this routine for the distributed calculation of weighted
        vertex degrees.

        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.annotate_weighted_degrees("outEdgesCount",edge_weight_property="weight", degree_option="out")
        [===Job Progress===]
        >>> result['source'].inspect()
        [#]  _vid  _label  source  label  outEdgesCount
        ===============================================
        [0]     1  source       1    1.0            3.0
        [1]     2  source       2    1.0            2.0
        [2]     3  source       3    5.0            2.0
        [3]     4  source       4    5.0            2.0
        [4]     5  source       5    5.0            1.0
        >>> result = graph.annotate_weighted_degrees("inEdgesCount",edge_weight_property="weight", degree_option="in")
        [===Job Progress===]
        >>> result['source'].inspect()
        [#]  _vid  _label  source  label  inEdgesCount
        ==============================================
        [0]     1  source       1    1.0           3.0
        [1]     2  source       2    1.0           2.0
        [2]     3  source       3    5.0           2.0
        [3]     4  source       4    5.0           2.0
        [4]     5  source       5    5.0           1.0

        :param output_property_name: property name of where to store output
        :type output_property_name: unicode
        :param degree_option: (default=None)  choose from 'out', 'in', 'undirected'
        :type degree_option: unicode
        :param input_edge_labels: (default=None)  labels of edge types that should be included
        :type input_edge_labels: list
        :param edge_weight_property: (default=None)  property name of edge weight, if not provided all edges are weighted equally
        :type edge_weight_property: unicode
        :param edge_weight_default: (default=None)  default edge weight
        :type edge_weight_default: float64

        :returns: Dictionary containing the vertex type as the key and the corresponding
            vertex's frame with a column storing the annotated weighted degree for the vertex
            in a user specified property.
            Call dictionary_name['vertex type'] to get the handle to frame of that 'vertex type' 
        :rtype: dict
        """
        return None


    @doc_stub
    def clustering_coefficient(self, output_property_name=None, input_edge_labels=None):
        """
        Coefficient of graph with respect to labels.

        Calculates the clustering coefficient of the graph with respect to an (optional) set of labels.

        Pulls graph from underlying store, calculates degrees and writes them into the property specified,
        and then writes the output graph to the underlying store.

        .. warning::

            THIS FUNCTION IS FOR UNDIRECTED GRAPHS.
            If it is called on a directed graph, its output is NOT guaranteed to calculate
            the local directed clustering coefficients.

        |
        **Clustering Coefficients**

        The clustering coefficient of a graph provides a measure of how tightly
        clustered an undirected graph is.
        Informally, if the edge relation denotes "friendship", the clustering
        coefficient of the graph is the probability that two people are friends given
        that they share a common friend.

        More formally:

        .. math::

            cc(G)  = \frac{ \| \{ (u,v,w) \in V^3: \ \{u,v\}, \{u, w\}, \{v,w \} \in \
            E \} \| }{\| \{ (u,v,w) \in V^3: \ \{u,v\}, \{u, w\} \in E \} \|}


        Analogously, the clustering coefficient of a vertex provides a measure of how
        tightly clustered that vertex's neighborhood is.
        Informally, if the edge relation denotes "friendship", the clustering
        coefficient at a vertex :math:`v` is the probability that two acquaintances of
        :math:`v` are themselves friends.

        More formally:

        .. math::

            cc(v)  = \frac{ \| \{ (u,v,w) \in V^3: \ \{u,v\}, \{u, w\}, \{v,w \} \in \
            E \} \| }{\| \{ (u,v,w) \in V^3: \ \{v, u \}, \{v, w\} \in E \} \|}


        The toolkit provides the function clustering_coefficient which computes both
        local and global clustering coefficients for a given undirected graph.

        For more details on the mathematics and applications of clustering
        coefficients, see http://en.wikipedia.org/wiki/Clustering_coefficient.



        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> results = graph.clustering_coefficient('ccgraph')
        [===Job Progress===]
        >>> results.global_clustering_coefficient
        0.5
        >>> results.frame.inspect()
        [#]  _label  source  label  ccgraph
        ==========================================
        [0]  source       5    5.0             0.0
        [1]  source       1    1.0  0.333333333333
        [2]  source       2    1.0             1.0
        [3]  source       3    5.0             1.0
        [4]  source       4    5.0             0.0


        :param output_property_name: (default=None)  The name of the new property to which each
            vertex's local clustering coefficient will be written.
            If this option is not specified, no output frame will be produced and only
            the global clustering coefficient will be returned.
        :type output_property_name: unicode
        :param input_edge_labels: (default=None)  If this list is provided,
            only edges whose labels are included in the given
            set will be considered in the clustering coefficient calculation.
            In the default situation (when no list is provided), all edges will be used
            in the calculation, regardless of label.
            It is required that all edges that enter into the clustering coefficient
            analysis be undirected.
        :type input_edge_labels: list

        :returns: Dictionary of the global clustering coefficient of the graph or,
            if local clustering coefficients are requested, a reference to the frame with local
            clustering coefficients stored at properties at each vertex.
        :rtype: dict
        """
        return None


    @doc_stub
    def copy(self, name=None):
        """
        Make a copy of the current graph.

        >>> copied_graph = graph.copy('my_graph2')  # create a copy named 'my_graph2'

        See also usage in
        the :doc:`graph construction examples <../../graphs/graph-/__init__>`.


        :param name: (default=None)  The name for the copy of the graph.
            Default is None.
        :type name: unicode

        :returns: A copy of the original graph.
        :rtype: dict
        """
        return None


    @doc_stub
    def define_edge_type(self, label, src_vertex_label, dest_vertex_label, directed=False):
        """
        Define an edge type.

        See :doc:`here <../../graphs/graph-/__init__>` for example usage in
        graph construction.

        :param label: Label of the edge type.
        :type label: unicode
        :param src_vertex_label: The source "type" of vertices this edge
            connects.
        :type src_vertex_label: unicode
        :param dest_vertex_label: The destination "type" of vertices this
            edge connects.
        :type dest_vertex_label: unicode
        :param directed: (default=False)  True if edges are directed,
            false if they are undirected.
        :type directed: bool

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def define_vertex_type(self, label):
        """
        Define a vertex type by label.

        See :doc:`here <../../graphs/graph-/__init__>` for example usage in
        graph construction.

        :param label: Label of the vertex type.
        :type label: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @property
    @doc_stub
    def edge_count(self):
        """
        Get the total number of edges in the graph.

        Examples
        --------
        See :doc:`here <__init__>` for example usage in graph construction.




        :returns: Total number of edges in the graph
        :rtype: int
        """
        return None


    @property
    @doc_stub
    def edges(self):
        """
        Edge frame collection

        Acts like a dictionary where the edge type is the key, returning the particular EdgeFrame

        Examples
        --------
        See :doc:`here <__init__>` for example usage in graph construction.



        """
        return None


    @doc_stub
    def export_to_orientdb(self, graph_name, batch_size=1000):
        """
        Exports graph to OrientDB

        Creates OrientDB database using the parameters provided in the configurations file.

              OrientDB database will be created in the given host name and port number,
              and with the given user credentials after checking the user authorization to create or access OrientDB database.

              Exports the graph edges and vertices to the OrientDB database. Each vertex or edge type in the graph corresponds to a vertex or edge class in OrientDB.

        :param graph_name: OrientDB database name.
        :type graph_name: unicode
        :param batch_size: (default=1000)  batch size for commiting transactions.
        :type batch_size: int32

        :returns: The location to the OrientDB database file "URI", in addition to dictionary for the exported vertices and edges.
                  for vertices dictionary:
                         it returns the vertex class name, the number of the exported vertices and the number of vertices failed to be exported.
                  for the edges dictionary:
                         it returns the edge class name, the number of the exported edges and the number of edges that failed to be exported.
        :rtype: dict
        """
        return None


    @doc_stub
    def graphx_connected_components(self, output_vertex_property_name='connectedComponentId'):
        """
        Implements the connected components computation on a graph by invoking graphx api.

        Pulls graph from underlying store, sends it off to the ConnectedComponentGraphXDefault,
        and then writes the output graph back to the underlying store.

        |
        **Connected Components (CC)**

        Connected components are disjoint subgraphs in which all vertices are
        connected to all other vertices in the same component via paths, but not
        connected via paths to vertices in any other component.
        The connected components algorithm uses message passing along a specified edge
        type to find all of the connected components of a graph and label each edge
        with the identity of the component to which it belongs.
        The algorithm is specific to an edge type, hence in graphs with several
        different types of edges, there may be multiple, overlapping sets of connected
        components.

        The algorithm works by assigning each vertex a unique numerical index and
        passing messages between neighbors.
        Vertices pass their indices back and forth with their neighbors and update
        their own index as the minimum of their current index and all other indices
        received.
        This algorithm continues until there is no change in any of the vertex
        indices.
        At the end of the algorithm, the unique levels of the indices denote the
        distinct connected components.
        The complexity of the algorithm is proportional to the diameter of the graph.


        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.graphx_connected_components()
        [===Job Progress===]
        >>> result['source'].inspect()
            [#]  _vid  _label  source  label  connectedComponentId
            ======================================================
            [0]     5  source       5    5.0                     1
            [1]     1  source       1    1.0                     1
            [2]     2  source       2    1.0                     1
            [3]     3  source       3    5.0                     1
            [4]     4  source       4    5.0                     1

        >>> graph.edges['edges'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  weight
            ==============================================
            [0]     6         1          2  edges        1
            [1]     7         1          3  edges        1
            [2]     9         1          4  edges        1
            [3]     8         2          3  edges        1
            [4]    10         4          5  edges        1


        :param output_vertex_property_name: (default=connectedComponentId)  The name of the column containing the connected component value.
        :type output_vertex_property_name: unicode

        :returns: Dictionary containing the vertex type as the key and the corresponding
              vertex's frame with a connected component column.
              Call dictionary_name['label'] to get the handle to frame whose vertex type is label.
        :rtype: dict
        """
        return None


    @doc_stub
    def graphx_label_propagation(self, max_steps=10, output_vertex_property_name='propagatedLabel'):
        """
        Implements the label propagation computation on a graph by invoking graphx api.

        For detailed information on the algorithm, please see: http://arxiv.org/abs/0709.2938

        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.graphx_label_propagation()
        [===Job Progress===]
        >>> result['source'].inspect()
            [#]  _vid  _label  source  label  propagatedLabel
            =================================================
            [0]     5  source       5    5.0                5
            [1]     1  source       1    1.0                1
            [2]     2  source       2    1.0                2
            [3]     3  source       3    5.0                2
            [4]     4  source       4    5.0                4

        >>> graph.edges['edges'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  weight
            ==============================================
            [0]     6         1          2  edges        1
            [1]     7         1          3  edges        1
            [2]     9         1          4  edges        1
            [3]     8         2          3  edges        1
            [4]    10         4          5  edges        1


        :param max_steps: (default=10)  Number of super-steps before the algorithm terminates. Default = 10
        :type max_steps: int32
        :param output_vertex_property_name: (default=propagatedLabel)  The name of the column containing the propagated label value.
        :type output_vertex_property_name: unicode

        :returns: The original graph with the additional label for each vertex
        :rtype: dict
        """
        return None


    @doc_stub
    def graphx_pagerank(self, output_property, input_edge_labels=None, max_iterations=None, reset_probability=None, convergence_tolerance=None):
        """
        Determine which vertices are the most important.

        Pulls graph from underlying store, sends it off to the
        PageRankRunner, and then writes the output graph back to the underlying store.

        ** Experimental Feature **

        **Basics and Background**

        *PageRank* is a method for determining which vertices in a directed graph are
        the most central or important.
        *PageRank* gives each vertex a score which can be interpreted as the
        probability that a person randomly walking along the edges of the graph will
        visit that vertex.

        The calculation of *PageRank* is based on the supposition that if a vertex has
        many vertices pointing to it, then it is "important",
        and that a vertex grows in importance as more important vertices point to it.
        The calculation is based only on the network structure of the graph and makes
        no use of any side data, properties, user-provided scores or similar
        non-topological information.

        *PageRank* was most famously used as the core of the Google search engine for
        many years, but as a general measure of centrality in a graph, it has
        other uses to other problems, such as recommendation systems and
        analyzing predator-prey food webs to predict extinctions.

        **Background references**

        *   Basic description and principles: `Wikipedia\: PageRank`_
        *   Applications to food web analysis: `Stanford\: Applications of PageRank`_
        *   Applications to recommendation systems: `PLoS\: Computational Biology`_

        **Mathematical Details of PageRank Implementation**

        The |PACKAGE| implementation of *PageRank* satisfies the following equation
        at each vertex :math:`v` of the graph:

        .. math::

            PR(v) = \frac {\rho}{n} + \rho \left( \sum_{u\in InSet(v)} \
            \frac {PR(u)}{L(u)} \right)

        Where:
            |   :math:`v` |EM| a vertex
            |   :math:`L(v)` |EM| outbound degree of the vertex v
            |   :math:`PR(v)` |EM| *PageRank* score of the vertex v
            |   :math:`InSet(v)` |EM| set of vertices pointing to the vertex v
            |   :math:`n` |EM| total number of vertices in the graph
            |   :math:`\rho` |EM| user specified damping factor (also known as reset
                probability)

        Termination is guaranteed by two mechanisms.

        *   The user can specify a convergence threshold so that the algorithm will
            terminate when, at every vertex, the difference between successive
            approximations to the *PageRank* score falls below the convergence
            threshold.
        *   The user can specify a maximum number of iterations after which the
            algorithm will terminate.

        .. _Wikipedia\: PageRank: http://en.wikipedia.org/wiki/PageRank
        .. _Stanford\: Applications of PageRank: http://web.stanford.edu/class/msande233/handouts/lecture8.pdf
        .. _PLoS\: Computational Biology:
            http://www.ploscompbiol.org/article/fetchObject.action?uri=info%3Adoi%2F10.1371%2Fjournal.pcbi.1000494&representation=PDF

        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.graphx_pagerank(output_property="PageRank",max_iterations=2,convergence_tolerance=0.001)
        [===Job Progress===]
        >>> graph.edges['edges'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  weight
            ==============================================
            [0]     6         1          2  edges        1
            [1]     7         1          3  edges        1
            [2]     9         1          4  edges        1
            [3]     8         2          3  edges        1
            [4]    10         4          5  edges        1
        >>> result['edge_dictionary']['edges'].row_count
        10
        >>> result['vertex_dictionary']['source'].row_count
        5


        :param output_property: Name of the property to which PageRank
            value will be stored on vertex and edge.
        :type output_property: unicode
        :param input_edge_labels: (default=None)  List of edge labels to consider for PageRank computation.
            Default is all edges are considered.
        :type input_edge_labels: list
        :param max_iterations: (default=None)  The maximum number of iterations that will be invoked.
            The valid range is all positive int.
            Invalid value will terminate with vertex page rank set to reset_probability.
            Default is 20.
        :type max_iterations: int32
        :param reset_probability: (default=None)  The probability that the random walk of a page is reset.
            Default is 0.15.
        :type reset_probability: float64
        :param convergence_tolerance: (default=None)  The amount of change in cost function that will be tolerated at
            convergence.
            If this parameter is specified, max_iterations is not considered as a stopping condition.
            If the change is less than this threshold, the algorithm exits earlier.
            The valid value range is all float and zero.
            Default is 0.001.
        :type convergence_tolerance: float64

        :returns: dict((vertex_dictionary, (label, Frame)), (edge_dictionary,(label,Frame))).

            Dictionary containing dictionaries of labeled vertices and labeled edges.

            For the *vertex_dictionary* the vertex type is the key and the corresponding
            vertex's frame with a new column storing the page rank value for the vertex.
            Call vertex_dictionary['label'] to get the handle to frame whose vertex
            type is label.

            For the *edge_dictionary* the edge type is the key and the corresponding
            edge's frame with a new column storing the page rank value for the edge.
            Call edge_dictionary['label'] to get the handle to frame whose edge type
            is label.
        :rtype: dict
        """
        return None


    @doc_stub
    def graphx_triangle_count(self, output_property, input_edge_labels=None):
        """
        Number of triangles among vertices of current graph.

        ** Experimental Feature **

        Counts the number of triangles among vertices in an undirected graph.
        If an edge is marked bidirectional, the implementation opts for canonical
        orientation of edges hence counting it only once (similar to an
        undirected graph).

        >>> graph = ta.Graph()

        >>> graph.define_vertex_type('source')
        [===Job Progress===]
        >>> graph.vertices['source'].add_vertices(vertex_frame, 'source', 'label')
        [===Job Progress===]
        >>> graph.define_edge_type('edges','source', 'source', directed=False)
        [===Job Progress===]
        >>> graph.edges['edges'].add_edges(edge_frame, 'source', 'dest', ['weight'])
        [===Job Progress===]
        >>> result = graph.graphx_triangle_count(output_property = "triangle_count")
        [===Job Progress===]
        >>> result['source'].inspect()
            [#]  _vid  _label  source  label  triangle_count
            ================================================
            [0]     5  source       5    5.0               0
            [1]     1  source       1    1.0               1
            [2]     2  source       2    1.0               1
            [3]     3  source       3    5.0               1
            [4]     4  source       4    5.0               0

        >>> graph.edges['edges'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  weight
            ==============================================
            [0]     6         1          2  edges        1
            [1]     7         1          3  edges        1
            [2]     9         1          4  edges        1
            [3]     8         2          3  edges        1
            [4]    10         4          5  edges        1




        :param output_property: The name of output property to be
            added to vertex/edge upon completion.
        :type output_property: unicode
        :param input_edge_labels: (default=None)  The name of edge labels to be considered for triangle count.
            Default is all edges are considered.
        :type input_edge_labels: list

        :returns: dict(label, Frame).

            Dictionary containing the vertex type as the key and the corresponding
            vertex's frame with a triangle_count column.
            Call dictionary_name['label'] to get the handle to frame whose vertex
            type is label.
        :rtype: dict
        """
        return None


    @doc_stub
    def kclique_percolation(self, clique_size, community_property_label):
        """
        Find groups of vertices with similar attributes.

        **Community Detection Using the K-Clique Percolation Algorithm**

        **Overview**

        Modeling data as a graph captures relations, for example, friendship ties
        between social network users or chemical interactions between proteins.
        Analyzing the structure of the graph reveals collections (often termed
        'communities') of vertices that are more likely to interact amongst each
        other.
        Examples could include a community of friends in a social network or a
        collection of highly interacting proteins in a cellular process.

        |PACKAGE| provides community detection using the k-Clique
        percolation method first proposed by Palla et. al. [1]_ that has been widely
        used in many contexts.

        **K-Clique Percolation**

        K-clique percolation is a method for detecting community structure in graphs.
        Here we provide mathematical background on how communities are defined in the
        context of the k-clique percolation algorithm.

        A clique is a group of vertices in which every vertex is connected (via
        undirected edge) with every other vertex in the clique.
        This graphically looks like a triangle or a structure composed of triangles:

        .. image:: /k-clique_201508281155.*

        A clique is certainly a community in the sense that its vertices are all
        connected, but, it is too restrictive for most purposes,
        since it is natural some members of a community may not interact.

        Mathematically, a k-clique has :math:`k` vertices, each with :math:`k - 1`
        common edges, each of which connects to another vertex in the k-clique.
        The k-clique percolation method forms communities by taking unions of k-cliques
        that have :math:`k - 1` vertices in common.

        **K-Clique Example**

        In the graph below, the cliques are the sections defined by their triangular
        appearance and the 3-clique communities are {1, 2, 3, 4} and {4, 5, 6, 7, 8}.
        The vertices 9, 10, 11, 12 are not in 3-cliques, therefore they do not belong
        to any community.
        Vertex 4 belongs to two distinct (but overlapping) communities.

        .. image:: /ds_mlal_a1.png

        **Distributed Implementation of K-Clique Community Detection**

        The implementation of k-clique community detection in |PACKAGE| is a fully
        distributed implementation that follows the map-reduce
        algorithm proposed in Varamesh et. al. [2]_ .

        It has the following steps:

        #.  All k-cliques are enumerated <enumerate>.
        #.  k-cliques are used to build a "clique graph" by declaring each k-clique to
            be a vertex in a new graph and placing edges between k-cliques that share
            k-1 vertices in the base graph.
        #.  A connected component analysis is performed on the clique graph.
            Connected components of the clique graph correspond to k-clique communities
            in the base graph.
        #.  The connected components information for the clique graph is projected back
            down to the base graph, providing each vertex with the set of k-clique
            communities to which it belongs.

        Notes
        -----
        Spawns a number of Spark jobs that cannot be calculated before execution
        (it is bounded by the diameter of the clique graph derived from the input graph).
        For this reason, the initial loading, clique enumeration and clique-graph
        construction steps are tracked with a single progress bar (this is most of
        the time), and then successive iterations of analysis of the clique graph
        are tracked with many short-lived progress bars, and then finally the
        result is written out.


        .. rubric:: Footnotes

        .. [1]
            G. Palla, I. Derenyi, I. Farkas, and T. Vicsek. Uncovering the overlapping
            community structure of complex networks in nature and society.
            Nature, 435:814, 2005 ( See http://hal.elte.hu/cfinder/wiki/papers/communitylettm.pdf )

        .. [2]
            Varamesh, A.; Akbari, M.K.; Fereiduni, M.; Sharifian, S.; Bagheri, A.,
            "Distributed Clique Percolation based community detection on social
            networks using MapReduce,"
            Information and Knowledge Technology (IKT), 2013 5th Conference on, vol.,
            no., pp.478,483, 28-30 May 2013


        :param clique_size: The sizes of the cliques used to form communities.
            Larger values of clique size result in fewer, smaller communities that are more connected.
            Must be at least 2.
        :type clique_size: int32
        :param community_property_label: Name of the community property of vertex that will be updated/created in the graph.
            This property will contain for each vertex the set of communities that contain that
            vertex.
        :type community_property_label: unicode

        :returns: Dictionary of vertex label and frame, Execution time.
        :rtype: dict
        """
        return None


    @doc_stub
    def label_propagation(self, prior_property, posterior_property, state_space_size, edge_weight_property='', convergence_threshold=0.0, max_iterations=20, was_labeled_property_name=None, alpha=None):
        """
        Classification on sparse data using Belief Propagation.

        Belief propagation by the sum-product algorithm.
         This algorithm analyzes a graphical model with prior beliefs using sum product message passing.
         The priors are read from a property in the graph, the posteriors are written to another property in the graph.
         This is the GraphX-based implementation of belief propagation.

         See :ref:`Loopy Belief Propagation <python_api/frames/frame-/loopy_belief_propagation>`
         for a more in-depth discussion of |BP| and |LBP|.

        :param prior_property: Name of the vertex property which contains the prior belief for the vertex.
        :type prior_property: unicode
        :param posterior_property: Name of the vertex property which will contain the posterior belief for each vertex.
        :type posterior_property: unicode
        :param state_space_size: Number of features
        :type state_space_size: int32
        :param edge_weight_property: (default=)  Name of the edge property that contains the edge weight for each edge.
        :type edge_weight_property: unicode
        :param convergence_threshold: (default=0.0)  Belief propagation will terminate when the average change in posterior beliefs between supersteps is less than or equal to this threshold.
        :type convergence_threshold: float64
        :param max_iterations: (default=20)  The maximum number of supersteps that the algorithm will execute.The valid range is all positive int.
        :type max_iterations: int32
        :param was_labeled_property_name: (default=None)  (LP only) - Represents the column/property name for the was labeled field
        :type was_labeled_property_name: unicode
        :param alpha: (default=None)  (LP only) - Represents the tradeoff parameter that controls how much influence an external classifier's prediction contributes to the final prediction.
            This is for the case where an external classifier is available that can produce initial probabilistic classification on unlabeled examples, and
            the option allows incorporating external classifier's prediction into the LP training process.The valid value range is [0.0,1.0].Default is 0.1
        :type alpha: float32

        :returns: Progress report for belief propagation in the format of a multiple-line string.
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this frame's data was accessed.



        :returns: Date string of the last time this frame's data was accessed
        :rtype: str
        """
        return None


    @doc_stub
    def loopy_belief_propagation(self, prior_property, posterior_property, state_space_size, edge_weight_property='', convergence_threshold=0.0, max_iterations=20, was_labeled_property_name=None, alpha=None):
        """
        Classification on sparse data using Belief Propagation.

        Belief propagation by the sum-product algorithm.
        This algorithm analyzes a graphical model with prior beliefs using sum product message passing.
        The priors are read from a property in the graph, the posteriors are written to another property in the graph.
        This is the GraphX-based implementation of belief propagation.

        See :ref:`Loopy Belief Propagation <python_api/frames/frame-/loopy_belief_propagation>`
        for a more in-depth discussion of |BP| and |LBP|.

        :param prior_property: Name of the vertex property which contains the prior belief for the vertex.
        :type prior_property: unicode
        :param posterior_property: Name of the vertex property which will contain the posterior belief for each vertex.
        :type posterior_property: unicode
        :param state_space_size: Number of features
        :type state_space_size: int32
        :param edge_weight_property: (default=)  Name of the edge property that contains the edge weight for each edge.
        :type edge_weight_property: unicode
        :param convergence_threshold: (default=0.0)  Belief propagation will terminate when the average change in posterior beliefs between supersteps is less than or equal to this threshold.
        :type convergence_threshold: float64
        :param max_iterations: (default=20)  The maximum number of supersteps that the algorithm will execute.The valid range is all positive int.
        :type max_iterations: int32
        :param was_labeled_property_name: (default=None)  (LP only) - Represents the column/property name for the was labeled field
        :type was_labeled_property_name: unicode
        :param alpha: (default=None)  (LP only) - Represents the tradeoff parameter that controls how much influence an external classifier's prediction contributes to the final prediction.
            This is for the case where an external classifier is available that can produce initial probabilistic classification on unlabeled examples, and
            the option allows incorporating external classifier's prediction into the LP training process.The valid value range is [0.0,1.0].Default is 0.1
        :type alpha: float32

        :returns: Progress report for belief propagation in the format of a multiple-line string.
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the graph object.

        Change or retrieve graph object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_graph.name
            "abc"

            >>> my_graph.name = "xyz"
            >>> my_graph.name
            "xyz"




        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current graph life cycle status.

        One of three statuses: Active, Dropped, Finalized
        -   Active:    Entity is available for use
        -   Dropped:   Entity has been dropped by user or by garbage collection which found it stale
        -   Finalized: Entity's data has been deleted




        :returns: Status of the graph.
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def vertex_count(self):
        """
        Get the total number of vertices in the graph.

        Returns
        -------
        int32
            The number of vertices in the graph.


        Examples
        --------
        See :doc:`here <__init__>` for example usage in graph construction.



        """
        return None


    @property
    @doc_stub
    def vertices(self):
        """
        Vertex frame collection

        Acts like a dictionary where the vertex type is the key, returning the particular VertexFrame

        Examples
        --------
        See :doc:`here <__init__>` for example usage in graph construction.



        """
        return None



@doc_stub
class _DocStubsVertexFrame(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, source=None, graph=None, label=None):
        """
            Examples

        --------
        Given a data file, create a frame, move the data to graph and then define a
        new VertexFrame and add data to it:

        .. only:: html

            .. code::

                >>> csv = ta.CsvFile("/movie.csv", schema= [('user_id', int32), ('user_name', str), ('movie_id', int32), ('movie_title', str), ('rating', str)])
                >>> my_frame = ta.Frame(csv)
                >>> my_graph = ta.Graph()
                >>> my_graph.define_vertex_type('users')
                >>> my_vertex_frame = my_graph.vertices['users']
                >>> my_vertex_frame.add_vertices(my_frame, 'user_id', ['user_name', 'age'])

        .. only:: html

            .. code::

                >>> csv = ta.CsvFile("/movie.csv", schema= [('user_id', int32),
                ...                                     ('user_name', str),
                ...                                     ('movie_id', int32),
                ...                                     ('movie_title', str),
                ...                                     ('rating', str)])
                >>> my_frame = ta.Frame(csv)
                >>> my_graph = ta.Graph()
                >>> my_graph.define_vertex_type('users')
                >>> my_vertex_frame = my_graph.vertices['users']
                >>> my_vertex_frame.add_vertices(my_frame, 'user_id',
                ... ['user_name', 'age'])

        Retrieve a previously defined graph and retrieve a VertexFrame from it:

        .. code::

            >>> my_graph = ta.get_graph("your_graph")
            >>> my_vertex_frame = my_graph.vertices["your_label"]

        Calling methods on a VertexFrame:

        .. code::

            >>> my_vertex_frame.vertices["your_label"].inspect(20)

        Convert a VertexFrame to a frame:

        .. code::

            >>> new_Frame = my_vertex_frame.vertices["label"].copy()
            

        :param source: (default=None)  
        :type source: 
        :param graph: (default=None)  
        :type graph: 
        :param label: (default=None)  
        :type label: 
        """
        raise DocStubCalledError("frame:vertex/__init__")


    @doc_stub
    def add_columns(self, func, schema, columns_accessed=None):
        """
        Add columns to current frame.

        Assigns data to column based on evaluating a function for each row.

        Notes
        -----
        1)  The row |UDF| ('func') must return a value in the same format as
            specified by the schema.
            See :doc:`/ds_apir`.
        2)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!

        Examples
        --------
        Given our frame, let's add a column which has how many years the person has been over 18

        .. code::


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183

            >>> frame.add_columns(lambda row: row.age - 18, ('adult_years', ta.int32))
            [===Job Progress===]

            >>> frame.inspect()
            [#]  name      age  tenure  phone     adult_years
            =================================================
            [0]  Fred       39      16  555-1234           21
            [1]  Susan      33       3  555-0202           15
            [2]  Thurston   65      26  555-4510           47
            [3]  Judy       44      14  555-2183           26


        Multiple columns can be added at the same time.  Let's add percentage of
        life and percentage of adult life in one call, which is more efficient.

        .. code::

            >>> frame.add_columns(lambda row: [row.tenure / float(row.age), row.tenure / float(row.adult_years)], [("of_age", ta.float32), ("of_adult", ta.float32)])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54

        Note that the function returns a list, and therefore the schema also needs to be a list.

        It is not necessary to use lambda syntax, any function will do, as long as it takes a single row argument.  We
        can also call other local functions within.

        Let's add a column which shows the amount of person's name based on their adult tenure percentage.

            >>> def percentage_of_string(string, percentage):
            ...     '''returns a substring of the given string according to the given percentage'''
            ...     substring_len = int(percentage * len(string))
            ...     return string[:substring_len]

            >>> def add_name_by_adult_tenure(row):
            ...     return percentage_of_string(row.name, row.of_adult)

            >>> frame.add_columns(add_name_by_adult_tenure, ('tenured_name', unicode))
            [===Job Progress===]

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame.inspect(columns=['name', 'of_adult', 'tenured_name'], round=2)
            [#]  name      of_adult  tenured_name
            =====================================
            [0]  Fred          0.76  Fre
            [1]  Susan         0.20  S
            [2]  Thurston      0.55  Thur
            [3]  Judy          0.54  Ju


        **Optimization** - If we know up front which columns our row function will access, we
        can tell add_columns to speed up the execution by working on only the limited feature
        set rather than the entire row.

        Let's add a name based on tenure percentage of age.  We know we're only going to use
        columns 'name' and 'of_age'.

        .. code::

            >>> frame.add_columns(lambda row: percentage_of_string(row.name, row.of_age),
            ...                   ('tenured_name_age', unicode),
            ...                   columns_accessed=['name', 'of_age'])
            [===Job Progress===]
            >>> frame.inspect(round=2)
            [#]  name      age  tenure  phone     adult_years  of_age  of_adult
            ===================================================================
            [0]  Fred       39      16  555-1234           21    0.41      0.76
            [1]  Susan      33       3  555-0202           15    0.09      0.20
            [2]  Thurston   65      26  555-4510           47    0.40      0.55
            [3]  Judy       44      14  555-2183           26    0.32      0.54
            <BLANKLINE>
            [#]  tenured_name  tenured_name_age
            ===================================
            [0]  Fre           F
            [1]  S
            [2]  Thur          Thu
            [3]  Ju            J

        More information on a row |UDF| can be found at :doc:`/ds_apir`



        :param func: User-Defined Function (|UDF|) which takes the values in the row and produces a value, or collection of values, for the new cell(s).
        :type func: UDF
        :param schema: The schema for the results of the |UDF|, indicating the new column(s) to add.  Each tuple provides the column name and data type, and is of the form (str, type).
        :type schema: tuple | list of tuples
        :param columns_accessed: (default=None)  List of columns which the |UDF| will access.  This adds significant performance benefit if we know which column(s) will be needed to execute the |UDF|, especially when the frame has significantly more columns than those being used to evaluate the |UDF|.
        :type columns_accessed: list
        """
        return None


    @doc_stub
    def add_vertices(self, source_frame, id_column_name, column_names=None):
        """
        Add vertices to a graph.

        Includes appending to a list of existing vertices.

        See :doc:`here <../../graphs/graph-/__init__>` for example usage in
        graph construction.


        :param source_frame: Frame that will be the source of
            the vertex data.
        :type source_frame: Frame
        :param id_column_name: Column name for a unique id for each vertex.
        :type id_column_name: unicode
        :param column_names: (default=None)  Column names that will be turned
            into properties for each vertex.
        :type column_names: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def assign_sample(self, sample_percentages, sample_labels=None, output_column=None, random_seed=None):
        """
        Randomly group rows into user-defined classes.

        Randomly assign classes to rows given a vector of percentages.
        The table receives an additional column that contains a random label.
        The random label is generated by a probability distribution function.
        The distribution function is specified by the sample_percentages, a list of
        floating point values, which add up to 1.
        The labels are non-negative integers drawn from the range
        :math:`[ 0, len(S) - 1]` where :math:`S` is the sample_percentages.

        **Notes**

        The sample percentages provided by the user are preserved to at least eight
        decimal places, but beyond this there may be small changes due to floating
        point imprecision.

        In particular:

        #)  The engine validates that the sum of probabilities sums to 1.0 within
            eight decimal places and returns an error if the sum falls outside of this
            range.
        #)  The probability of the final class is clamped so that each row receives a
            valid label with probability one.


        Consider this simple frame.

        >>> frame.inspect()
        [#]  blip  id
        =============
        [0]  abc    0
        [1]  def    1
        [2]  ghi    2
        [3]  jkl    3
        [4]  mno    4
        [5]  pqr    5
        [6]  stu    6
        [7]  vwx    7
        [8]  yza    8
        [9]  bcd    9

        We'll assign labels to each row according to a rough 40-30-30 split, for
        "train", "test", and "validate".

        >>> frame.assign_sample([0.4, 0.3, 0.3])
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin
        =========================
        [0]  abc    0  VA
        [1]  def    1  TR
        [2]  ghi    2  TE
        [3]  jkl    3  TE
        [4]  mno    4  TE
        [5]  pqr    5  TR
        [6]  stu    6  TR
        [7]  vwx    7  VA
        [8]  yza    8  VA
        [9]  bcd    9  VA


        Now the frame  has a new column named "sample_bin" with a string label.
        Values in the other columns are unaffected.

        Here it is again, this time specifying labels, output column and random seed

        >>> frame.assign_sample([0.2, 0.2, 0.3, 0.3],
        ...                     ["cat1", "cat2", "cat3", "cat4"],
        ...                     output_column="cat",
        ...                     random_seed=12)
        [===Job Progress===]

        >>> frame.inspect()
        [#]  blip  id  sample_bin  cat
        ===============================
        [0]  abc    0  VA          cat4
        [1]  def    1  TR          cat2
        [2]  ghi    2  TE          cat3
        [3]  jkl    3  TE          cat4
        [4]  mno    4  TE          cat1
        [5]  pqr    5  TR          cat3
        [6]  stu    6  TR          cat2
        [7]  vwx    7  VA          cat3
        [8]  yza    8  VA          cat3
        [9]  bcd    9  VA          cat4



        :param sample_percentages: Entries are non-negative and sum to 1. (See the note below.)
            If the *i*'th entry of the  list is *p*,
            then then each row receives label *i* with independent probability *p*.
        :type sample_percentages: list
        :param sample_labels: (default=None)  Names to be used for the split classes.
            Defaults to "TR", "TE", "VA" when the length of *sample_percentages* is 3,
            and defaults to Sample_0, Sample_1, ... otherwise.
        :type sample_labels: list
        :param output_column: (default=None)  Name of the new column which holds the labels generated by the
            function.
        :type output_column: unicode
        :param random_seed: (default=None)  Random seed used to generate the labels.
            Defaults to 0.
        :type random_seed: int32

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column(self, column_name, cutoffs, include_lowest=None, strict_binning=None, bin_column_name=None):
        """
        Classify data into user-defined groups.

        Summarize rows of data based on the value in a single column by sorting them
        into bins, or groups, based on a list of bin cutoff points.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  Bins IDs are 0-index, in other words, the lowest bin number is 0.
        #)  The first and last cutoffs are always included in the bins.
            When *include_lowest* is ``True``, the last bin includes both cutoffs.
            When *include_lowest* is ``False``, the first bin (bin 0) includes both
            cutoffs.

        Examples
        --------
        For these examples, we will use a frame with column *a* accessed by a Frame
        object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame with a column showing what bin the data is in.
        The data values should use strict_binning:

        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1      -1
        [1]    1      -1
        [2]    2      -1
        [3]    3      -1
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89      -1

        Modify the frame with a column showing what bin the data is in.
        The data value should not use strict_binning:


        >>> my_frame.bin_column('a', [5,12,25,60], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       0
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       2
        [10]  89       2

        Modify the frame with a column showing what bin the data is in.
        The bins should be lower inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=True,
        ... strict_binning=False, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       1
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       2
        [9]   55       3
        [10]  89       3

        Modify the frame with a column showing what bin the data is in.
        The bins should be upper inclusive:

        >>> my_frame.bin_column('a', [1,5,34,55,89], include_lowest=False,
        ... strict_binning=True, bin_column_name='binned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   binned
        ================
        [0]    1       0
        [1]    1       0
        [2]    2       0
        [3]    3       0
        [4]    5       0
        [5]    8       1
        [6]   13       1
        [7]   21       1
        [8]   34       1
        [9]   55       2
        [10]  89       3



        :param column_name: Name of the column to bin.
        :type column_name: unicode
        :param cutoffs: Array of values containing bin cutoff points.
            Array can be list or tuple.
            Array values must be progressively increasing.
            All bin boundaries must be included, so, with N bins, you need N+1 values.
        :type cutoffs: list
        :param include_lowest: (default=None)  Specify how the boundary conditions are handled.
            ``True`` indicates that the lower bound of the bin is inclusive.
            ``False`` indicates that the upper bound is inclusive.
            Default is ``True``.
        :type include_lowest: bool
        :param strict_binning: (default=None)  Specify how values outside of the cutoffs array should be binned.
            If set to ``True``, each value less than cutoffs[0] or greater than
            cutoffs[-1] will be assigned a bin value of -1.
            If set to ``False``, values less than cutoffs[0] will be included in the first
            bin while values greater than cutoffs[-1] will be included in the final
            bin.
        :type strict_binning: bool
        :param bin_column_name: (default=None)  The name for the new binned column.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def bin_column_equal_depth(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into groups with the same frequency.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal depth binning attempts to label rows such that each bin contains the
        same number of elements.
        For :math:`n` bins of a column :math:`C` of length :math:`m`, the bin
        number is determined by:

        .. math::

            \lceil n * \frac { f(C) }{ m } \rceil

        where :math:`f` is a tie-adjusted ranking function over values of
        :math:`C`.
        If there are multiples of the same value in :math:`C`, then their
        tie-adjusted rank is the average of their ordered rank values.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has a quantity of :math"`X`
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89


        Modify the frame, adding a column showing what bin the data is in.
        The data should be grouped into a maximum of five bins.
        Note that each bin will have the same quantity of members (as much as
        possible):

        >>> cutoffs = my_frame.bin_column_equal_depth('a', 5, 'aEDBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEDBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          1
        [3]    3          1
        [4]    5          2
        [5]    8          2
        [6]   13          3
        [7]   21          3
        [8]   34          4
        [9]   55          4
        [10]  89          4

        >>> print cutoffs
        [1.0, 2.0, 5.0, 13.0, 34.0, 89.0]


        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list containing the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def bin_column_equal_width(self, column_name, num_bins=None, bin_column_name=None):
        """
        Classify column into same-width groups.

        Group rows of data based on the value in a single column and add a label
        to identify grouping.

        Equal width binning places column values into groups such that the values
        in each group fall within the same interval and the interval width for each
        group is equal.

        **Notes**

        #)  Unicode in column names is not supported and will likely cause the
            drop_frames() method (and others) to fail!
        #)  The num_bins parameter is considered to be the maximum permissible number
            of bins because the data may dictate fewer bins.
            For example, if the column to be binned has 10
            elements with only 2 distinct values and the *num_bins* parameter is
            greater than 2, then the number of actual number of bins will only be 2.
            This is due to a restriction that elements with an identical value must
            belong to the same bin.

        Examples
        --------
        Given a frame with column *a* accessed by a Frame object *my_frame*:

        >>> my_frame.inspect( n=11 )
        [##]  a 
        ========
        [0]    1
        [1]    1
        [2]    2
        [3]    3
        [4]    5
        [5]    8
        [6]   13
        [7]   21
        [8]   34
        [9]   55
        [10]  89

        Modify the frame, adding a column showing what bin the data is in.
        The data should be separated into a maximum of five bins and the bin cutoffs
        should be evenly spaced.
        Note that there may be bins with no members:

        >>> cutoffs = my_frame.bin_column_equal_width('a', 5, 'aEWBinned')
        [===Job Progress===]
        >>> my_frame.inspect( n=11 )
        [##]  a   aEWBinned
        ===================
        [0]    1          0
        [1]    1          0
        [2]    2          0
        [3]    3          0
        [4]    5          0
        [5]    8          0
        [6]   13          0
        [7]   21          1
        [8]   34          1
        [9]   55          3
        [10]  89          4

        The method returns a list of 6 cutoff values that define the edges of each bin.
        Note that difference between the cutoff values is constant:

        >>> print cutoffs
        [1.0, 18.6, 36.2, 53.8, 71.4, 89.0]



        :param column_name: The column whose values are to be binned.
        :type column_name: unicode
        :param num_bins: (default=None)  The maximum number of bins.
            Default is the Square-root choice
            :math:`\lfloor \sqrt{m} \rfloor`, where :math:`m` is the number of rows.
        :type num_bins: int32
        :param bin_column_name: (default=None)  The name for the new column holding the grouping labels.
            Default is ``<column_name>_binned``.
        :type bin_column_name: unicode

        :returns: A list of the edges of each bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def categorical_summary(self, *column_inputs):
        """
        Compute a summary of the data in a column(s) for categorical or numerical data types.

        The returned value is a Map containing categorical summary for each specified column.

        For each column, levels which satisfy the top k and/or threshold cutoffs are displayed along
        with their frequency and percentage occurrence with respect to the total rows in the dataset.

        Missing data is reported when a column value is empty ("") or null.

        All remaining data is grouped together in the Other category and its frequency and percentage are reported as well.

        User must specify the column name and can optionally specify top_k and/or threshold.

        Optional parameters:

            top_k
                Displays levels which are in the top k most frequently occurring values for that column.

            threshold
                Displays levels which are above the threshold percentage with respect to the total row count.

            top_k and threshold
                Performs level pruning first based on top k and then filters out levels which satisfy the threshold criterion.

            defaults
                Displays all levels which are in Top 10.


        Examples
        --------


        .. code::

            >>> frame.categorical_summary('source','target')
            >>> frame.categorical_summary(('source', {'top_k' : 2}))
            >>> frame.categorical_summary(('source', {'threshold' : 0.5}))
            >>> frame.categorical_summary(('source', {'top_k' : 2}), ('target',
            ... {'threshold' : 0.5}))

        Sample output (for last example above):

            >>> {u'categorical_summary': [{u'column': u'source', u'levels': [
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'thing'},
            ... {u'percentage': 0.32142857142857145, u'frequency': 9, u'level': u'abstraction'},
            ... {u'percentage': 0.25, u'frequency': 7, u'level': u'physical_entity'},
            ... {u'percentage': 0.10714285714285714, u'frequency': 3, u'level': u'entity'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Other'}]},
            ... {u'column': u'target', u'levels': [
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'thing'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2,
            ...  u'level': u'physical_entity'},
            ... {u'percentage': 0.07142857142857142, u'frequency': 2, u'level': u'entity'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'variable'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'unit'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'substance'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'subject'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'set'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'reservoir'},
            ... {u'percentage': 0.03571428571428571, u'frequency': 1, u'level': u'relation'},
            ... {u'percentage': 0.0, u'frequency': 0, u'level': u'Missing'},
            ... {u'percentage': 0.5357142857142857, u'frequency': 15, u'level': u'Other'}]}]}



        :param *column_inputs: (default=None)  Comma-separated column names to summarize or tuple containing column name and dictionary of optional parameters. Optional parameters (see below for details): top_k (default = 10), threshold (default = 0.0)
        :type *column_inputs: str | tuple(str, dict)

        :returns: Summary for specified column(s) consisting of levels with their frequency and percentage
        :rtype: dict
        """
        return None


    @doc_stub
    def classification_metrics(self, label_column, pred_column, pos_label=None, beta=None, frequency_column=None):
        """
        Model statistics of accuracy, precision, and others.

        Calculate the accuracy, precision, confusion_matrix, recall and
        :math:`F_{ \beta}` measure for a classification model.

        *   The **f_measure** result is the :math:`F_{ \beta}` measure for a
            classification model.
            The :math:`F_{ \beta}` measure of a binary classification model is the
            harmonic mean of precision and recall.
            If we let:

            * beta :math:`\equiv \beta`,
            * :math:`T_{P}` denotes the number of true positives,
            * :math:`F_{P}` denotes the number of false positives, and
            * :math:`F_{N}` denotes the number of false negatives

            then:

            .. math::

                F_{ \beta} = (1 + \beta ^ 2) * \frac{ \frac{T_{P}}{T_{P} + F_{P}} * \
                \frac{T_{P}}{T_{P} + F_{N}}}{ \beta ^ 2 * \frac{T_{P}}{T_{P} + \
                F_{P}}  + \frac{T_{P}}{T_{P} + F_{N}}}

            The :math:`F_{ \beta}` measure for a multi-class classification model is
            computed as the weighted average of the :math:`F_{ \beta}` measure for
            each label, where the weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **recall** result of a binary classification model is the proportion
            of positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{N}` denote the number of false negatives, then the model
            recall is given by :math:`\frac {T_{P}} {T_{P} + F_{N}}`.

            For multi-class classification models, the recall measure is computed as
            the weighted average of the recall for each label, where the weight is
            the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **precision** of a binary classification model is the proportion of
            predicted positive instances that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives and
            :math:`F_{P}` denote the number of false positives, then the model
            precision is given by: :math:`\frac {T_{P}} {T_{P} + F_{P}}`.

            For multi-class classification models, the precision measure is computed
            as the weighted average of the precision for each label, where the
            weight is the number of instances of each label.
            The determination of binary vs. multi-class is automatically inferred
            from the data.

        *   The **accuracy** of a classification model is the proportion of
            predictions that are correctly identified.
            If we let :math:`T_{P}` denote the number of true positives,
            :math:`T_{N}` denote the number of true negatives, and :math:`K` denote
            the total number of classified instances, then the model accuracy is
            given by: :math:`\frac{T_{P} + T_{N}}{K}`.

            This measure applies to binary and multi-class classifiers.

        *   The **confusion_matrix** result is a confusion matrix for a
            binary classifier model, formatted for human readability.

        Notes
        -----
        The **confusion_matrix** is not yet implemented for multi-class classifiers.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  a      b  labels  predictions
            ==================================
            [0]  red    1       0            0
            [1]  blue   3       1            0
            [2]  green  1       0            0
            [3]  green  0       1            1


            >>> cm = my_frame.classification_metrics('labels', 'predictions', 1, 1)
            [===Job Progress===]

            >>> cm.f_measure
            0.6666666666666666

            >>> cm.recall
            0.5

            >>> cm.accuracy
            0.75

            >>> cm.precision
            1.0

            >>> cm.confusion_matrix
                        Predicted_Pos  Predicted_Neg
            Actual_Pos              1              1
            Actual_Neg              0              2





        :param label_column: The name of the column containing the
            correct label for each instance.
        :type label_column: unicode
        :param pred_column: The name of the column containing the
            predicted label for each instance.
        :type pred_column: unicode
        :param pos_label: (default=None)  
        :type pos_label: None
        :param beta: (default=None)  This is the beta value to use for
            :math:`F_{ \beta}` measure (default F1 measure is computed); must be greater than zero.
            Defaults is 1.
        :type beta: float64
        :param frequency_column: (default=None)  The name of an optional column containing the
            frequency of observations.
        :type frequency_column: unicode

        :returns: The data returned is composed of multiple components\:

            |   <object>.accuracy : double
            |   <object>.confusion_matrix : table
            |   <object>.f_measure : double
            |   <object>.precision : double
            |   <object>.recall : double
        :rtype: dict
        """
        return None


    @doc_stub
    def column_median(self, data_column, weights_column=None):
        """
        Calculate the (weighted) median of a column.

        The median is the least value X in the range of the distribution so that
        the cumulative weight of values strictly below X is strictly less than half
        of the total weight and the cumulative weight of values up to and including X
        is greater than or equal to one-half of the total weight.

        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If a weight column is provided and no weights are finite numbers greater
        than 0, None is returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return middle number of values in column *a*:

        .. code::

           >>> median = my_frame.column_median('a')
           [===Job Progress===]
           >>> print median
           5

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return middle number of values in column 'a' with weights 'w':

        .. code::

           >>> median = my_frame.column_median('a', weights_column='w')
           [===Job Progress===]
           >>> print median
           3


        :param data_column: The column whose median is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies)
            for the median calculation.
            Must contain numerical data.
            Default is all items have a weight of 1.
        :type weights_column: unicode

        :returns: varies
                The median of the values.
                If a weight column is provided and no weights are finite numbers greater
                than 0, None is returned.
                The type of the median returned is the same as the contents of the data
                column, so a column of Longs will result in a Long median and a column of
                Floats will result in a Float median.
        :rtype: None
        """
        return None


    @doc_stub
    def column_mode(self, data_column, weights_column=None, max_modes_returned=None):
        """
        Evaluate the weights assigned to rows.

        Calculate the modes of a column.
        A mode is a data element of maximum weight.
        All data elements of weight less than or equal to 0 are excluded from the
        calculation, as are all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight greater than 0,
        no mode is returned.

        Because data distributions often have multiple modes, it is possible for a
        set of modes to be returned.
        By default, only one is returned, but by setting the optional parameter
        max_modes_returned, a larger number of modes can be returned.

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30
           

        Compute and return a dictionary containing summary statistics of column *a*:

        .. code::

           >>> mode = my_frame.column_mode('a')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 1), (u'modes', [3]), (u'total_weight', 7.0), (u'weight_of_mode', 2.0)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149
           

        Compute and return dictionary containing summary statistics of column 'a' with weights 'w':

        .. code::

           >>> mode = my_frame.column_mode('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(mode.items())
           [(u'mode_count', 2), (u'modes', [2]), (u'total_weight', 6.200000144541264), (u'weight_of_mode', 1.7000000476837158)]



        :param data_column: Name of the column supplying the data.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of the column supplying the weights.
            Default is all items have weight of 1.
        :type weights_column: unicode
        :param max_modes_returned: (default=None)  Maximum number of modes returned.
            Default is 1.
        :type max_modes_returned: int32

        :returns: Dictionary containing summary statistics.
                The data returned is composed of multiple components\:

            mode : A mode is a data element of maximum net weight.
                A set of modes is returned.
                The empty set is returned when the sum of the weights is 0.
                If the number of modes is less than or equal to the parameter
                max_modes_returned, then all modes of the data are
                returned.
                If the number of modes is greater than the max_modes_returned
                parameter, only the first max_modes_returned many modes (per a
                canonical ordering) are returned.
            weight_of_mode : Weight of a mode.
                If there are no data elements of finite weight greater than 0,
                the weight of the mode is 0.
                If no weights column is given, this is the number of appearances
                of each mode.
            total_weight : Sum of all weights in the weight column.
                This is the row count if no weights are given.
                If no weights column is given, this is the number of rows in
                the table with non-zero weight.
            mode_count : The number of distinct modes in the data.
                In the case that the data is very multimodal, this number may
                exceed max_modes_returned.


        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def column_names(self):
        """
        Column identifications in the current frame.

        Returns the names of the columns of the current frame.

        Examples
        --------

        .. code::


            >>> frame.column_names
            [u'name', u'age', u'tenure', u'phone']





        :returns: list of names of all the frame's columns
        :rtype: list
        """
        return None


    @doc_stub
    def column_summary_statistics(self, data_column, weights_column=None, use_population_variance=None):
        """
        Calculate multiple statistics for a column.

        Notes
        -----
        Sample Variance
            Sample Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W - 1} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Population Variance
            Population Variance is computed by the following formula:

            .. math::

                \left( \frac{1}{W} \right) * sum_{i} \
                \left(x_{i} - M \right) ^{2}

            where :math:`W` is sum of weights over valid elements of positive
            weight, and :math:`M` is the weighted mean.

        Standard Deviation
            The square root of the variance.

        Logging Invalid Data
            A row is bad when it contains a NaN or infinite value in either
            its data or weights column.
            In this case, it contributes to bad_row_count; otherwise it
            contributes to good row count.

            A good row can be skipped because the value in its weight
            column is less than or equal to 0.
            In this case, it contributes to non_positive_weight_count, otherwise
            (when the weight is greater than 0) it contributes to
            valid_data_weight_pair_count.

        **Equations**

            .. code::

                bad_row_count + good_row_count = # rows in the frame
                positive_weight_count + non_positive_weight_count = good_row_count

            In particular, when no weights column is provided and all weights are 1.0:

            .. code::

                non_positive_weight_count = 0 and
                positive_weight_count = good_row_count

        Examples
        --------
        Given a frame with column 'a' accessed by a Frame object 'my_frame':

        .. code::

           >>> import trustedanalytics as ta
           >>> ta.connect()
           Connected ...
           >>> data = [[2],[3],[3],[5],[7],[10],[30]]
           >>> schema = [('a', ta.int32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a
           =======
           [0]   2
           [1]   3
           [2]   3
           [3]   5
           [4]   7
           [5]  10
           [6]  30

        Compute and return summary statistics for values in column *a*:

        .. code::

           >>> summary_statistics = my_frame.column_summary_statistics('a')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 5.6725751451901045), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 8.571428571428571), (u'mean_confidence_lower', 1.277083729932067), (u'mean_confidence_upper', 15.865773412925076), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 9.846440014156434), (u'total_weight', 7.0), (u'variance', 96.95238095238095)]

        Given a frame with column 'a' and column 'w' as weights accessed by a Frame object 'my_frame':

        .. code::

           >>> data = [[2,1.7],[3,0.5],[3,1.2],[5,0.8],[7,1.1],[10,0.8],[30,0.1]]
           >>> schema = [('a', ta.int32), ('w', ta.float32)]
           >>> my_frame = ta.Frame(ta.UploadRows(data, schema))
           [===Job Progress===]

        Inspect my_frame

        .. code::

           >>> my_frame.inspect()
           [#]  a   w
           =======================
           [0]   2   1.70000004768
           [1]   3             0.5
           [2]   3   1.20000004768
           [3]   5  0.800000011921
           [4]   7   1.10000002384
           [5]  10  0.800000011921
           [6]  30   0.10000000149


        Compute and return summary statistics values in column 'a' with weights 'w':

        .. code::
           >>> summary_statistics = my_frame.column_summary_statistics('a', weights_column='w')
           [===Job Progress===]
           >>> print sorted(summary_statistics.items())
           [(u'bad_row_count', 0), (u'geometric_mean', 4.039682869616821), (u'good_row_count', 7), (u'maximum', 30.0), (u'mean', 5.032258048622591), (u'mean_confidence_lower', 1.4284724667085964), (u'mean_confidence_upper', 8.636043630536586), (u'minimum', 2.0), (u'non_positive_weight_count', 0), (u'positive_weight_count', 7), (u'standard_deviation', 4.578241754132706), (u'total_weight', 6.200000144541264), (u'variance', 20.96029755928412)]


        :param data_column: The column to be statistically summarized.
            Must contain numerical data; all NaNs and infinite values are excluded
            from the calculation.
        :type data_column: unicode
        :param weights_column: (default=None)  Name of column holding weights of
            column values.
        :type weights_column: unicode
        :param use_population_variance: (default=None)  If true, the variance is calculated
            as the population variance.
            If false, the variance calculated as the sample variance.
            Because this option affects the variance, it affects the standard
            deviation and the confidence intervals as well.
            Default is false.
        :type use_population_variance: bool

        :returns: Dictionary containing summary statistics.
            The data returned is composed of multiple components\:

            |   mean : [ double | None ]
            |       Arithmetic mean of the data.
            |   geometric_mean : [ double | None ]
            |       Geometric mean of the data. None when there is a data element <= 0, 1.0 when there are no data elements.
            |   variance : [ double | None ]
            |       None when there are <= 1 many data elements. Sample variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight minus 1. None when the sum of the weights is <= 1. Population variance is the weighted sum of the squared distance of each data element from the weighted mean, divided by the total weight.
            |   standard_deviation : [ double | None ]
            |       The square root of the variance. None when  sample variance is being used and the sum of weights is <= 1.
            |   total_weight : long
            |       The count of all data elements that are finite numbers. In other words, after excluding NaNs and infinite values.
            |   minimum : [ double | None ]
            |       Minimum value in the data. None when there are no data elements.
            |   maximum : [ double | None ]
            |       Maximum value in the data. None when there are no data elements.
            |   mean_confidence_lower : [ double | None ]
            |       Lower limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   mean_confidence_upper : [ double | None ]
            |       Upper limit of the 95% confidence interval about the mean. Assumes a Gaussian distribution. None when there are no elements of positive weight.
            |   bad_row_count : [ double | None ]
            |       The number of rows containing a NaN or infinite value in either the data or weights column.
            |   good_row_count : [ double | None ]
            |       The number of rows not containing a NaN or infinite value in either the data or weights column.
            |   positive_weight_count : [ double | None ]
            |       The number of valid data elements with weight > 0. This is the number of entries used in the statistical calculation.
            |   non_positive_weight_count : [ double | None ]
            |       The number valid data elements with finite weight <= 0.
        :rtype: dict
        """
        return None


    @doc_stub
    def copy(self, columns=None, where=None, name=None):
        """
        Create new frame from current frame.

        Copy frame or certain frame columns entirely or filtered.
        Useful for frame query.

        Examples
        --------

        .. code::

            >>> frame
            Frame <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode, adult_years:int32, of_age:float32, of_adult:float32, tenured_name:unicode, tenured_name_age:unicode]
            status = ACTIVE  (last_read_date = -etc-)

            >>> frame2 = frame.copy()  # full copy of the frame
            [===Job Progress===]

            >>> frame3 = frame.copy(['name', 'age'])  # copy only two columns
            [===Job Progress===]
            >>> frame3
            Frame  <unnamed>
            row_count = 4
            schema = [name:unicode, age:int32]
            status = ACTIVE  (last_read_date = -etc-)

        .. code::

            >>> frame4 = frame.copy({'name': 'name', 'age': 'age', 'tenure': 'years'},
            ...                     where=lambda row: row.age > 40)
            [===Job Progress===]
            >>> frame4.inspect()
            [#]  name      age  years
            =========================
            [0]  Thurston   65     26
            [1]  Judy       44     14



        :param columns: (default=None)  If not None, the copy will only include the columns specified. If dict, the string pairs represent a column renaming, {source_column_name: destination_column_name}
        :type columns: str | list of str | dict
        :param where: (default=None)  If not None, only those rows for which the UDF evaluates to True will be copied.
        :type where: function
        :param name: (default=None)  Name of the copied frame
        :type name: str

        :returns: A new Frame of the copied data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def correlation(self, data_column_names):
        """
        Calculate correlation for two columns of current frame.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation computes the common correlation coefficient (Pearson's) on the pair
        of columns provided.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051 .


            >>> my_frame.correlation(["x1", "x2"])
            [===Job Progress===]

                -1.0
            >>> my_frame.correlation(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.correlation(["x2", "x3"])
            [===Job Progress===]

                -0.948683298051




        :param data_column_names: The names of 2 columns from which
            to compute the correlation.
        :type data_column_names: list

        :returns: Pearson correlation coefficient of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def correlation_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate correlation matrix for two or more columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.correlation_matrix computes the common correlation coefficient (Pearson's) on each pair
        of columns in the user-provided list.
        In this example, the *idnum* and most of the columns have trivial correlations: -1, 0, or +1.
        Column *x3* provides a contrasting coefficient of 3 / sqrt(3) = 0.948683298051

            >>> corr_matrix = my_frame.correlation_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> corr_matrix.inspect()
            [#]  idnum           x1              x2               x3               x4
            ==========================================================================
            [0]             1.0             1.0             -1.0   0.948683298051  0.0
            [1]             1.0             1.0             -1.0   0.948683298051  0.0
            [2]            -1.0            -1.0              1.0  -0.948683298051  0.0
            [3]  0.948683298051  0.948683298051  -0.948683298051              1.0  0.0
            [4]             0.0             0.0              0.0              0.0  1.0





        :param data_column_names: The names of the columns from
            which to compute the matrix.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name for the returned
            matrix Frame.
        :type matrix_name: unicode

        :returns: A Frame with the matrix of the correlation values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def count(self, where):
        """
        Counts the number of rows which meet given criteria.

        Examples
        --------


            >>> frame.inspect()
            [#]  name      age  tenure  phone
            ====================================
            [0]  Fred       39      16  555-1234
            [1]  Susan      33       3  555-0202
            [2]  Thurston   65      26  555-4510
            [3]  Judy       44      14  555-2183
            >>> frame.count(lambda row: row.age > 35)
            [===Job Progress===]
            3



        :param where: |UDF| which evaluates a row to a boolean
        :type where: function

        :returns: number of rows for which the where |UDF| evaluated to True.
        :rtype: int
        """
        return None


    @doc_stub
    def covariance(self, data_column_names):
        """
        Calculate covariance for exactly two columns.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
            [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance computes the covariance on the pair of columns provided.

            >>> my_frame.covariance(["x1", "x2"])
            [===Job Progress===]

                -2.5
            >>> my_frame.covariance(["x1", "x4"])
            [===Job Progress===]

                0.0
            >>> my_frame.covariance(["x2", "x3"])
            [===Job Progress===]

                -1.5




        :param data_column_names: The names of two columns from which
            to compute the covariance.
        :type data_column_names: list

        :returns: Covariance of the two columns.
        :rtype: float64
        """
        return None


    @doc_stub
    def covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def cumulative_percent(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative percent sum is computed by sequentially stepping through the
        rows, observing the column values and keeping track of the current percentage of the total sum
        accounted for at the current value.


        Notes
        -----
        This method applies only to columns containing numerical data.
        Although this method will execute for columns containing negative
        values, the interpretation of the result will change (for example,
        negative percentages).

        Examples
        --------
        Consider Frame *my_frame* accessing a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent sum for column *obs* is obtained by:

            >>> my_frame.cumulative_percent('obs')
            [===Job Progress===]

        The Frame *my_frame* now contains two columns *obs* and
        *obsCumulativePercentSum*.
        They contain the original data and the cumulative percent sum,
        respectively:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_percent
            ================================
            [0]    0                     0.0
            [1]    1          0.166666666667
            [2]    2                     0.5
            [3]    0                     0.5
            [4]    1          0.666666666667
            [5]    2                     1.0


        :param sample_col: The name of the column from which to compute
            the cumulative percent sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def cumulative_sum(self, sample_col):
        """
        Add column to frame with cumulative percent sum.

        A cumulative sum is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the cumulative sum for each value.

        Notes
        -----
        This method applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative sum for column *obs* is obtained by:

            >>> my_frame.cumulative_sum('obs')
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativeSum* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_cumulative_sum
            ============================
            [0]    0                 0.0
            [1]    1                 1.0
            [2]    2                 3.0
            [3]    0                 3.0
            [4]    1                 4.0
            [5]    2                 6.0

        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def daal_covariance_matrix(self, data_column_names, matrix_name=None):
        """
        Calculate covariance matrix for two or more columns.

        Uses Intel Data Analytics and Acceleration Library (DAAL) to compute covariance matrix.

        Notes
        -----
        This function applies only to columns containing numerical data.

        Examples
        --------
        Consider Frame *my_frame*, which contains the data

            >>> my_frame.inspect()
             [#]  idnum  x1   x2   x3   x4
            ===============================
            [0]      0  1.0  4.0  0.0  -1.0
            [1]      1  2.0  3.0  0.0  -1.0
            [2]      2  3.0  2.0  1.0  -1.0
            [3]      3  4.0  1.0  2.0  -1.0
            [4]      4  5.0  0.0  2.0  -1.0


        my_frame.daal_covariance_matrix computes the covariance on each pair of columns in the user-provided list.

            >>> cov_matrix = my_frame.daal_covariance_matrix(my_frame.column_names)
            [===Job Progress===]

            The resulting table (specifying all columns) is:

            >>> cov_matrix.inspect()
            [#]  idnum  x1    x2    x3    x4
            =================================
            [0]    2.5   2.5  -2.5   1.5  0.0
            [1]    2.5   2.5  -2.5   1.5  0.0
            [2]   -2.5  -2.5   2.5  -1.5  0.0
            [3]    1.5   1.5  -1.5   1.0  0.0
            [4]    0.0   0.0   0.0   0.0  0.0






        :param data_column_names: The names of the column from which to compute the matrix.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type data_column_names: list
        :param matrix_name: (default=None)  The name of the new
            matrix.
        :type matrix_name: unicode

        :returns: A matrix with the covariance values for the columns.
        :rtype: Frame
        """
        return None


    @doc_stub
    def dot_product(self, left_column_names, right_column_names, dot_product_column_name, default_left_values=None, default_right_values=None):
        """
        Calculate dot product for each row in current frame.

        Calculate the dot product for each row in a frame using values from two
        equal-length sequences of columns.

        Dot product is computed by the following formula:

        The dot product of two vectors :math:`A=[a_1, a_2, ..., a_n]` and
        :math:`B =[b_1, b_2, ..., b_n]` is :math:`a_1*b_1 + a_2*b_2 + ...+ a_n*b_n`.
        The dot product for each row is stored in a new column in the existing frame.

        Notes
        -----
        If default_left_values or default_right_values are not specified, any null
        values will be replaced by zeros.

        Examples
        --------
        Calculate the dot product for a sequence of columns in Frame object *my_frame*:

        .. code::

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3
            ===============================
            [0]      1    0.2     -2      5
            [1]      2    0.4     -1      6
            [2]      3    0.6      0      7
            [3]      4    0.8      1      8


        Modify the frame by computing the dot product for a sequence of columns:

        .. code::

             >>> my_frame.dot_product(['col_0','col_1'], ['col_2', 'col_3'], 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_0  col_1  col_2  col_3  dot_product
            ============================================
            [0]      1    0.2     -2      5         -1.0
            [1]      2    0.4     -1      6          0.4
            [2]      3    0.6      0      7          4.2
            [3]      4    0.8      1      8         10.4


        Calculate the dot product for columns of vectors in Frame object *my_frame*:


        .. code::
             >>> my_frame.dot_product('col_4', 'col_5', 'dot_product')
             [===Job Progress===]

            >>> my_frame.inspect()
            [#]  col_4       col_5        dot_product
            =========================================
            [0]  [1.0, 0.2]  [-2.0, 5.0]         -1.0
            [1]  [2.0, 0.4]  [-1.0, 6.0]          0.4
            [2]  [3.0, 0.6]  [0.0, 7.0]           4.2
            [3]  [4.0, 0.8]  [1.0, 8.0]          10.4


        :param left_column_names: Names of columns used to create the left vector (A) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type left_column_names: list
        :param right_column_names: Names of columns used to create right vector (B) for each row.
            Names should refer to a single column of type vector, or two or more
            columns of numeric scalars.
        :type right_column_names: list
        :param dot_product_column_name: Name of column used to store the
            dot product.
        :type dot_product_column_name: unicode
        :param default_left_values: (default=None)  Default values used to substitute null values in left vector.
            Default is None.
        :type default_left_values: list
        :param default_right_values: (default=None)  Default values used to substitute null values in right vector.
            Default is None.
        :type default_right_values: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def download(self, n=100, offset=0, columns=None):
        """
        Download frame data from the server into client workspace as a pandas dataframe

        Similar to the 'take' function, but puts the data in a pandas dataframe.

        Examples
        --------

        .. code::

            >>> pandas_frame = frame.download(columns=['name', 'phone'])
            >>> pandas_frame
                   name     phone
            0      Fred  555-1234
            1     Susan  555-0202
            2  Thurston  555-4510
            3      Judy  555-2183



        :param n: (default=100)  The number of rows to download to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before copying
        :type offset: int
        :param columns: (default=None)  Column filter, the names of columns to be included (default is all columns)
        :type columns: list

        :returns: A new pandas dataframe object containing the downloaded frame data
        :rtype: pandas.DataFrame
        """
        return None


    @doc_stub
    def drop_columns(self, columns):
        """
        Remove columns from the frame.

        The data from the columns is lost.

        Notes
        -----
        It is not possible to delete all columns from a frame.
        At least one column needs to remain.
        If it is necessary to delete all columns, then delete the frame.

        Examples
        --------
        For this example, the Frame object *my_frame* accesses a frame with 4 columns
        columns *column_a*, *column_b*, *column_c* and *column_d* and drops 2 columns *column_b* and *column_d* using drop columns.



            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_b', <type 'numpy.int32'>), (u'column_c', <type 'unicode'>), (u'column_d', <type 'numpy.int32'>)]


        Eliminate columns *column_b* and *column_d*:

            >>> my_frame.drop_columns(["column_b", "column_d"])
            >>> print my_frame.schema
            [(u'column_a', <type 'unicode'>), (u'column_c', <type 'unicode'>)]

        Now the frame only has the columns *column_a* and *column_c*.
        For further examples, see: ref:`example_frame.drop_columns`.




        :param columns: Column name OR list of column names to be removed from the frame.
        :type columns: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_duplicates(self, unique_columns=None):
        """
        Remove duplicate vertex rows.

        Remove duplicate vertex rows, keeping only one vertex row per uniqueness
        criteria match.
        Edges that were connected to removed vertices are also automatically dropped.

        See :doc:`here <../../graphs/graph-/__init__>` for example usage


        :param unique_columns: (default=None)  
        :type unique_columns: None

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def drop_rows(self, predicate):
        """
        Delete rows in this vertex frame that qualify.

        Parameters
        ----------
        predicate : |UDF|
            |UDF| or lambda which takes a row argument and evaluates
            to a boolean value.

        Examples
        --------
        Create a frame, move the data to graph and then define a new VertexFrame and add data to it:

        .. code::

            >>> schema = [('viewer', str), ('profile', ta.int32), ('movie', str), ('rating', ta.int32)]
            >>> data = [['fred',0,'Croods',5],
            ...          ['fred',0,'Jurassic Park',5],
            ...          ['fred',0,'2001',2],
            ...          ['fred',0,'Ice Age',4],
            ...          ['wilma',0,'Jurassic Park',3],
            ...          ['wilma',0,'2001',5],
            ...          ['wilma',0,'Ice Age',4],
            ...          ['pebbles',1,'Croods',4],
            ...          ['pebbles',1,'Land Before Time',3],
            ...          ['pebbles',1,'Ice Age',5]]
            >>> frame = ta.Frame(ta.UploadRows(data, schema))
            [===Job Progress===]

            >>> frame.inspect()
            [#]  viewer   profile  movie             rating
            ===============================================
            [0]  fred           0  Croods                 5
            [1]  fred           0  Jurassic Park          5
            [2]  fred           0  2001                   2
            [3]  fred           0  Ice Age                4
            [4]  wilma          0  Jurassic Park          3
            [5]  wilma          0  2001                   5
            [6]  wilma          0  Ice Age                4
            [7]  pebbles        1  Croods                 4
            [8]  pebbles        1  Land Before Time       3
            [9]  pebbles        1  Ice Age                5

            >>> graph = ta.Graph()

            >>> graph.define_vertex_type('viewer')
            [===Job Progress===]

            >>> graph.define_vertex_type('film')
            [===Job Progress===]

            >>> graph.define_edge_type('rating', 'viewer', 'film')
            [===Job Progress===]

            >>> graph.vertices['viewer'].add_vertices(frame, 'viewer', ['profile'])
            [===Job Progress===]

            >>> graph.vertices['viewer'].inspect()
            [#]  _vid  _label  viewer   profile
            ===================================
            [0]     1  viewer  fred           0
            [1]     8  viewer  pebbles        1
            [2]     5  viewer  wilma          0

            >>> graph.vertices['film'].add_vertices(frame, 'movie')
            [===Job Progress===]

            >>> graph.vertices['film'].inspect()
            [#]  _vid  _label  movie
            ===================================
            [0]    19  film    Land Before Time
            [1]    14  film    Ice Age
            [2]    12  film    Jurassic Park
            [3]    11  film    Croods
            [4]    13  film    2001

            >>> graph.edges['rating'].add_edges(frame, 'viewer', 'movie', ['rating'])
            [===Job Progress===]

            >>> graph.edges['rating'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  rating
            ==============================================
            [0]    24         1         14  rating       4
            [1]    22         1         12  rating       5
            [2]    21         1         11  rating       5
            [3]    23         1         13  rating       2
            [4]    29         8         19  rating       3
            [5]    30         8         14  rating       5
            [6]    28         8         11  rating       4
            [7]    27         5         14  rating       4
            [8]    25         5         12  rating       3
            [9]    26         5         13  rating       5

        Call drop_rows() on the film VertexFrame to remove the row for the movie 'Croods' (vid = 11).
        Dangling edges (edges corresponding to 'Croods, vid = 11) are also removed.

        .. code::

            >>> graph.vertices['film'].drop_rows(lambda row: row.movie=='Croods')
            [===Job Progress===]

            >>> graph.vertices['film'].inspect()
            [#]  _vid  _label  movie
            ===================================
            [0]    19  film    Land Before Time
            [1]    14  film    Ice Age
            [2]    12  film    Jurassic Park
            [3]    13  film    2001

            >>> graph.edges['rating'].inspect()
            [#]  _eid  _src_vid  _dest_vid  _label  rating
            ==============================================
            [0]    22         1         12  rating       5
            [1]    25         5         12  rating       3
            [2]    23         1         13  rating       2
            [3]    26         5         13  rating       5
            [4]    24         1         14  rating       4
            [5]    30         8         14  rating       5
            [6]    27         5         14  rating       4
            [7]    29         8         19  rating       3



        :param predicate: |UDF| which evaluates a row (vertex) to a boolean; vertices that answer True are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def ecdf(self, column, result_frame_name=None):
        """
        Builds new frame with columns for data and distribution.

        Generates the empirical cumulative distribution for the input column.

        Consider the following sample data set in *frame* 'frame' containing several numbers.


        >>> frame.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        4
        [7]        3
        >>> ecdf_frame = frame.ecdf('numbers')
        [===Job Progress===]
        >>> ecdf_frame.inspect()
        [#]  numbers  numbers_ECDF
        ==========================
        [0]        0         0.125
        [1]        1           0.5
        [2]        2         0.625
        [3]        3         0.875
        [4]        4           1.0



        :param column: The name of the input column containing sample.
        :type column: unicode
        :param result_frame_name: (default=None)  A name for the resulting frame which is created
            by this operation.
        :type result_frame_name: unicode

        :returns: A new Frame containing each distinct value in the sample and its corresponding ECDF value.
        :rtype: Frame
        """
        return None


    @doc_stub
    def entropy(self, data_column, weights_column=None):
        """
        Calculate the Shannon entropy of a column.

        The data column is weighted via the weights column.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements with a finite weight greater than 0,
        the entropy is zero.

        Consider the following sample data set in *frame* 'frame' containing several numbers.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data  weight
        =================
        [0]     0       1
        [1]     1       2
        [2]     2       4
        [3]     4       8
        >>> entropy = frame.entropy("data", "weight")
        [===Job Progress===]

        >>> "%0.8f" % entropy
        '1.13691659'



        If we have more choices and weights, the computation is not as simple.
        An on-line search for "Shannon Entropy" will provide more detail.

        Given a frame of coin flips, half heads and half tails, the entropy is simply ln(2):

        >>> frame.inspect()
        [#]  data
        =========
        [0]  H
        [1]  T
        [2]  H
        [3]  T
        [4]  H
        [5]  T
        [6]  H
        [7]  T
        [8]  H
        [9]  T
        >>> entropy = frame.entropy("data")
        [===Job Progress===]
        >>> "%0.8f" % entropy
        '0.69314718'



        :param data_column: The column whose entropy is to be calculated.
        :type data_column: unicode
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the entropy calculation.
            Must contain numerical data.
            Default is using uniform weights of 1 for all items.
        :type weights_column: unicode

        :returns: Entropy.
        :rtype: float64
        """
        return None


    @doc_stub
    def export_to_csv(self, folder_name, separator=',', count=-1, offset=0):
        """
        Write current frame to HDFS in csv format.

        Export the frame to a file in csv format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_csv('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"



        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param separator: (default=,)  The separator for separating the values.
            Default is comma (,).
        :type separator: unicode
        :param count: (default=-1)  The number of records you want.
            Default, or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def export_to_hbase(self, table_name, key_column_name=None, family_name='familyColumn'):
        """
        Write current frame to HBase table.

        Table must exist in HBase.
        Export of Vectors is not currently supported.

        Examples
        --------

        Overwrite/append scenarios (see below):

        1. create a simple hbase table from csv
               load csv into a frame using existing frame api
               save the frame into hbase (it creates a table - lets call it table1)

        2. overwrite existing table with new data
               do scenario 1 and create table1
               load the second csv into a frame
               save the frame into table1 (old data is gone)

        3. append data to the existing table 1
               do scenario 1 and create table1
               load table1 into frame1
               load csv into frame2
               let frame1 = frame1 + frame2 (concatenate frame2 into frame1)
               save frame1 into base as table1 (overwrite with initial + appended data)


        Vector scenarios (see below):

        Vectors are not directly supported by HBase (which represents data as byte arrays) or the plugin.
        While is true that a vector can be saved because of the byte array conversion for hbase, the following
        is actually the recommended practice:

        1. Convert the vector to csv (in python, outside ATK)
        2. save the csv as string in the database (using ATK export_to_hbase)
        3. read the cell as string (using ATK, read from hbase
        4. convert the csv to vector (in python, outside ATK)




        :param table_name: The name of the HBase table that will contain the exported frame
        :type table_name: unicode
        :param key_column_name: (default=None)  The name of the column to be used as row key in hbase table
        :type key_column_name: unicode
        :param family_name: (default=familyColumn)  The family name of the HBase table that will contain the exported frame
        :type family_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_hive(self, table_name):
        """
        Write  current frame to Hive table.

        Table must not exist in Hive. Hive does not support case sensitive table names and columns names. Hence column names with uppercase letters will be converted to lower case by Hive.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_hive('covarianceresults')

        :param table_name: The name of the Hive table that will contain the exported frame
        :type table_name: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_jdbc(self, table_name, connector_type='postgres'):
        """
        Write current frame to JDBC table.

        Table will be created or appended to.
        Export of Vectors is not currently supported.

        Examples
        --------
        Consider Frame *my_frame*:

        .. code::

            >>> my_frame.export_to_jdbc('covarianceresults')



        :param table_name: JDBC table name
        :type table_name: unicode
        :param connector_type: (default=postgres)  (optional) JDBC connector, either mysql or postgres. Default is postgres
        :type connector_type: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def export_to_json(self, folder_name, count=0, offset=0):
        """
        Write current frame to HDFS in JSON format.

        Export the frame to a file in JSON format as a Hadoop file.

        Examples
        --------

        .. code::

            >>> frame.export_to_json('covarianceresults')
            [===Job Progress===]
            "hdfs://hostname/user/user1/covarianceresults"


        :param folder_name: The HDFS folder path where the files
            will be created.
        :type folder_name: unicode
        :param count: (default=0)  The number of records you want.
            Default (0), or a non-positive value, is the whole frame.
        :type count: int32
        :param offset: (default=0)  The number of rows to skip before exporting to the file.
            Default is zero (0).
        :type offset: int32

        :returns: The URI of the created file
        :rtype: dict
        """
        return None


    @doc_stub
    def filter(self, predicate):
        """
        <Missing Doc>

        :param predicate: |UDF| which evaluates a row to a boolean; vertices that answer False are dropped from the Frame
        :type predicate: function
        """
        return None


    @doc_stub
    def flatten_columns(self, columns, delimiters=None):
        """
        Spread data to multiple rows based on cell data.

        Splits cells in the specified columns into multiple rows according to a string
        delimiter.
        New rows are a full copy of the original row, but the specified columns only
        contain one value.
        The original row is deleted.

        Examples
        --------

        Given a data file::

            1-solo,mono,single-green,yellow,red
            2-duo,double-orange,black

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32), ('b', str),('c',str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', int32),
                ... ('b', str),('c', str)], delimiter='-')
                >>> frame = ta.Frame(source=my_csv)


        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a  b                 c
            ==========================================
            [0]  1  solo,mono,single  green,yellow,red
            [1]  2  duo,double        orange,black

        Now, spread out those sub-strings in column *b* and *c*:

        .. code::

            >>> frame.flatten_columns(['b','c'], ',')
            [===Job Progress===]

        Note that the delimiters parameter is optional, and if no delimiter is specified, the default
        is a comma (,).  So, in the above example, the delimiter parameter could be omitted.  Also, if
        the delimiters are different for each column being flattened, a list of delimiters can be
        provided.  If a single delimiter is provided, it's assumed that we are using the same delimiter
        for all columns that are being flattened.  If more than one delimiter is provided, the number of
        delimiters must match the number of string columns being flattened.

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a  b       c
            ======================
            [0]  1  solo    green
            [1]  1  mono    yellow
            [2]  1  single  red
            [3]  2  duo     orange
            [4]  2  double  black


        Alternatively, flatten_columns also accepts a single column name (instead of a list) if just one
        column is being flattened.  For example, we could have called flatten_column on just column *b*:


        .. code::

            >>> frame.flatten_columns('b', ',')
            [===Job Progress===]

        Check again:

        .. code ::

            >>> frame.inspect()
            [#]  a  b       c
            ================================
            [0]  1  solo    green,yellow,red
            [1]  1  mono    green,yellow,red
            [2]  1  single  green,yellow,red
            [3]  2  duo     orange,black
            [4]  2  double  orange,black





        :param columns: The columns to be flattened.
        :type columns: list
        :param delimiters: (default=None)  The list of delimiter strings for each column.
            Default is comma (,).
        :type delimiters: list

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def get_error_frame(self):
        """
        Get a frame with error recordings.

        When a frame is created, another frame is transparently
        created to capture parse errors.

        Returns
        -------
        Frame : error frame object
            A new object accessing a frame that contains the parse errors of
            the currently active Frame or None if no error frame exists.



        """
        return None


    @doc_stub
    def group_by(self, group_by_columns, *aggregation_arguments):
        """
        Create summarized frame.

        Creates a new frame and returns a Frame object to access it.
        Takes a column or group of columns, finds the unique combination of
        values, and creates unique rows with these column values.
        The other columns are combined according to the aggregation
        argument(s).

        Notes
        -----
        *   Column order is not guaranteed when columns are added
        *   The column names created by aggregation functions in the new frame
            are the original column name appended with the '_' character and
            the aggregation function.
            For example, if the original field is *a* and the function is
            *avg*, the resultant column is named *a_avg*.
        *   An aggregation argument of *count* results in a column named
            *count*.
        *   The aggregation function *agg.count* is the only full row
            aggregation function supported at this time.
        *   Aggregation currently supports using the following functions:

            *   avg
            *   count
            *   count_distinct
            *   max
            *   min
            *   stdev
            *   sum
            *   var (see glossary Bias vs Variance)
            *   The aggregation arguments also accepts the User Defined function(UDF). UDF acts on each row

        Examples
        --------
        For setup, we will use a Frame *my_frame* accessing a frame with a
        column *a*:

        .. code::


            >>> frame.inspect()
            [#]  a  b        c     d       e  f    g
            ========================================
            [0]  1  alpha     3.0  small   1  3.0  9
            [1]  1  bravo     5.0  medium  1  4.0  9
            [2]  1  alpha     5.0  large   1  8.0  8
            [3]  2  bravo     8.0  large   1  5.0  7
            [4]  2  charlie  12.0  medium  1  6.0  6
            [5]  2  bravo     7.0  small   1  8.0  5
            [6]  2  bravo    12.0  large   1  6.0  4

            Count the groups in column 'b'

            >>> b_count = frame.group_by('b', ta.agg.count)
            [===Job Progress===]
            >>> b_count.inspect()
            [#]  b        count
            ===================
            [0]  alpha        2
            [1]  bravo        4
            [2]  charlie      1

            >>> avg1 = frame.group_by(['a', 'b'], {'c' : ta.agg.avg})
            [===Job Progress===]
            >>> avg1.inspect()
            [#]  a  b        c_AVG
            ======================
            [0]  2  bravo      9.0
            [1]  1  alpha      4.0
            [2]  2  charlie   12.0
            [3]  1  bravo      5.0

            >>> mix_frame = frame.group_by('a', ta.agg.count, {'f': [ta.agg.avg, ta.agg.sum, ta.agg.min], 'g': ta.agg.max})
            [===Job Progress===]
            >>> mix_frame.inspect()
            [#]  a  count  g_MAX  f_AVG  f_SUM  f_MIN
            =========================================
            [0]  1      3      9    5.0   15.0    3.0
            [1]  2      4      7   6.25   25.0    5.0

            >>> def custom_agg(acc, row):
            ...     acc.c_sum = acc.c_sum + row.c
            ...     acc.c_prod= acc.c_prod*row.c

            >>> sum_prod_frame = frame.group_by(['a', 'b'], ta.agg.udf(aggregator=custom_agg,output_schema=[('c_sum', ta.float64),('c_prod', ta.float64)],init_values=[0,1]))
            [===Job Progress===]

            >>> sum_prod_frame.inspect()
            [#]  a  b        c_sum  c_prod
            ==============================
            [0]  2  bravo     27.0   672.0
            [1]  1  alpha      8.0    15.0
            [2]  2  charlie   12.0    12.0
            [3]  1  bravo      5.0     5.0

        For further examples, see :ref:`example_frame.group_by`.


        :param group_by_columns: Column name or list of column names
        :type group_by_columns: list
        :param *aggregation_arguments: (default=None)  Aggregation function based on entire row, and/or dictionaries (one or more) of { column name str : aggregation function(s) }.
        :type *aggregation_arguments: dict

        :returns: A new frame with the results of the group_by
        :rtype: Frame
        """
        return None


    @doc_stub
    def histogram(self, column_name, num_bins=None, weight_column_name=None, bin_type='equalwidth'):
        """
        Compute the histogram for a column in a frame.

        Compute the histogram of the data in a column.
        The returned value is a Histogram object containing 3 lists one each for:
        the cutoff points of the bins, size of each bin, and density of each bin.

        **Notes**

        The num_bins parameter is considered to be the maximum permissible number
        of bins because the data may dictate fewer bins.
        With equal depth binning, for example, if the column to be binned has 10
        elements with only 2 distinct values and the *num_bins* parameter is
        greater than 2, then the number of actual number of bins will only be 2.
        This is due to a restriction that elements with an identical value must
        belong to the same bin.

        Examples
        --------

        Consider the following sample data set\:

        .. code::

            >>> frame.inspect()
                [#]  a  b
                =========
                [0]  a  2
                [1]  b  7
                [2]  c  3
                [3]  d  9
                [4]  e  1

        A simple call for 3 equal-width bins gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3)
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 3.6666666666666665, 6.333333333333333, 9.0],
            hist: [3.0, 0.0, 2.0],
            density: [0.6, 0.0, 0.4]

        Switching to equal depth gives\:

        .. code::

            >>> hist = frame.histogram("b", num_bins=3, bin_type='equaldepth')
            [===Job Progress===]

            >>> print hist
            Histogram:
            cutoffs: [1.0, 2.0, 7.0, 9.0],
            hist: [1.0, 2.0, 2.0],
            density: [0.2, 0.4, 0.4]

        .. only:: html

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - hist.cutoffs[0])
        .. only:: latex

               Plot hist as a bar chart using matplotlib\:

            .. code::
                >>> import matplotlib.pyplot as plt

                >>> plt.bar(hist.cutoffs[:1], hist.hist, width=hist.cutoffs[1] - 
                ... hist.cutoffs[0])


        :param column_name: Name of column to be evaluated.
        :type column_name: unicode
        :param num_bins: (default=None)  Number of bins in histogram.
            Default is Square-root choice will be used
            (in other words math.floor(math.sqrt(frame.row_count)).
        :type num_bins: int32
        :param weight_column_name: (default=None)  Name of column containing weights.
            Default is all observations are weighted equally.
        :type weight_column_name: unicode
        :param bin_type: (default=equalwidth)  The type of binning algorithm to use: ["equalwidth"|"equaldepth"]
            Defaults is "equalwidth".
        :type bin_type: unicode

        :returns: histogram
                A Histogram object containing the result set.
                The data returned is composed of multiple components:
            cutoffs : array of float
                A list containing the edges of each bin.
            hist : array of float
                A list containing count of the weighted observations found in each bin.
            density : array of float
                A list containing a decimal containing the percentage of
                observations found in the total set per bin.
        :rtype: dict
        """
        return None


    @doc_stub
    def inspect(self, n=10, offset=0, columns=None, wrap='inspect_settings', truncate='inspect_settings', round='inspect_settings', width='inspect_settings', margin='inspect_settings', with_types='inspect_settings'):
        """
        Pretty-print of the frame data

        Essentially returns a string, but technically returns a RowInspection object which renders a string.
        The RowInspection object naturally converts to a str when needed, like when printed or when displayed
        by python REPL (i.e. using the object's __repr__).  If running in a script and want the inspect output
        to be printed, then it must be explicitly printed, then `print frame.inspect()`


        Examples
        --------
        To look at the first 4 rows of data in a frame:

        .. code::

            >>> frame.inspect(4)
            [#]  animal    name    age  weight
            ==================================
            [0]  human     George    8   542.5
            [1]  human     Ursula    6   495.0
            [2]  ape       Ape      41   400.0
            [3]  elephant  Shep      5  8630.0

        # For other examples, see :ref:`example_frame.inspect`.

        Note: if the frame data contains unicode characters, this method may raise a Unicode exception when
        running in an interactive REPL or otherwise which triggers the standard python repr().  To get around
        this problem, explicitly print the unicode of the returned object:

        .. code::

            >>> print unicode(frame.inspect())


        **Global Settings**

        If not specified, the arguments that control formatting receive default values from
        'trustedanalytics.inspect_settings'.  Make changes there to affect all calls to inspect.

        .. code::

            >>> import trustedanalytics as ta
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = 120  # changes inspect to use 120 width globally
            >>> ta.inspect_settings.truncate = 16  # changes inspect to always truncate strings to 16 chars
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width           120
            margin         None
            with_types    False
            >>> ta.inspect_settings.width = None  # return value back to default
            >>> ta.inspect_settings
            wrap             20
            truncate         16
            round          None
            width            80
            margin         None
            with_types    False
            >>> ta.inspect_settings.reset()  # set everything back to default
            >>> ta.inspect_settings
            wrap             20
            truncate       None
            round          None
            width            80
            margin         None
            with_types    False

        ..


        :param n: (default=10)  The number of rows to print (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before printing.
        :type offset: int
        :param columns: (default=None)  Filter columns to be included.  By default, all columns are included
        :type columns: int
        :param wrap: (default=inspect_settings)  If set to 'stripes' then inspect prints rows in stripes; if set to an integer N, rows will be printed in clumps of N columns, where the columns are wrapped
        :type wrap: int or 'stripes'
        :param truncate: (default=inspect_settings)  If set to integer N, all strings will be truncated to length N, including a tagged ellipses
        :type truncate: int
        :param round: (default=inspect_settings)  If set to integer N, all floating point numbers will be rounded and truncated to N digits
        :type round: int
        :param width: (default=inspect_settings)  If set to integer N, the print out will try to honor a max line width of N
        :type width: int
        :param margin: (default=inspect_settings)  ('stripes' mode only) If set to integer N, the margin for printing names in a stripe will be limited to N characters
        :type margin: int
        :param with_types: (default=inspect_settings)  If set to True, header will include the data_type of each column
        :type with_types: bool

        :returns: An object which naturally converts to a pretty-print string
        :rtype: RowsInspection
        """
        return None


    @doc_stub
    def join(self, right, left_on, right_on=None, how='inner', name=None):
        """
        Join operation on one or two frames, creating a new frame.

        Create a new frame from a SQL JOIN operation with another frame.
        The frame on the 'left' is the currently active frame.
        The frame on the 'right' is another frame.
        This method take column(s) in the left frame and matches its values
        with column(s) in the right frame.
        Using the default 'how' option ['inner'] will only allow data in the
        resultant frame if both the left and right frames have the same value
        in the matching column(s).
        Using the 'left' 'how' option will allow any data in the resultant
        frame if it exists in the left frame, but will allow any data from the
        right frame if it has a value in its column(s) which matches the value in
        the left frame column(s).
        Using the 'right' option works similarly, except it keeps all the data
        from the right frame and only the data from the left frame when it
        matches.
        The 'outer' option provides a frame with data from both frames where
        the left and right frames did not have the same value in the matching
        column(s).

        Notes
        -----
        When a column is named the same in both frames, it will result in two
        columns in the new frame.
        The column from the *left* frame (originally the current frame) will be
        copied and the column name will have the string "_L" added to it.
        The same thing will happen with the column from the *right* frame,
        except its name has the string "_R" appended. The order of columns
        after this method is called is not guaranteed.

        It is recommended that you rename the columns to meaningful terms prior
        to using the ``join`` method.
        Keep in mind that unicode in column names will likely cause the
        drop_frames() method (and others) to fail!

        Examples
        --------


        Consider two frames: codes and colors

        >>> codes.inspect()
        [#]  numbers
        ============
        [0]        1
        [1]        3
        [2]        1
        [3]        0
        [4]        2
        [5]        1
        [6]        5
        [7]        3


        >>> colors.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        2  yellow
        [2]        3  green
        [3]        4  blue


        Join them on the 'numbers' column ('inner' join by default)

        >>> j = codes.join(colors, 'numbers')
        [===Job Progress===]

        >>> j.inspect()
        [#]  numbers  color
        ====================
        [0]        1  red
        [1]        3  green
        [2]        1  red
        [3]        2  yellow
        [4]        1  red
        [5]        3  green

        (The join adds an extra column *_R which is the join column from the right frame; it may be disregarded)

        Try a 'left' join, which includes all the rows of the codes frame.

        >>> j_left = codes.join(colors, 'numbers', how='left')
        [===Job Progress===]

        >>> j_left.inspect()
        [#]  numbers_L  color
        ======================
        [0]          1  red
        [1]          3  green
        [2]          1  red
        [3]          0  None
        [4]          2  yellow
        [5]          1  red
        [6]          5  None
        [7]          3  green


        And an outer join:

        >>> j_outer = codes.join(colors, 'numbers', how='outer')
        [===Job Progress===]

        >>> j_outer.inspect()
        [#]  numbers_L  color
        ======================
        [0]          0  None
        [1]          1  red
        [2]          1  red
        [3]          1  red
        [4]          2  yellow
        [5]          3  green
        [6]          3  green
        [7]          4  blue
        [8]          5  None

        Consider two frames: country_codes_frame and country_names_frame

        >>> country_codes_frame.inspect()
        [#]  col_0  col_1  col_2
        ========================
        [0]      1    354  a
        [1]      2     91  a
        [2]      2    100  b
        [3]      3     47  a
        [4]      4    968  c
        [5]      5     50  c


        >>> country_names_frame.inspect()
        [#]  col_0  col_1     col_2
        ===========================
        [0]      1  Iceland   a
        [1]      1  Ice-land  a
        [2]      2  India     b
        [3]      3  Norway    a
        [4]      4  Oman      c
        [5]      6  Germany   c

        Join them on the 'col_0' and 'col_2' columns ('inner' join by default)

        >>> composite_join = country_codes_frame.join(country_names_frame, ['col_0', 'col_2'])
        [===Job Progress===]

        >>> composite_join.inspect()
        [#]  col_0  col_1_L  col_2  col_1_R
        ====================================
        [0]      1      354  a      Ice-land
        [1]      1      354  a      Iceland
        [2]      2      100  b      India
        [3]      3       47  a      Norway
        [4]      4      968  c      Oman

        More examples can be found in the :ref:`user manual
        <example_frame.join>`.


        :param right: Another frame to join with
        :type right: Frame
        :param left_on: Names of the columns in the left frame used to match up the two frames.
        :type left_on: list
        :param right_on: (default=None)  Names of the columns in the right frame used to match up the two frames. Default is the same as the left frame.
        :type right_on: list
        :param how: (default=inner)  How to qualify the data to be joined together.  Must be one of the following:  'left', 'right', 'inner', 'outer'.  Default is 'inner'
        :type how: str
        :param name: (default=None)  Name of the result grouped frame
        :type name: str

        :returns: A new frame with the results of the join
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def last_read_date(self):
        """
        Last time this frame's data was accessed.

        Examples
        --------

        .. code::

            >>> frame.last_read_date
            datetime.datetime(2015, 10, 8, 15, 48, 8, 791000, tzinfo=tzoffset(None, -25200))





        :returns: Date string of the last time this frame's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the frame object.

        Change or retrieve frame object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_frame.name
            "abc"

            >>> my_frame.name = "xyz"
            >>> my_frame.name
            "xyz"




        """
        return None


    @doc_stub
    def quantiles(self, column_name, quantiles):
        """
        New frame with Quantiles and their values.

        Calculate quantiles on the given column.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column *final_sale_price*:

        .. code::

            >>> my_frame.inspect()
            [#]  final_sale_price
            =====================
            [0]               100
            [1]               250
            [2]                95
            [3]               179
            [4]               315
            [5]               660
            [6]               540
            [7]               420
            [8]               250
            [9]               335

        To calculate 10th, 50th, and 100th quantile:

        .. code::

            >>> quantiles_frame = my_frame.quantiles('final_sale_price', [10, 50, 100])
            [===Job Progress===]

        A new Frame containing the requested Quantiles and their respective values
        will be returned :

        .. code::

           >>> quantiles_frame.inspect()
           [#]  Quantiles  final_sale_price_QuantileValue
           ==============================================
           [0]       10.0                            95.0
           [1]       50.0                           250.0
           [2]      100.0                           660.0


        :param column_name: The column to calculate quantiles.
        :type column_name: unicode
        :param quantiles: What is being requested.
        :type quantiles: list

        :returns: A new frame with two columns (float64): requested Quantiles and their respective values.
        :rtype: Frame
        """
        return None


    @doc_stub
    def rename_columns(self, names):
        """
        Rename columns for vertex frame.

        :param names: Dictionary of old names to new names.
        :type names: dict

        :returns: 
        :rtype: _Unit
        """
        return None


    @property
    @doc_stub
    def row_count(self):
        """
        Number of rows in the current frame.

        Counts all of the rows in the frame.

        Examples
        --------
        Get the number of rows:

        .. code::

            >>> frame.row_count
            4





        :returns: The number of rows in the frame
        :rtype: int
        """
        return None


    @property
    @doc_stub
    def schema(self):
        """
        Current frame column names and types.

        The schema of the current frame is a list of column names and
        associated data types.
        It is retrieved as a list of tuples.
        Each tuple has the name and data type of one of the frame's columns.

        Examples
        --------

        .. code::

            >>> frame.schema
            [(u'name', <type 'unicode'>), (u'age', <type 'numpy.int32'>), (u'tenure', <type 'numpy.int32'>), (u'phone', <type 'unicode'>)]

        Note how the types shown are the raw, underlying types used in python.  To see the schema in a friendlier
        format, used the __repr__ presentation, invoke by simply entering the frame:
            >>> frame
            Frame "example_frame"
            row_count = 4
            schema = [name:unicode, age:int32, tenure:int32, phone:unicode]
            status = ACTIVE  (last_read_date = -etc-)





        :returns: list of tuples of the form (<column name>, <data type>)
        :rtype: list
        """
        return None


    @doc_stub
    def sort(self, columns, ascending=True):
        """
        Sort the data in a frame.

        Sort a frame by column values either ascending or descending.

        Examples
        --------


        Consider the frame
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     1  charlie
            [2]     3  bravo
            [3]     2  echo
            [4]     4  delta
            [5]     3  alpha

        Sort a single column:

        .. code::

            >>> frame.sort('col1')
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  foxtrot
            [3]     3  bravo
            [4]     3  alpha
            [5]     4  delta

        Sort a single column descending:

        .. code::

            >>> frame.sort('col2', False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     3  foxtrot
            [1]     2  echo
            [2]     4  delta
            [3]     1  charlie
            [4]     3  bravo
            [5]     3  alpha

        Sort multiple columns:

        .. code::

            >>> frame.sort(['col1', 'col2'])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     1  charlie
            [1]     2  echo
            [2]     3  alpha
            [3]     3  bravo
            [4]     3  foxtrot
            [5]     4  delta


        Sort multiple columns descending:

        .. code::

            >>> frame.sort(['col1', 'col2'], False)
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  foxtrot
            [2]     3  bravo
            [3]     3  alpha
            [4]     2  echo
            [5]     1  charlie

        Sort multiple columns: 'col1' decending and 'col2' ascending:

        .. code::

            >>> frame.sort([ ('col1', False), ('col2', True) ])
            [===Job Progress===]
            >>> frame.inspect()
            [#]  col1  col2
            ==================
            [0]     4  delta
            [1]     3  alpha
            [2]     3  bravo
            [3]     3  foxtrot
            [4]     2  echo
            [5]     1  charlie



        :param columns: Either a column name, a list of column names, or a list of tuples where each tuple is a name and an ascending bool value.
        :type columns: str | list of str | list of tuples
        :param ascending: (default=True)  True for ascending, False for descending.
        :type ascending: bool
        """
        return None


    @doc_stub
    def sorted_k(self, k, column_names_and_ascending, reduce_tree_depth=None):
        """
        Get a sorted subset of the data.

        Take a number of rows and return them
        sorted in either ascending or descending order.

        Sorting a subset of rows is more efficient than sorting the entire frame when
        the number of sorted rows is much less than the total number of rows in the frame.

        Notes
        -----
        The number of sorted rows should be much smaller than the number of rows
        in the original frame.

        In particular:

        #)  The number of sorted rows returned should fit in Spark driver memory.
            The maximum size of serialized results that can fit in the Spark driver is
            set by the Spark configuration parameter *spark.driver.maxResultSize*.
        #)  If you encounter a Kryo buffer overflow exception, increase the Spark
            configuration parameter *spark.kryoserializer.buffer.max.mb*.
        #)  Use Frame.sort() instead if the number of sorted rows is very large (in
            other words, it cannot fit in Spark driver memory).

        Examples
        --------
        These examples deal with the most recently-released movies in a private collection.
        Consider the movie collection already stored in the frame below:

            >>> my_frame.inspect()
            [#]  genre      year  title
            ========================================================
            [0]  Drama      1957  12 Angry Men
            [1]  Crime      1946  The Big Sleep
            [2]  Western    1969  Butch Cassidy and the Sundance Kid
            [3]  Drama      1971  A Clockwork Orange
            [4]  Drama      2008  The Dark Knight
            [5]  Animation  2013  Frozen
            [6]  Drama      1972  The Godfather
            [7]  Animation  1994  The Lion King
            [8]  Animation  2010  Tangled
            [9]  Fantasy    1939  The WOnderful Wizard of Oz


        This example returns the top 3 rows sorted by a single column: 'year' descending:

            >>> topk_frame = my_frame.sorted_k(3, [ ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Drama      2008  The Dark Knight

        This example returns the top 5 rows sorted by multiple columns: 'genre' ascending, then 'year' descending:

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', False) ])
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            =====================================
            [0]  Animation  2013  Frozen
            [1]  Animation  2010  Tangled
            [2]  Animation  1994  The Lion King
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      2008  The Dark Knight


        This example returns the top 5 rows sorted by multiple columns: 'genre'
        ascending, then 'year' ascending.
        It also illustrates the optional tuning parameter for reduce-tree depth
        (which does not affect the final result).

            >>> topk_frame = my_frame.sorted_k(5, [ ('genre', True), ('year', True) ], reduce_tree_depth=1)
            [===Job Progress===]

            >>> topk_frame.inspect()
            [#]  genre      year  title
            ===================================
            [0]  Animation  1994  The Lion King
            [1]  Animation  2010  Tangled
            [2]  Animation  2013  Frozen
            [3]  Crime      1946  The Big Sleep
            [4]  Drama      1957  12 Angry Men




        :param k: Number of sorted records to return.
        :type k: int32
        :param column_names_and_ascending: Column names to sort by, and true to sort column by ascending order,
            or false for descending order.
        :type column_names_and_ascending: list
        :param reduce_tree_depth: (default=None)  Advanced tuning parameter which determines the depth of the
            reduce-tree (uses Spark's treeReduce() for scalability.)
            Default is 2.
        :type reduce_tree_depth: int32

        :returns: A new frame with a subset of sorted rows from the original frame.
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Current frame life cycle status.

        One of three statuses: ACTIVE, DROPPED, FINALIZED
           ACTIVE:    Entity is available for use
           DROPPED:   Entity has been dropped by user or by garbage collection which found it stale
           FINALIZED: Entity's data has been deleted

        Examples
        --------

        .. code::

            >>> frame.status
            u'ACTIVE'





        :returns: Status of the frame
        :rtype: str
        """
        return None


    @doc_stub
    def take(self, n, offset=0, columns=None):
        """
        Get data subset.

        Take a subset of the currently active Frame.

        Examples
        --------
        .. code::

            >>> frame.take(2)
            [[u'Fred', 39, 16, u'555-1234'], [u'Susan', 33, 3, u'555-0202']]

            >>> frame.take(2, offset=2)
            [[u'Thurston', 65, 26, u'555-4510'], [u'Judy', 44, 14, u'555-2183']]



        :param n: The number of rows to copy to this client from the frame (warning: do not overwhelm this client by downloading too much)
        :type n: int
        :param offset: (default=0)  The number of rows to skip before starting to copy
        :type offset: int
        :param columns: (default=None)  If not None, only the given columns' data will be provided.  By default, all columns are included
        :type columns: str | iterable of str

        :returns: A list of lists, where each contained list is the data for one row.
        :rtype: list
        """
        return None


    @doc_stub
    def tally(self, sample_col, count_val):
        """
        Count number of times a value is seen.

        A cumulative count is computed by sequentially stepping through the rows,
        observing the column values and keeping track of the number of times the specified
        *count_value* has been seen.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally
            ===================
            [0]    0        0.0
            [1]    1        1.0
            [2]    2        1.0
            [3]    0        1.0
            [4]    1        2.0
            [5]    2        2.0

        :param sample_col: The name of the column from which to compute the cumulative count.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def tally_percent(self, sample_col, count_val):
        """
        Compute a cumulative percent count.

        A cumulative percent count is computed by sequentially stepping through
        the rows, observing the column values and keeping track of the percentage of the
        total number of times the specified *count_value* has been seen up to
        the current value.

        Examples
        --------
        Consider Frame *my_frame*, which accesses a frame that contains a single
        column named *obs*:

            >>> my_frame.inspect()
            [#]  obs
            ========
            [0]    0
            [1]    1
            [2]    2
            [3]    0
            [4]    1
            [5]    2

        The cumulative percent count for column *obs* is obtained by:

            >>> my_frame.tally_percent("obs", "1")
            [===Job Progress===]

        The Frame *my_frame* accesses the original frame that now contains two
        columns, *obs* that contains the original column values, and
        *obsCumulativePercentCount* that contains the cumulative percent count:

            >>> my_frame.inspect()
            [#]  obs  obs_tally_percent
            ===========================
            [0]    0                0.0
            [1]    1                0.5
            [2]    2                0.5
            [3]    0                0.5
            [4]    1                1.0
            [5]    2                1.0



        :param sample_col: The name of the column from which to compute
            the cumulative sum.
        :type sample_col: unicode
        :param count_val: The column value to be used for the counts.
        :type count_val: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


    @doc_stub
    def timeseries_from_observations(self, date_time_index, timestamp_column, key_column, value_column):
        """
        Returns a frame that has the observations formatted as a time series.

        Uses the specified timestamp, key, and value columns and the date/time
                        index provided to format the observations as a time series.  The time series
                        frame will have columns for the key and a vector of the observed values that
                        correspond to the date/time index.

        Examples
        --------
        In this example, we will use a frame of observations of resting heart rate for
        three individuals over three days.  The data is accessed from Frame object
        called *my_frame*:


        .. code::

         >>> my_frame.inspect( my_frame.row_count )
         [#]  name     date                      resting_heart_rate
         ==========================================================
         [0]  Edward   2016-01-01T12:00:00.000Z                62.0
         [1]  Stanley  2016-01-01T12:00:00.000Z                57.0
         [2]  Edward   2016-01-02T12:00:00.000Z                63.0
         [3]  Sarah    2016-01-02T12:00:00.000Z                64.0
         [4]  Stanley  2016-01-02T12:00:00.000Z                57.0
         [5]  Edward   2016-01-03T12:00:00.000Z                62.0
         [6]  Sarah    2016-01-03T12:00:00.000Z                64.0
         [7]  Stanley  2016-01-03T12:00:00.000Z                56.0


        We then need to create an array that contains the date/time index,
        which will be used when creating the time series.  Since our data
        is for three days, our date/time index will just contain those
        three dates:

        .. code::

         >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z"]

        Then we can create our time series frame by specifying our date/time
        index along with the name of our timestamp column (in this example, it's
         "date"), key column (in this example, it's "name"), and value column (in
        this example, it's "resting_heart_rate").

        .. code::

         >>> ts = my_frame.timeseries_from_observations(datetimeindex, "date", "name", "resting_heart_rate")
         [===Job Progress===]

        Take a look at the resulting time series frame schema and contents:

        .. code::

         >>> ts.schema
         [(u'name', <type 'unicode'>), (u'resting_heart_rate', vector(3))]

         >>> ts.inspect()
         [#]  name     resting_heart_rate
         ================================
         [0]  Stanley  [57.0, 57.0, 56.0]
         [1]  Edward   [62.0, 63.0, 62.0]
         [2]  Sarah    [None, 64.0, 64.0]



        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param timestamp_column: The name of the column telling when the observation occurred.
        :type timestamp_column: unicode
        :param key_column: The name of the column that contains which string key the observation belongs to.
        :type key_column: unicode
        :param value_column: The name of the column that contains the observed value.
        :type value_column: unicode

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def timeseries_slice(self, date_time_index, start, end):
        """
        Returns a frame that is a sub-slice of the given series.

        Splits a time series frame on the specified start and end date/times.

        Examples
        --------
        For this example, we start with a frame that has already been formatted as a time series.
        This means that the frame has a string column for key and a vector column that contains
        a series of the observed values.  We must also know the date/time index that corresponds
        to the time series.

        The time series is in a Frame object called *ts_frame*.


        .. code::

            >>> ts_frame.inspect()
            [#]  key  series
            ==============================================
            [0]  A    [62.0, 55.0, 60.0, 61.0, 60.0, 59.0]
            [1]  B    [60.0, 58.0, 61.0, 62.0, 60.0, 61.0]
            [2]  C    [69.0, 68.0, 68.0, 70.0, 71.0, 69.0]

        Next, we define the date/time index.  In this example, it is one day intervals from
        2016-01-01 to 2016-01-06:

        .. code::

            >>> datetimeindex = ["2016-01-01T12:00:00.000Z","2016-01-02T12:00:00.000Z","2016-01-03T12:00:00.000Z","2016-01-04T12:00:00.000Z","2016-01-05T12:00:00.000Z","2016-01-06T12:00:00.000Z"]

        Get a slice of our time series from 2016-01-02 to 2016-01-04:

        .. code::
            >>> slice_start = "2016-01-02T12:00:00.000Z"
            >>> slice_end = "2016-01-04T12:00:00.000Z"

            >>> sliced_frame = ts_frame.timeseries_slice(datetimeindex, slice_start, slice_end)
            [===Job Progress===]

        Take a look at our sliced time series:

        .. code::

            >>> sliced_frame.inspect()
            [#]  key  series
            ============================
            [0]  A    [55.0, 60.0, 61.0]
            [1]  B    [58.0, 61.0, 62.0]
            [2]  C    [68.0, 68.0, 70.0]


        :param date_time_index: DateTimeIndex to conform all series to.
        :type date_time_index: list
        :param start: The start date for the slice in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ 
        :type start: datetime
        :param end: The end date for the slice (inclusive) in the ISO 8601 format, like: yyyy-MM-dd'T'HH:mm:ss.SSSZ.
        :type end: datetime

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def top_k(self, column_name, k, weights_column=None):
        """
        Most or least frequent column values.

        Calculate the top (or bottom) K distinct values by count of a column.
        The column can be weighted.
        All data elements of weight <= 0 are excluded from the calculation, as are
        all data elements whose weight is NaN or infinite.
        If there are no data elements of finite weight > 0, then topK is empty.

        Examples
        --------
        For this example, we calculate the top 5 movie genres in a data frame:
        Consider the following frame containing four columns.

        >>> frame.inspect()
            [#]  rank  city         population_2013  population_2010  change  county
            ============================================================================
            [0]     1  Portland              609456           583776  4.40%   Multnomah
            [1]     2  Salem                 160614           154637  3.87%   Marion
            [2]     3  Eugene                159190           156185  1.92%   Lane
            [3]     4  Gresham               109397           105594  3.60%   Multnomah
            [4]     5  Hillsboro              97368            91611  6.28%   Washington
            [5]     6  Beaverton              93542            89803  4.16%   Washington
            [6]    15  Grants Pass            35076            34533  1.57%   Josephine
            [7]    16  Oregon City            34622            31859  8.67%   Clackamas
            [8]    17  McMinnville            33131            32187  2.93%   Yamhill
            [9]    18  Redmond                27427            26215  4.62%   Deschutes
        >>> top_frame = frame.top_k("county", 2)
        [===Job Progress===]
        >>> top_frame.inspect()
            [#]  county      count
                ======================
                [0]  Washington    4.0
                [1]  Clackamas     3.0

















        :param column_name: The column whose top (or bottom) K distinct values are
            to be calculated.
        :type column_name: unicode
        :param k: Number of entries to return (If k is negative, return bottom k).
        :type k: int32
        :param weights_column: (default=None)  The column that provides weights (frequencies) for the topK calculation.
            Must contain numerical data.
            Default is 1 for all items.
        :type weights_column: unicode

        :returns: An object with access to the frame of data.
        :rtype: Frame
        """
        return None


    @doc_stub
    def unflatten_columns(self, columns, delimiter=None):
        """
        Compacts data from multiple rows based on cell data.

        Groups together cells in all columns (less the composite key) using "," as string delimiter.
        The original rows are deleted.
        The grouping takes place based on a composite key created from cell values.
        The column datatypes are changed to string.

        Examples
        --------
        Given a data file::

            user1 1/1/2015 1 70
            user1 1/1/2015 2 60
            user2 1/1/2015 1 65

        The commands to bring the data into a frame, where it can be worked on:

        .. only:: html

            .. code::

                >>> my_csv = ta.CsvFile("original_data.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        .. only:: latex

            .. code::

                >>> my_csv = ta.CsvFile("unflatten_column.csv", schema=[('a', str), ('b', str),('c', int32) ,('d', int32)])
                >>> frame = ta.Frame(source=my_csv)

        Looking at it:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c  d
            ===========================
            [0]  user1  1/1/2015  1  70
            [1]  user1  1/1/2015  2  60
            [2]  user2  1/1/2015  1  65


        Unflatten the data using columns a & b:

        .. code::

            >>> frame.unflatten_columns(['a','b'])
            [===Job Progress===]

        Check again:

        .. code::

            >>> frame.inspect()
            [#]  a      b         c    d
            ================================
            [0]  user2  1/1/2015  1    65
            [1]  user1  1/1/2015  1,2  70,60

        Alternatively, unflatten_columns() also accepts a single column like:


        .. code::

            >>> frame.unflatten_columns('a')
            [===Job Progress===]

            >>> frame.inspect()
            [#]  a      b                  c    d
            =========================================
            [0]  user1  1/1/2015,1/1/2015  1,2  70,60
            [1]  user2  1/1/2015           1    65


        :param columns: Name of the column(s) to be used as keys
            for unflattening.
        :type columns: list
        :param delimiter: (default=None)  Separator for the data in the result columns.
            Default is comma (,).
        :type delimiter: unicode

        :returns: 
        :rtype: _Unit
        """
        return None


del doc_stub
del DocStubCalledError