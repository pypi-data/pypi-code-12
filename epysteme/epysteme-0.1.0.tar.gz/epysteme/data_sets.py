# -*- coding: utf-8 -*-
"""Data sets and related classes and functions for epysteme.

Author: Stefan Peterson
"""

# from db_interfacing import Database
import tempfile
import sqlite3
import os
import random
import itertools
import weakref

# noinspection PyPackageRequirements
import numpy as np


class _BaseDataSet(object):
    """Base class for data sets.

    Parameters
    ----------

    """

    def __init__(self):
        self.features = dict()
        self.crs = None

    def add_polynomial_features(self, base_feature, degree):
        """Add polynomial features of a base feature to the data set.

        Polynomial features are named <base_feature_name>_poly_<degree> and are
        computed on demand rather than stored in the database.

        Parameters
        ----------
        base_feature : str
            Name of the base feature.
        degree : int
            Maximum degree of the polynomial features.
        """
        if self.crs is None:
            raise Exception("Instance has no cursor")

        if base_feature not in self.features:
            raise ValueError("Feature '%s' not found in data set"
                             % base_feature)
        if degree < 2:
            raise ValueError("Degree must be at least 2")

        # Add to PolynomialFeatures table
        if isinstance(self, DataSet):
            self.crs.execute("INSERT INTO PolynomialFeatures (Feature, Degree) "
                             "VALUES (?, ?)", (base_feature, degree))

        # Add to features
        for poly_degree in range(2, degree + 1):
            poly_name = "%s_poly_%d" % (base_feature, poly_degree)
            if poly_degree == 1:
                self.features[poly_name] = self.features[base_feature]
            else:
                self.features[poly_name] = PolynomialFeature(
                    self.features[base_feature], poly_degree)


class DataSet(_BaseDataSet):
    """Default Epysteme data set class.

    Data is stored out-of-memory in an SQLite database.
    """

    def __init__(self, features=None):
        """Initialize a DataSet object.

        Parameters
        ----------
        features : optional[iterable[(str, type)]]
            Feature tuples on the form (name, type).
        """
        super().__init__()
        self.db_file = tempfile.mktemp('.db', 'epysteme_')
        self.db_connection = sqlite3.connect(self.db_file)
        self.crs = self.db_connection.cursor()
        self.n_observations = 0

        # Create the main table
        self.crs.execute(
            "CREATE TABLE Epysteme("
            "Idx INT PRIMARY KEY NOT NULL, "
            "Subset INT, "
            "RandomNumber FLOAT)")

        self.crs.execute(
            "CREATE TABLE PolynomialFeatures("
            "Feature VARCHAR(50) PRIMARY KEY NOT NULL, "
            "Degree INT)")

        # Add any features
        self.features = dict()
        self.ordered_features = []
        if features is not None:
            for feature in features:
                self.add_feature(*feature)

        self.subsets = dict()

        # # Dynamically define some methods (pretty cool, huh?)
        # if type(set_base) == Database:
        #     def add_feature():
        #         pass
        #
        # setattr(self, "add_feature", add_feature)
        #
        # for feature in features:
        #     self.add_feature(feature)

    def __del__(self):
        os.remove(self.db_file)

    def __getitem__(self, key):
        if key in self.subsets:
            return self.subsets[key]
        if key in self.features:
            self.crs.execute("SELECT %s FROM Epysteme"
                             % self.features[key].sql_name)
            return [value[0] for value in self.crs.fetchall()]
        elif isinstance(key, int):       # is an index
            feature_string = ', '.join([self.features[feature].sql_name
                                        for feature in self.ordered_features])
            self.crs.execute("SELECT %s FROM Epysteme WHERE Idx=%d"
                             % (feature_string, key))
            return [value for value in self.crs.fetchone()]
        else:
            raise KeyError("%s is neither a feature nor an index of data set")

    def add_feature(self, name, data_type):
        """Add a feature to the data set.

        Parameters
        ----------
        name : str
            Name of the feature.
        data_type : type
            Type (python type) of the feature.
        """
        self.features[name] = Feature(name,
                                      data_type=data_type,
                                      _data_set=self)
        self.ordered_features.append(name)

    def add_observation(self, observation):
        """Add an observation to the data set.

        Parameters
        ----------
        observation : iterable
            Values for each of the features in the data set, ordered as in the
            attribute 'ordered_features'.
        """
        n_features = len(self.ordered_features)
        extended_observation = [self.n_observations, random.random(), -1]
        extended_observation.extend(observation)
        columns_string = 'Idx, Subset, RandomNumber, ' + ', '.join(
            self.features[feature].sql_name
            for feature in self.ordered_features)
        values_string = ('?, ' * (3 + n_features))[:-2]
        self.crs.execute("INSERT INTO Epysteme (%s) VALUES (%s)"
                         % (columns_string, values_string),
                         extended_observation)
        self.n_observations += 1

    def random_split(self, split_ratios):
        """Randomly split observations into subsets.

        Parameters
        ----------
        split_ratios : {str: float}
            A dict of subset names and proportions. Proportions are relative,
            so {'subset 1': 1, 'subset 2': 3} is functionally equivalent to
            {'subset 1': 0.25, 'subset 2': 0.75}.
        """
        # Clear old subsets
        self.subsets = dict()

        # Compute normalized split ratio, group sizes and boundaries
        split_tuples = [(key, value) for key, value in split_ratios.items()]
        names = [t[0] for t in split_tuples]
        ratios = [t[1] for t in split_tuples]

        n_subsets = len(ratios)
        sr_sum = sum(ratios)
        normalized_split_ratio = [r/sr_sum for r in ratios]
        subset_boundaries = list(itertools.accumulate(normalized_split_ratio))
        subset_sizes = [0 for _ in range(n_subsets)]
        target_subset_sizes = [round(r * self.n_observations)
                               for r in normalized_split_ratio]
        excess = sum(target_subset_sizes) - self.n_observations
        for k in range(excess):
            target_subset_sizes[-(k + 1)] -= 1

        # Empty the Groups table and assign new groups
        # TODO: work in batches instead of elements
        self.crs.execute("UPDATE Epysteme SET Subset=-1")
        for k in range(self.n_observations):
            r = random.random()
            this_subset = n_subsets - 1
            for kk in range(n_subsets):
                if subset_boundaries[kk] >= r:
                    this_subset = kk
                    break

            self.crs.execute(
                "UPDATE Epysteme SET Subset=%d WHERE Idx=%d"
                % (this_subset, k))

            subset_sizes[this_subset] += 1
            subset_full = subset_sizes[this_subset] == \
                target_subset_sizes[this_subset]
            if k < (self.n_observations - 1) and subset_full:
                ratios[this_subset] = 0
                sr_sum = sum(ratios)
                normalized_split_ratio = [r / sr_sum for r in ratios]
                subset_boundaries = list(
                    itertools.accumulate(normalized_split_ratio))
                subset_boundaries = [
                    subset_boundaries[k] if ratios[k] > 0 else -2
                    for k in range(n_subsets)]

        # Create new subsets and randomize their order
        self.subsets = {name: subset_idx
                        for name, subset_idx in zip(names, range(n_subsets))}
        
    def windows(self, features, target=None, const=False):
        """Yield windows of the data set for models.

        Each window is a primary numpy.ndarray and optionally a secondary
        column vector.

        Parameters
        ----------
        features : iterable[str]
            Names of features to be included.
        target : optional[str]
            A target feature to be yielded as a separate column vector.
            If None (default), only the primary array is yielded.
        const : optional[bool]
            If True, the first column of the primary array is ones.
            Default is False.

        Yields
        ------
        numpy.ndarray
            Primary array of feature observations.
        optional[numpy.ndarray]
            Secondary column vector of target feature observations.
        """
        m = len(features) + 1 if const is True else len(features)
        chunk_size = max(m, 500)  # TODO: smarter rule

        x = np.zeros((chunk_size, m))
        y = np.zeros((chunk_size, 1))
        if const is True:
            x_offset = 1
            x[:, 0] = 1
        else:
            x_offset = 0

        sql_features = [[], []]
        derived_features = []
        f_c_dict = dict()
        for feature, col in zip(features, range(x_offset, m)):
            if feature in self.ordered_features:
                sql_features[0].append(self.features[feature].sql_name)
                sql_features[1].append(col)
                f_c_dict[feature] = col
            else:
                derived_features.append([
                    self.features[feature].lda,
                    col,
                    self.features[feature].base_feature.name])

        n_sql_features = len(sql_features[1])

        # Find parent columns
        k = -1
        for feature in derived_features:
            if feature[2] in f_c_dict:
                feature[2] = f_c_dict[feature[2]]
            else:
                sql_features[0].append(self.features[feature[2]].sql_name)
                feature[2] = k
                k -= 1

        p = np.zeros((chunk_size, -(k + 1)))

        if target in self.ordered_features:
            sql_features[0].append(self.features[target].sql_name)
            # derived_target = False
        else:
            # derived_target = True
            pass

        # noinspection PyTypeChecker
        self.crs.execute("SELECT %s FROM Epysteme ORDER BY RandomNumber"
                         % ', '.join(sql_features[0]))

        for k in range(self.n_observations):
            row = k % chunk_size
            a = self.crs.fetchone()
            x[row, sql_features[1]] = a[:n_sql_features]
            p[row] = a[n_sql_features:-1]
            y[row] = a[-1]

            if row == chunk_size - 1:
                # Compute derived features
                for lda, col, parent_col in derived_features:
                    if parent_col < 0:
                        x[:, col] = lda(x[:, -(parent_col + 1)])
                    else:
                        x[:, col] = lda(x[:, parent_col])
                yield x, y

        final = self.n_observations % chunk_size
        # Compute derived features
        for lda, col, parent_col in derived_features:
            if parent_col < 0:
                x[:final, col] = lda(p[:final, -(parent_col + 1)])
            else:
                x[:final, col] = lda(x[:final, parent_col])
        yield x[:final], y[:final]


class ForeignDataSet(_BaseDataSet):
    """Data set from a pre-existing database.

    Epysteme currently supports SQLite only. MySQL and MSSQL are on the to-do
    list.
    """

    def __init__(self, db_parameters, features=None):
        """Initialize a DataSet object.

        Parameters
        ----------
        db_parameters : dict
            database connection information
        features : optional[iterable[(str, type)]]
            Feature tuples on the form (name, table, column, idx_column,
            demux, demux_values). See add_feature for details.
        """
        super().__init__()
        if db_parameters['db_type'].lower() == 'sqlite':
            self.db_file = db_parameters['file']
            self.db_connection = sqlite3.connect(self.db_file)
            self.crs = self.db_connection.cursor()

        self.n_observations = 0
        # self.primary_key = db_parameters['primary key']
        self.features = dict()
        self.proper_features = []
        self.subsets = dict()

        if features is not None:
            for feature in features:
                self.add_feature(*feature)

    def add_feature(self,
                    name,
                    table,
                    column,
                    idx_column,
                    demux=None,
                    demux_values=None):
        """Add a feature to the data set.

        Parameters
        ----------
        name : str
            Name of the feature.
        table : str
            Name of the table the feature belongs to.
        column : str
            Column name in table for the feature.
        idx_column : str
            Column name in table for the index key.
        demux : optional[str]
            Column name in table for a demultiplexer, default is None.
        demux_values : optional
            Values to use from the demultiplexer column
        """
        get_n_observations = False if len(self.features) > 0 else True

        if demux is not None:
            if demux_values is None:
                self.crs.execute("SELECT DISTINCT %s FROM %s" % (demux, table))
                demux_values = [val[0] for val in self.crs.fetchall()]
        else:
            demux_values = [None]

        for demux_val in demux_values:
            if demux_val is not None:
                table_alias = "%s_%s_%s" % (table, demux, demux_val)
                demux_tuple = (demux, demux_val)
                compound_name = "%s_%s_%s" % (name, demux, demux_val)
            else:
                demux_tuple = None
                table_alias = None
                compound_name = name

            self.features[compound_name] = ForeignFeature(compound_name,
                                                          table,
                                                          column,
                                                          idx_column,
                                                          table_alias,
                                                          demux_tuple)
            self.proper_features.append(compound_name)

        if get_n_observations:
            if demux_values[0] is None:
                self.crs.execute("SELECT %s FROM %s" % (idx_column, table))
            else:
                self.crs.execute("SELECT %s FROM %s WHERE %s = %s" % (
                    idx_column, table, demux, demux_values[0]))
            self.n_observations = len(self.crs.fetchall())

    def windows(self, features, target=None, const=False):
        """Yield windows of the data set for models.

        Each window is a primary numpy.ndarray and optionally a secondary
        column vector.

        Parameters
        ----------
        features : iterable[str]
            Names of features to be included.
        target : optional[str]
            A target feature to be yielded as a separate column vector.
            If None (default), only the primary array is yielded.
        const : optional[bool]
            If True, the first column of the primary array is ones.
            Default is False.

        Yields
        ------
        numpy.ndarray
            Primary array of feature observations.
        optional[numpy.ndarray]
            Secondary column vector of target feature observations.
        """
        m = len(features) + 1 if const is True else len(features)
        chunk_size = max(m, 500)  # TODO: smarter rule and move to helper

        x = np.zeros((chunk_size, m))
        y = np.zeros((chunk_size, 1))
        if const is True:
            x_offset = 1
            x[:, 0] = 1
        else:
            x_offset = 0

        # TODO: rename sql_features -> something relevant
        sql_features = [[], [], [], []]
        derived_features = []
        f_c_dict = dict()
        master_idx = None
        tables = []
        for feature, col in zip(features, range(x_offset, m)):
            if isinstance(self.features[feature], ForeignFeature):
                sql_features[0].append(self.features[feature].sql_name)
                if self.features[feature].sql_table_name not in tables:
                    sql_features[1].append(
                        self.features[feature].sql_table_name)
                    tables.append(self.features[feature].sql_table_name)

                if master_idx is not None:
                    # noinspection PyTypeChecker
                    sql_features[2].append("%s = %s" % (
                        self.features[feature].idx_column, master_idx))
                else:
                    master_idx = self.features[feature].idx_column

                if self.features[feature].demux_condition is not None:
                    sql_features[2].append(
                        self.features[feature].demux_condition)

                sql_features[3].append(col)
                f_c_dict[feature] = col
            else:
                derived_features.append([
                    self.features[feature].lda,
                    col,
                    self.features[feature].base_feature.name])

        n_sql_features = len(sql_features[1])

        # Find parent columns
        k = -1
        for feature in derived_features:
            if feature[2] in f_c_dict:
                feature[2] = f_c_dict[feature[2]]
            else:
                sql_features[0].append(self.features[feature[2]].sql_name)
                sql_features[1].append(self.features[feature[2]].sql_table_name)
                # noinspection PyTypeChecker
                sql_features[2].append("%s = %s" % (
                    self.features[feature[2]].idx_column, master_idx))
                if self.features[feature[2]].demux_condition is not None:
                    sql_features[2].append(
                        self.features[feature[2]].demux_condition)
                feature[2] = k
                k -= 1

        p = np.zeros((chunk_size, -(k + 1)))

        if target in self.proper_features:
            # TODO: functionalize these steps
            sql_features[0].append(self.features[target].sql_name)
            sql_features[1].append(self.features[target].sql_table_name)
            # noinspection PyTypeChecker
            sql_features[2].append("%s = %s" % (
                self.features[target].idx_column, master_idx))
            if self.features[target].demux_condition is not None:
                sql_features[2].append(
                    self.features[target].demux_condition)
            # derived_target = False
        else:
            # derived_target = True
            pass

        # noinspection PyTypeChecker
        query = "SELECT %s FROM %s ON (%s)" % (', '.join(sql_features[0]),
                                               " JOIN ".join(sql_features[1]),
                                               " AND ".join(sql_features[2]))

        self.crs.execute(query)

        for k in range(self.n_observations):
            row = k % chunk_size
            a = self.crs.fetchone()
            x[row, sql_features[3]] = a[:n_sql_features]
            p[row] = a[n_sql_features:-1]
            y[row] = a[-1]

            if row == chunk_size - 1:
                # Compute derived features
                for lda, col, parent_col in derived_features:
                    if parent_col < 0:
                        x[:, col] = lda(x[:, -(parent_col + 1)])
                    else:
                        x[:, col] = lda(x[:, parent_col])

                yield x, y

        final = self.n_observations % chunk_size
        # Compute derived features
        for lda, col, parent_col in derived_features:
            if parent_col < 0:
                x[:final, col] = lda(p[:final, -(parent_col + 1)])
            else:
                x[:final, col] = lda(x[:final, parent_col])

        yield x[:final], y[:final]

# class Subset(object):
#     def __init__(self, data_set, subset_idx):
#         self._data_set = weakref.ref(data_set)
#         self.subset_idx = subset_idx
#
#         data_set.crs.execute("SELECT Subset FROM Epysteme WHERE Subset=%d"
#                              % self.subset_idx)
#         self.n_observations = len(data_set.crs.fetchall())
#
#     def __get__(self, key):
#         if key in self._data_set().features:
#             self._data_set().crs.execute(
#                 "SELECT %s FROM Epysteme"
#                 % self._data_set().features[key].sql_name)
#             return [value[0] for value in self._data_set().crs.fetchall()]
#         elif isinstance(key, int):  # is an index
#             feature_string = ', '.join(
#                 [self._data_set().features[feature].sql_name
#                  for feature in self._data_set().ordered_features])
#             self._data_set().crs.execute("SELECT %s FROM Epysteme WHERE "
#                                          "Subset=%d" % (feature_string,
#                                                         key))
#             return [value for value in self._data_set().crs.fetchone()]
#         else:
#             raise KeyError("%s is neither a feature nor an index of subset")
#
#     def windows(self, features, target, const=False):
#         # TODO: inherit from DataSet or perhaps remove subset class entirely?
#         m = len(features) + 1 if const is True else len(features)
#         chunk_size = max(m, 500)  # TODO: smarter rule
#
#         x = np.zeros((chunk_size, m))
#         y = np.zeros((chunk_size, 1))
#         if const is True:
#             x_offset = 1
#             x[:, 0] = 1
#         else:
#             x_offset = 0
#
#         sql_features = [self._data_set().features[feature].sql_name
#                         for feature in features]
#         sql_features.append(self.features[target].sql_name)
#
#         self._data_set().crs.execute("SELECT %s FROM Epysteme ORDER BY "
#                                      "RandomNumber" % ', '.join(sql_features))
#
#         for k in range(self.n_observations):
#             row = k % chunk_size
#             a = self.crs.fetchone()
#             x[row, x_offset:] = a[:-1]
#             y[row] = a[-1]
#             if row == chunk_size - 1:
#                 yield x, y
#
#         final = self.n_observations % chunk_size
#         yield x[:final], y[:final]


class Feature(object):
    def __init__(self,
                 name,
                 data_type,
                 _data_set=None):
        self._data_set = None
        self.name = name
        self.sql_name = self.name.replace(' ', '_')
        self.type = data_type

        if data_type == int:
            self._sql_type = 'INT'
        elif data_type == float:
            self._sql_type = 'FLOAT'
        elif data_type == str:
            self._sql_type = 'VARCHAR(255)'
        else:
            raise ValueError("Type %s is not yet supported" % data_type)

        if _data_set is not None:
            self._attach(_data_set)

    def _attach(self, data_set):
        self._data_set = weakref.ref(data_set)
        self._data_set().crs.execute("ALTER TABLE Epysteme ADD COLUMN %s %s"
                                     % (self.sql_name, self._sql_type))
        # if self._values is not None:
        #     for idx, value in self._values:
        #         self._data_set().crs.execute("UPDATE TABLE Epysteme
        # SET %s=? WHERE Idx=?" % self.name, (value, idx))
        #     self._values = None


class PolynomialFeature(object):
    def __init__(self, base_feature, degree):
        self.base_feature = base_feature
        self.degree = degree
        self.lda = lambda x: x**degree


class ForeignFeature(object):
    def __init__(self,
                 name,
                 table,
                 column,
                 idx_column,
                 table_alias=None,
                 demux=None):
        self.name = name

        if table_alias is not None:
            self.sql_name = "%s.%s" % (table_alias, column)
            self.idx_column = "%s.%s" % (table_alias, idx_column)
            self.sql_table_name = "%s AS %s" % (table, table_alias)
            self.demux_condition = None if demux is None else "%s.%s = %s" % (
                table_alias, demux[0], demux[1])
        else:
            self.sql_name = "%s.%s" % (table, column)
            self.idx_column = "%s.%s" % (table, idx_column)
            self.sql_table_name = table
            self.demux_condition = None if demux is None else "%s.%s = %s" % (
                table, demux[0], demux[1])
