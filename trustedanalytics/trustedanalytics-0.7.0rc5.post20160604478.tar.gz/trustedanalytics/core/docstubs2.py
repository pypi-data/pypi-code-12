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

# Auto-generated file for API static documentation stubs (2016-06-04T19:51:59.924657)
#
# **DO NOT EDIT**

from trustedanalytics.meta.docstub import doc_stub, DocStubCalledError



__all__ = ["ArimaModel", "ArxModel", "CollaborativeFilteringModel", "CoxPhModel", "DaalKMeansModel", "DaalLinearRegressionModel", "DaalNaiveBayesModel", "DaalPrincipalComponentsModel", "GmmModel", "KMeansModel", "LdaModel", "LibsvmModel", "LinearRegressionModel", "LogisticRegressionModel", "NaiveBayesModel", "PowerIterationClusteringModel", "PrincipalComponentsModel", "RandomForestClassifierModel", "RandomForestRegressorModel", "SvmModel", "drop", "drop_frames", "drop_graphs", "drop_models", "get_frame", "get_frame_names", "get_graph", "get_graph_names", "get_model", "get_model_names"]

@doc_stub
class ArimaModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of an Autoregressive Integrated Moving Average (ARIMA) model.

        An autoregressive integrated moving average (ARIMA) [1]_ model is a
        generalization of an autoregressive moving average (ARMA) model.
        These models are fitted to time series data either to better understand
        the data or to predict future points in the series (forecasting).
        Non-seasonal ARIMA models are generally denoted ARIMA (p,d,q) where
        parameters p, d, and q are non-negative integers, p is the order of the
        Autoregressive model, d is the degree of differencing, and q is the order
        of the Moving-average model.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average
            

        Consider the following frame of observations collected over seven days.

        The frame has three columns: timestamp, name, and value.

        >>> frame.inspect()
        [#]  timestamp                 name   value
        =================================================
        [0]  2015-01-01T00:00:00.000Z  Sarah  12.88969427
        [1]  2015-01-02T00:00:00.000Z  Sarah  13.54964408
        [2]  2015-01-03T00:00:00.000Z  Sarah   13.8432745
        [3]  2015-01-04T00:00:00.000Z  Sarah  12.13843611
        [4]  2015-01-05T00:00:00.000Z  Sarah  12.81156092
        [5]  2015-01-06T00:00:00.000Z  Sarah   14.2499628
        [6]  2015-01-07T00:00:00.000Z  Sarah  15.12102595



        Define the date time index:

        >>> datetimeindex = ['2015-01-01T00:00:00.000Z','2015-01-02T00:00:00.000Z',
        ... '2015-01-03T00:00:00.000Z','2015-01-04T00:00:00.000Z','2015-01-05T00:00:00.000Z',
        ... '2015-01-06T00:00:00.000Z','2015-01-07T00:00:00.000Z']

        Then, create a time series frame from the frame of observations, since the ARIMA model
        expects data to be in a time series format (where the time series values are in a
        vector column).

        >>> ts = frame.timeseries_from_observations(datetimeindex, "timestamp","name","value")
        [===Job Progress===]

        >>> ts.inspect()
        [#]  name
        ==========
        [0]  Sarah
        <BLANKLINE>
        [#]  value
        ================================================================================
        [0]  [12.88969427, 13.54964408, 13.8432745, 12.13843611, 12.81156092, 14.2499628, 15.12102595]


        Use the frame take function to get one row of data with just the "value" column

        >>> ts_frame_data = ts.take(n=1,offset=0,columns=["value"])

        From the ts_frame_data, get the first row and first column to extract out just the time series values.

        >>> ts_values = ts_frame_data[0][0]

        >>> ts_values
        [12.88969427,
         13.54964408,
         13.8432745,
         12.13843611,
         12.81156092,
         14.2499628,
         15.12102595]

        Create an ARIMA model:

        >>> model = ta.ArimaModel()
        [===Job Progress===]

        Train the model using the timeseries frame:

        >>> model.train(ts_values, 1, 0, 1)
        [===Job Progress===]
        {u'coefficients': [9.864444620964322, 0.2848511106449633, 0.47346114378593795]}

        Call predict to future periods:

        >>> model.predict(ts_values, 0)
        [===Job Progress===]
        {u'forecasted': [12.674342627141744,
          13.638048984791693,
          13.682219498657313,
          13.883970022400577,
          12.49564914570843,
          13.66340392811346,
          14.201275185574925]}

        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine:

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Post a request to get the metadata about the model.

        >>> r = requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"ARIMA Model","model_class":"com.cloudera.sparkts.models.ARIMAModel","model_reader":"org.trustedanalytics.atk.scoring.models.ARIMAModelReaderPlugin","custom_values":{}},"input":[{"name":"timeseries","value":"Array[Double]"},{"name":"future","value":"Int"}],"output":[{"name":"timeseries","value":"Array[Double]"},{"name":"future","value":"Int"},{"name":"predicted_values","value":"Array[Double]"}]}'

        The ARIMA model only supports version 2 of the scoring engine.  In the following example, we send the historical
        time series value and specify to forecast 0 periods beyond the length of the time series provided.  This means that
        since 7 historical time series values were provided, 7 future periods will be forecasted.

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v2/score',json={"records":[{"timeseries":[12.88969427,13.54964408,13.8432745,12.13843611,12.81156092,14.2499628,15.12102595],"future":0}]})

        The 'predicted_values' array contains the future values, which have been forecasted based on the historical data.

        >>> r.text
        u'{"data":[{"timeseries":[12.88969427,13.54964408,13.8432745,12.13843611,12.81156092,14.2499628,15.12102595],"future":0.0,"predicted_values":[12.674342627141744,13.638048984791693,13.682219498657313,13.883970022400577,12.49564914570843,13.66340392811346,14.201275185574925]}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of ARIMAModel
        :rtype: ArimaModel
        """
        raise DocStubCalledError("model:arima/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, timeseries_values, future_periods):
        """
        Forecasts future periods using ARIMA.

        Provided fitted values of the time series as 1-step ahead forecasts, based
        on current model parameters, then provide future periods of forecast.  We assume
        AR terms prior to the start of the series are equal to the model's intercept term
        (or 0.0, if fit without an intercept term).  Meanwhile, MA terms prior to the start
        are assumed to be 0.0.  If there is differencing, the first d terms come from the
        original series.

        See :doc: 'here <new>' for examples.

        :param timeseries_values: Time series values to use as the gold standard.
        :type timeseries_values: list
        :param future_periods: Number of periods in the future to forecast (beyond the length the time series)
        :type future_periods: int32

        :returns: A series of 1-step ahead forecasts for historicals and then future periods
            of forecasts.
        :rtype: dict
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the ARIMA Model and its implementation into a tar
        file.  The tar file is then published on HDFS and this method returns the path to
        to the tar file.  The tar file serves as input to the scoring engine.
        This model can then be used to predict future values.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file.
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, timeseries_values, p, d, q, include_intercept=True, method='css-cgd', user_init_params=None):
        """
        Creates Autoregressive Integrated Moving Average (ARIMA) Model from the specified time series values.

        Given a time series, fits an non-seasonal Autoregressive Integrated Moving Average (ARIMA) model of
        order (p, d, q) where p represents the autoregression terms, d represents the order of differencing,
        and q represents the moving average error terms.  If includeIntercept is true, the model is fitted
        with an intercept.

        See :doc: 'here <new>' for examples.

        :param timeseries_values: List of time series values.
        :type timeseries_values: list
        :param p: Autoregressive order
        :type p: int32
        :param d: Differencing order
        :type d: int32
        :param q: Moving average order
        :type q: int32
        :param include_intercept: (default=True)  If true, the model is fit with an intercept.  Default is True
        :type include_intercept: bool
        :param method: (default=css-cgd)  Objective function and optimization method.  Current options are: 'css-bobyqa' and 'css-cgd'.
            Both optimize the log likelihood in terms of the conditional sum of squares.  The first uses BOBYQA for optimization, while
            the second uses conjugate gradient descent.  Default is 'css-cgd'.
        :type method: unicode
        :param user_init_params: (default=None)  A set of user provided initial parameters for optimization. If the list is empty
            (default), initialized using Hannan-Rissanen algorithm. If provided, order of parameter should be: intercept term, AR
            parameters (in increasing order of lag), MA parameters (in increasing order of lag)
        :type user_init_params: list

        :returns: Array of coefficients (intercept, AR, MA, with increasing degrees).
        :rtype: dict
        """
        return None



@doc_stub
class ArxModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a AutoRegressive Exogenous model.

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.
        The frame has five columns where "y" is the time series value and "vistors", "wkends",
        "incidentRate", and "seasonality" are exogenous inputs.


        >>> frame.inspect()
        [#]  y      visitors  wkends  incidentRate  seasonality
        ===========================================================
        [0]   68.0     278.0     0.0          28.0  0.0151327580791
        [1]   89.0     324.0     0.0          28.0  0.0115112433251
        [2]   96.0     318.0     0.0          28.0  0.0190129524584
        [3]   98.0     347.0     0.0          28.0  0.0292307976571
        [4]   70.0     345.0     1.0          28.0  0.0232811662756
        [5]   88.0     335.0     1.0          29.0  0.0306535355962
        [6]   76.0     309.0     0.0          29.0   0.027808059718
        [7]  104.0     318.0     0.0          29.0  0.0305241957835
        [8]   64.0     308.0     0.0          29.0  0.0247039042146
        [9]   89.0     320.0     0.0          29.0  0.0269026810295

        >>> model = ta.ArxModel()
        [===Job Progress===]

        >>> train_output = model.train(frame, "y", ["visitors", "wkends", "incidentRate", "seasonality"], 0, 0, True)
        [===Job Progress===]

        >>> train_output
        {u'c': 0.0,
         u'coefficients': [0.27583285049358186,
          -13.096710518563603,
          -0.030872283789462572,
          -103.8264674349643]}

        >>> predicted_frame = model.predict(frame, "y", ["visitors", "wkends", "incidentRate", "seasonality"])
        [===Job Progress===]

        >>> predicted_frame.column_names
        [u'y', u'visitors', u'wkends', u'incidentRate', u'seasonality', u'predicted_y']

        >>> predicted_frame.inspect(columns=("y","predicted_y"))
        [#]  y      predicted_y
        =========================
        [0]   68.0  74.2459276772
        [1]   89.0  87.3102478836
        [2]   96.0  84.8763748216
        [3]   98.0  91.8146447141
        [4]   70.0  78.7839977035
        [5]   88.0  75.2293498516
        [6]   76.0  81.4498419659
        [7]  104.0  83.6503308076
        [8]   64.0  81.4963026157
        [9]   89.0  84.5780055922

        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine:

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Post a request to get the metadata about the model

        >>> r = requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"ARX Model","model_class":"com.cloudera.sparkts.models.ARXModel","model_reader":"org.trustedanalytics.atk.scoring.models.ARXModelReaderPlugin","custom_values":{}},"input":[{"name":"y","value":"Array[Double]"},{"name":"x_values","value":"Array[Double]"}],"output":[{"name":"y","value":"Array[Double]"},{"name":"x_values","value":"Array[Double]"},{"name":"score","value":"Array[Double]"}]}'

        The ARX model only supports version 2 of the scoring engine.  In the following example, we are using the ARX model
        that was trained and published in the example above.  To keep things simple, we just send the first three rows of
        'y' values and the corresponding 'x_values' (visitors, wkends, incidentRate, and seasonality).

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v2/score',json={"records":[{"y":[68.0,89.0,96.0],"x_values":[278.0,324.0,318.0,0.0,0.0,0.0,28.0,28.0,28.0,0.0151327580791,0.0115112433251,0.0190129524584]}]})

        The 'score' value contains an array of predicted y values.

        >>> r.text
        u'{"data":[{"y":[68.0,89.0,96.0],"x_values":[278.0,324.0,318.0,0.0,0.0,0.0,28.0,28.0,28.0,0.0151327580791,0.0115112433251,0.0190129524584],"score":[74.24592767720993,87.31024788358613,84.8763748215895]}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of ARXModel
        :rtype: ArxModel
        """
        raise DocStubCalledError("model:arx/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, timeseries_column, x_columns):
        """
        New frame with column of predicted y values

        Predict the time series values for a test frame, based on the specified
        x values.  Creates a new frame revision with the existing columns and a new predicted_y
        column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose values are to be predicted.
        :type frame: Frame
        :param timeseries_column: Name of the column that contains the time series values.
        :type timeseries_column: unicode
        :param x_columns: Names of the column(s) that contain the values of the exogenous inputs.
        :type x_columns: list

        :returns: A new frame containing the original frame's columns and a column *predictied_y*
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the ARX Model and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine.
        This model can then be used to predict the cluster assignment of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, timeseries_column, x_columns, y_max_lag, x_max_lag, no_intercept=False):
        """
        Creates AutoregressionX (ARX) Model from train frame.

        Fit an autoregressive model with additional exogenous variables.

        **Notes**

        #)  Dataset being trained must be small enough to be worked with on a single node.
        #)  If the specified set of exogenous variables is not invertible, an exception is
            thrown stating that the "matrix is singular".  This happens when there are
            certain patterns in the dataset or columns of all zeros.  In order to work
            around the singular matrix issue, try selecting a different set of columns for
            exogenous variables, or use a different time window for training.


        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param timeseries_column: Name of the column that contains the time series values.
        :type timeseries_column: unicode
        :param x_columns: Names of the column(s) that contain the values of previous exogenous regressors.
        :type x_columns: list
        :param y_max_lag: The maximum lag order for the dependent (time series) variable
        :type y_max_lag: int32
        :param x_max_lag: The maximum lag order for exogenous variables
        :type x_max_lag: int32
        :param no_intercept: (default=False)  a boolean flag indicating if the intercept should be dropped. Default is false
        :type no_intercept: bool

        :returns: A dictionary with trained ARX model with the following keys\:

                          |   **c** : *float64*
                          |       intercept term, or zero for no intercept
                          |   **coefficients** : *list*
                          |       coefficients for each column of exogenous input.
        :rtype: dict
        """
        return None



@doc_stub
class CollaborativeFilteringModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a new Collaborative Filtering (ALS) model.

        For details about Collaborative Filter (ALS) modelling,
        see :ref:`Collaborative Filter <CollaborativeFilteringNewPlugin_Summary>`.

        >>> model = ta.CollaborativeFilteringModel()
        [===Job Progress===]
        >>> model.train(edge_frame, 'source', 'dest', 'weight')
        [===Job Progress===]
        >>> model.score(1,5)
        [===Job Progress===]
        >>> recommendations = model.recommend(1, 3, True)
        [===Job Progress===]
        >>> recommendations
        [{u'rating': 0.04854799984010311, u'product': 4, u'user': 1}, {u'rating': 0.04045666535703035, u'product': 3, u'user': 1}, {u'rating': 0.030060528471388848, u'product': 5, u'user': 1}]
        >>> recommendations = model.recommend(5, 2, False)
        [===Job Progress===]



        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: 
        :rtype: CollaborativeFilteringModel
        """
        raise DocStubCalledError("model:collaborative_filtering/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, input_source_column_name, input_dest_column_name, output_user_column_name='user', output_product_column_name='product', output_rating_column_name='rating'):
        """
        Collaborative Filtering Predict (ALS).

        See :ref:`Collaborative Filtering Train
        <python_api/models/model-collaborative_filtering/train>` for more information.

        >>> model = ta.CollaborativeFilteringModel()
        [===Job Progress===]
        >>> model.train(edge_frame, 'source', 'dest', 'weight')
        [===Job Progress===]

        >>> result = model.predict(edge_frame_predict, 'source', 'dest')
        [===Job Progress===]
        >>> result.inspect()
            [#]  user  product  rating
            ====================================
            [0]     1        4   0.0485403053463
            [1]     1        5   0.0300555229187
            [2]     2        5  0.00397346867248
            [3]     1        3   0.0404502525926


        [===Job Progress===]


        :param frame: 
        :type frame: Frame
        :param input_source_column_name: source column name.
        :type input_source_column_name: unicode
        :param input_dest_column_name: destination column name.
        :type input_dest_column_name: unicode
        :param output_user_column_name: (default=user)  A user column name for the output frame
        :type output_user_column_name: unicode
        :param output_product_column_name: (default=product)  A product  column name for the output frame
        :type output_product_column_name: unicode
        :param output_rating_column_name: (default=rating)  A rating column name for the output frame
        :type output_rating_column_name: unicode

        :returns: Returns a double representing the probability if the user(i) to like product (j)
        :rtype: Frame
        """
        return None


    @doc_stub
    def recommend(self, entity_id, number_of_recommendations=1, recommend_products=True):
        """
        Collaborative Filtering Predict (ALS).

        See :ref:`Collaborative Filtering Train
        <python_api/models/model-collaborative_filtering/train>` for more information.

        See :doc: 'here <new>' for examples.

        :param entity_id: A user/product id
        :type entity_id: int32
        :param number_of_recommendations: (default=1)  Number of recommendations
        :type number_of_recommendations: int32
        :param recommend_products: (default=True)  True - products for user; false - users for the product
        :type recommend_products: bool

        :returns: Returns an array of recommendations (as array of csv-strings)
        :rtype: list
        """
        return None


    @doc_stub
    def score(self, user_id, item_id):
        """
        Collaborative Filtering Predict (ALS).

        See :ref:`Collaborative Filtering Train
        <python_api/models/model-collaborative_filtering/train>` for more information.

        See :doc: 'here <new>' for examples.

        :param user_id: A user id from the first column of the input frame
        :type user_id: int32
        :param item_id: An item id from the first column of the input frame
        :type item_id: int32

        :returns: Returns a double representing the probability if the user(i) to like product (j)
        :rtype: float64
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, source_column_name, dest_column_name, weight_column_name, max_steps=10, regularization=0.5, alpha=0.5, num_factors=3, use_implicit=False, num_user_blocks=2, num_item_block=3, checkpoint_iterations=10, target_rmse=0.05):
        """
        Collaborative filtering (ALS) model

        See :doc: 'here <new>' for examples.

        :param frame: 
        :type frame: Frame
        :param source_column_name: source column name.
        :type source_column_name: unicode
        :param dest_column_name: destination column name.
        :type dest_column_name: unicode
        :param weight_column_name: weight column name.
        :type weight_column_name: unicode
        :param max_steps: (default=10)  max number of super-steps (max iterations) before the algorithm terminates. Default = 10
        :type max_steps: int32
        :param regularization: (default=0.5)  float value between 0 .. 1 
        :type regularization: float32
        :param alpha: (default=0.5)  double value between 0 .. 1 
        :type alpha: float64
        :param num_factors: (default=3)  number of the desired factors (rank)
        :type num_factors: int32
        :param use_implicit: (default=False)  use implicit preference
        :type use_implicit: bool
        :param num_user_blocks: (default=2)  number of user blocks
        :type num_user_blocks: int32
        :param num_item_block: (default=3)  number of item blocks
        :type num_item_block: int32
        :param checkpoint_iterations: (default=10)  Number of iterations between checkpoints
        :type checkpoint_iterations: int32
        :param target_rmse: (default=0.05)  target RMSE
        :type target_rmse: float64

        :returns: 
        :rtype: _Unit
        """
        return None



@doc_stub
class CoxPhModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Multivariate Cox Proportional Hazards model

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  time    bmi   censor
        =========================
        [0]     6.0  31.4     1.0
        [1]    98.0  21.5     1.0
        [2]   189.0  27.1     1.0
        [3]   374.0  22.7     1.0
        [4]  1002.0  35.7     1.0
        [5]  1205.0  30.7     1.0
        [6]  2065.0  26.5     1.0
        [7]  2201.0  28.3     1.0
        [8]  2421.0  27.9     1.0

        >>> model = ta.CoxPhModel()
        [===Job Progress===]
        >>> train_output = model.train(frame,time_column='time',covariate_columns=['bmi'],censor_column='censor',convergence_tolerance=0.01,max_steps=10)
        [===Job Progress===]
        >>> train_output
        {u'beta': [-0.03351902788328831], u'mean': [27.977777777777778]}
        >>> train_output['beta']
        [-0.03351902788328831]
        >>> predict_output = model.predict(frame)
        [===Job Progress===]
        >>> predict_output.inspect()
        [#]  time    bmi   censor  hazard_ratio
        =========================================
        [0]     6.0  31.4     1.0  0.891625068026
        [1]    98.0  21.5     1.0    1.2425041437
        [2]   189.0  27.1     1.0   1.02985936884
        [3]   374.0  22.7     1.0    1.1935188738
        [4]  1002.0  35.7     1.0  0.771945457787
        [5]  1205.0  30.7     1.0  0.912792914749
        [6]  2065.0  26.5     1.0   1.05078097618
        [7]  2201.0  28.3     1.0  0.989257541146
        [8]  2421.0  27.9     1.0   1.00261043677


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: 
        :rtype: CoxPhModel
        """
        raise DocStubCalledError("model:cox_ph/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, predict_frame, comparison_frame=None, feature_columns=None):
        """
        <Missing Doc>

        :param predict_frame: A frame whose hazard values
        :type predict_frame: Frame
        :param comparison_frame: (default=None)  A frame storing observations to compare hazards of the predict frame against. By default it is the frame used to train the model 
        :type comparison_frame: Frame
        :param feature_columns: (default=None)  Columns containing the observations. By default it is the columns used to train the model
        :type feature_columns: list

        :returns: 
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, time_column, covariate_columns, censor_column, convergence_tolerance=1e-06, max_steps=100):
        """
        Build Cox proportional hazard model.

        Fitting a CoxProportionalHazard Model using the covariate column(s)

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param time_column: Column containing the time data.
        :type time_column: unicode
        :param covariate_columns: List of column(s) containing the co-variate data.
        :type covariate_columns: list
        :param censor_column: Column containing the censored data. Can have 2 values: 0 - event did not happen (censored); 1 - event happened (not censored)
        :type censor_column: unicode
        :param convergence_tolerance: (default=1e-06)  Convergence tolerance
        :type convergence_tolerance: float64
        :param max_steps: (default=100)  Max steps.
        :type max_steps: int32

        :returns: Trained Cox proportional hazard model
        :rtype: dict
        """
        return None



@doc_stub
class DaalKMeansModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a DAAL k-means model.

        k-means [1]_ is an unsupervised algorithm used to partition
        the data into 'k' clusters.
        Each observation can belong to only one cluster, the cluster with the nearest
        mean.
        The k-means model is initialized, trained on columns of a frame, and used to
        predict cluster assignments for a frame.

        This model runs the DAAL implementation of k-means[2]_. The K-Means clustering
        algorithm computes centroids using the Lloyd method[3]_

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/K-means_clustering
        .. [2] https://software.intel.com/en-us/daal
        .. [3] https://en.wikipedia.org/wiki/Lloyd%27s_algorithm

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing two columns.

        >>> frame.inspect()
        [#]  data   name
        ===================
        [0]    2.0  ab
        [1]    1.0  cd
        [2]    7.0  ef
        [3]    1.0  gh
        [4]    9.0  ij
        [5]    2.0  kl
        [6]    0.0  mn
        [7]    6.0  op
        [8]    5.0  qr
        [9]  120.0  outlier

        >>> model = ta.DaalKMeansModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, ["data"],  k=2, max_iterations = 20)
        [===Job Progress===]
        >>> train_output
        {u'centroids': {u'Cluster:0': [120.0], u'Cluster:1': [3.6666666666666665]},
         u'cluster_size': {u'Cluster:0': 1, u'Cluster:1': 9}}
        >>> predicted_frame = model.predict(frame, ["data"])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  data   name     distance_from_cluster_0  distance_from_cluster_1  predicted_cluster
        ========================================================================================
        [0]    2.0  ab                       13924.0            2.77777777778        1
        [1]    1.0  cd                       14161.0            7.11111111111        1
        [2]    7.0  ef                       12769.0            11.1111111111        1
        [3]    1.0  gh                       14161.0            7.11111111111        1
        [4]    9.0  ij                       12321.0            28.4444444444        1
        [5]    2.0  kl                       13924.0            2.77777777778        1
        [6]    0.0  mn                       14400.0            13.4444444444        1
        [7]    6.0  op                       12996.0            5.44444444444        1
        [8]    5.0  qr                       13225.0            1.77777777778        1
        [9]  120.0  outlier                      0.0            13533.4444444        0


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of DaalKMeansModel
        :rtype: DaalKMeansModel
        """
        raise DocStubCalledError("model:daal_k_means/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None, label_column=None):
        """
        Predict the cluster assignments for the data points.

        Predicts the clusters for each data point and distance to every cluster center of the frame using the trained model

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose clusters are to be predicted.
            Default is to predict the clusters over columns the KMeans model was trained on.
        :type observation_columns: list
        :param label_column: (default=None)  Name of output column with
            index of cluster each observation belongs to.
        :type label_column: unicode

        :returns: Frame
                A new frame consisting of the existing columns of the frame and the following new columns:
                'k' columns : Each of the 'k' columns containing squared distance of that observation to the 'k'th cluster center
                predicted_cluster column: The cluster assignment for the observation
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the DaalKMeansModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine. 
        This model can then be used to predict the cluster assignment of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, observation_columns, column_scalings=None, k=2, max_iterations=100, label_column='predicted_cluster'):
        """
        Creates DAAL KMeans Model from train frame.

        Creating a DAAL KMeans Model using the observation columns.
        The algorithm chooses random observations as the initial cluster centers.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param observation_columns: Columns containing the
            observations.
        :type observation_columns: list
        :param column_scalings: (default=None)  Optional column scalings for each of the observation columns.
            The scaling value is multiplied by the corresponding value in the
            observation column.
        :type column_scalings: list
        :param k: (default=2)  Desired number of clusters.
            Default is 2.
        :type k: int32
        :param max_iterations: (default=100)  Number of iterations for which the algorithm should run.
            Default is 20.
        :type max_iterations: int32
        :param label_column: (default=predicted_cluster)  Optional name of output column with
            index of cluster each observation belongs to.
        :type label_column: unicode

        :returns: dictionary
                A dictionary with trained KMeans model with the following keys:
            'centroids' : dictionary with 'Cluster:id' as the key and the corresponding centroid as the value
            'assignments' : Frame with cluster assignments.
        :rtype: dict
        """
        return None



@doc_stub
class DaalLinearRegressionModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a DAAL Linear Regression model.

        Linear Regression [1]_ is used to model the relationship between a scalar
        dependent variable and one or more independent variables.
        The Linear Regression model is initialized, trained on columns of a frame and
        used to predict the value of the dependent variable given the independent
        observations of a frame.
        This model runs the DAAL implementation of Linear Regression [2]_ with
        QR [3]_ decomposition.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Linear_regression
        .. [2] https://software.intel.com/en-us/daal
        .. [3] https://en.wikipedia.org/wiki/QR_decomposition

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing two columns.

        >>> frame.inspect()
        [#]  x1   y
        ===============
        [0]  0.0    0.0
        [1]  1.0    2.5
        [2]  2.0    5.0
        [3]  3.0    7.5
        [4]  4.0   10.0
        [5]  5.0   12.5
        [6]  6.0   13.0
        [7]  7.0  17.15
        [8]  8.0   18.5
        [9]  9.0   23.5

        >>> model = ta.DaalLinearRegressionModel()
        [===Job Progress===]
        >>> train_output = model.train(frame,'y',['x1'])
        [===Job Progress===]
        >>> train_output
        {u'explained_variance': 49.275928030303035,
         u'intercept': -0.03272727272727477,
         u'mean_absolute_error': 0.5299393939393953,
         u'mean_squared_error': 0.6300969696969696,
         u'observation_columns': [u'x1'],
         u'r_2': 0.987374330660537,
         u'root_mean_squared_error': 0.7937864761363534,
         u'value_column': u'y',
         u'weights': [2.443939393939394]}
        >>> test_output = model.test(frame,'y')
        [===Job Progress===]
        >>> test_output
        {u'explained_variance': 49.275928030303035,
         u'mean_absolute_error': 0.5299393939393953,
         u'mean_squared_error': 0.6300969696969696,
         u'r_2': 0.987374330660537,
         u'root_mean_squared_error': 0.7937864761363534}
        >>> predicted_frame = model.predict(frame, observation_columns = ["x1"])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  x1   y      predict_y
        =================================
        [0]  0.0    0.0  -0.0327272727273
        [1]  1.0    2.5     2.41121212121
        [2]  2.0    5.0     4.85515151515
        [3]  3.0    7.5     7.29909090909
        [4]  4.0   10.0     9.74303030303
        [5]  5.0   12.5      12.186969697
        [6]  6.0   13.0     14.6309090909
        [7]  7.0  17.15     17.0748484848
        [8]  8.0   18.5     19.5187878788
        [9]  9.0   23.5     21.9627272727
        >>> model.publish()

        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of DaalLinearRegressionNewPlugin
        :rtype: DaalLinearRegressionModel
        """
        raise DocStubCalledError("model:daal_linear_regression/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, value_column=None, observation_columns=None):
        """
        Predict labels for a test frame using trained Intel DAAL linear regression model.

        Predict the labels for a test frame and create a new frame revision with
        existing columns and a new predicted value column.

        See :doc:`here <new>` for examples.

        :param frame: The frame to predict on
        :type frame: Frame
        :param value_column: (default=None)  Column name containing the value of each observation
        :type value_column: unicode
        :param observation_columns: (default=None)  List of column(s) containing the observations
        :type observation_columns: list

        :returns: frame\:
              Frame containing the original frame's columns and a column with the predicted value.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the Intel DAAL linear regression model
               and its implementation into a tar file. The tar file is then published
               on HDFS and this method returns the path to the tar file.
               The tar file serves as input to the scoring engine.
               This model can then be used to predict the target value of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, value_column=None, observation_columns=None):
        """
        Compute test metrics for trained Intel DAAL linear regression model.

        Predict the labels for a test frame, and compute test metrics for trained model.

        See :doc:`here <new>` for examples.

        :param frame: The frame to test the linear regression model on
        :type frame: Frame
        :param value_column: (default=None)  Column name containing the value of each observation
        :type value_column: unicode
        :param observation_columns: (default=None)  List of column(s) containing the observations
        :type observation_columns: list

        :returns: Test metrics for Intel DAAL linear regression model
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, value_column, observation_columns, fit_intercept=True):
        """
        Build Intel DAAL linear regression model.

        Create Intel DAAL LinearRegression Model using the observation column and target column of the train frame

        See :doc:`here <new>` for examples.

        :param frame: A frame to train or test the model on.
        :type frame: Frame
        :param value_column: Column name containing the value for each observation.
        :type value_column: unicode
        :param observation_columns: List of column(s) containing the observations.
        :type observation_columns: list
        :param fit_intercept: (default=True)  Parameter for whether to fit an intercept term. Default is true
        :type fit_intercept: bool

        :returns: Trained Intel DAAL linear regression model
        :rtype: dict
        """
        return None



@doc_stub
class DaalNaiveBayesModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a multinomial Naive Bayes model

        Naive Bayes [1]_ is a probabilistic classifier with strong
        independence assumptions between features.
        It computes the conditional probability distribution of each feature given label,
        and then applies Bayes' theorem to compute the conditional probability
        distribution of a label given an observation, and use it for prediction.
        The Naive Bayes model is initialized, trained on columns of a frame, tested against true labels of a frame and used
        to predict the value of the dependent variable given the independent
        observations of a frame and test the performance of the classification on test data.
        This model runs the Intel DAAL implementation of Naive Bayes [2]_.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Naive_Bayes_classifier
        .. [2] https://software.intel.com/en-us/daal
                     

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  Class  Dim_1          Dim_2
        =======================================
        [0]      1  19.8446136104  2.2985856384
        [1]      1  16.8973559126  2.6933495054
        [2]      1   5.5548729596  2.7777687995
        [3]      0  46.1810010826  3.1611961917
        [4]      0  44.3117586448  3.3458963222
        [5]      0  34.6334526911  3.6429838715

        >>> model = ta.DaalNaiveBayesModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'Class', ['Dim_1', 'Dim_2'], num_classes=2)
        [===Job Progress===]
        >>> train_output
        {u'class_log_prior': [-0.6931471805599453, -0.6931471805599453],
         u'feature_log_prob': [[-0.07696104113612832, -2.6026896854443837],[-0.15762894420358317, -1.9252908618525777]]}
        >>> predicted_frame = model.predict(frame, ['Dim_1', 'Dim_2'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  Class  Dim_1          Dim_2         predicted_class
        ========================================================
        [0]      1  19.8446136104  2.2985856384              0.0
        [1]      1  16.8973559126  2.6933495054              1.0
        [2]      1   5.5548729596  2.7777687995              1.0
        [3]      0  46.1810010826  3.1611961917              0.0
        [4]      0  44.3117586448  3.3458963222              0.0
        [5]      0  34.6334526911  3.6429838715              0.0

        >>> test_metrics = model.test(frame, 'Class', ['Dim_1','Dim_2'])
        [===Job Progress===]
        >>> test_metrics
        Precision: 1.0
        Recall: 0.666666666667
        Accuracy: 0.833333333333
        FMeasure: 0.8
        Confusion Matrix:
                    Predicted_Pos  Predicted_Neg
        Actual_Pos              2              1
        Actual_Neg              0              3
        >>> model.publish()
        [===Job Progress===]

        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of DaalNaiveBayesModel
        :rtype: DaalNaiveBayesModel
        """
        raise DocStubCalledError("model:daal_naive_bayes/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict labels for data points using trained multinomial Naive Bayes model.

        Predict the labels for a test frame using trained multinomial Naive Bayes model,
              and create a new frame revision with existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the
            observations whose labels are to be predicted.
            By default, we predict the labels over columns the NaiveBayesModel
            was trained on.
        :type observation_columns: list

        :returns: Frame containing the original frame's columns and a column with the predicted label.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a scoring engine tar file.

        Creates a tar file with the trained multinomial Naive Bayes Model
        The tar file is used as input to the scoring engine to predict the class of an observation.

        See :doc:`here <new>` for examples.



        :returns: The HDFS path to the tar file.
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param label_column: Column containing the actual
            label for each observation.
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the
            observations whose labels are to be predicted.
            By default, we predict the labels over columns the NaiveBayesModel
            was trained on.
        :type observation_columns: list

        :returns: A dictionary with classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, num_classes=2):
        """
        Build a multinomial naive bayes model.

        Train a DaalNaiveBayesModel using the observation column, label column of the train frame and an optional lambda value.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param label_column: Column containing the label for each
            observation.
        :type label_column: unicode
        :param observation_columns: Column(s) containing the
            observations.
        :type observation_columns: list
        :param num_classes: (default=2)  Number of classes
        :type num_classes: int32

        :returns: dictionary
            A dictionary with trained multinomial naive bayes model with the following keys:
            'class_log_prior': smoothed empirical log probability for each class
            'feature_log_prob': empirical log probability of features given a class, P(x_i|y)
                        
        :rtype: dict
        """
        return None



@doc_stub
class DaalPrincipalComponentsModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of an Intel DAAL Principal Components model.

        Principal component analysis [1]_ is a statistical algorithm
        that converts possibly correlated features to linearly uncorrelated variables
        called principal components.
        The number of principal components is less than or equal to the number of
        original variables.
        This implementation of computing Principal Components is done by Singular
        Value Decomposition [2]_ of the data, providing the user with an option to
        mean center the data.
        The Principal Components model is initialized; trained on
        specifying the observation columns of the frame and the number of components;
        used to predict principal components.
        The Intel DAAL Singular Value Decomposition [3]_ implementation has been used for
        this, with additional features to 1) mean center the data during train and
        predict and 2) compute the t-squared index during prediction.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Principal_component_analysis
        .. [2] https://en.wikipedia.org/wiki/Singular_value_decomposition
        .. [3] https://software.intel.com/en-us/daal

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing six columns.

        >>> frame.inspect()
        [#]  1    2    3    4    5    6
        =================================
        [0]  2.6  1.7  0.3  1.5  0.8  0.7
        [1]  3.3  1.8  0.4  0.7  0.9  0.8
        [2]  3.5  1.7  0.3  1.7  0.6  0.4
        [3]  3.7  1.0  0.5  1.2  0.6  0.3
        [4]  1.5  1.2  0.5  1.4  0.6  0.4
        >>> model = ta.DaalPrincipalComponentsModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, ['1','2','3','4','5','6'], mean_centered=True, k=6)
        [===Job Progress===]
        >>> train_output
        {u'k': 6, u'column_means': [2.92, 1.48, 0.4, 1.3, 0.7, 0.52], u'observation_columns': [u'1', u'2', u'3', u'4', u'5', u'6'], u'mean_centered': True, u'right_singular_vectors': [[-0.9906468642089332, 0.11801374544146297, 0.025647010353320242, 0.048525096275535286, -0.03252674285233843, 0.02492194235385788], [-0.07735139793384983, -0.6023104604841424, 0.6064054412059493, -0.4961696216881456, -0.12443126544906798, -0.042940400527513106], [0.028850639537397756, 0.07268697636708575, -0.2446393640059097, -0.17103491337994586, -0.9368360903028429, 0.16468461966702994], [0.10576208410025369, 0.5480329468552815, 0.75230590898727, 0.2866144016081251, -0.20032699877119212, 0.015210798298156058], [-0.024072151446194606, -0.30472267167437633, -0.01125936644585159, 0.48934541040601953, -0.24758962014033054, -0.7782533654748628], [-0.0061729539518418355, -0.47414707747028795, 0.07533458226215438, 0.6329307498105832, -0.06607181431092408, 0.6037419362435869]], u'singular_values': [1.8048170096632419, 0.8835344148403882, 0.7367461843294286, 0.15234027471064404, 5.90167578565564e-09, 4.478916578455115e-09]}
        >>> train_output['column_means']
        [2.92, 1.48, 0.4, 1.3, 0.7, 0.52]
        >>> predicted_frame = model.predict(frame, mean_centered=True, t_squared_index=True, observation_columns=['1','2','3','4','5','6'], c=3)
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  1    2    3    4    5    6    p_1              p_2
        ===================================================================
        [0]  2.6  1.7  0.3  1.5  0.8  0.7   0.314738695012  -0.183753549226
        [1]  3.3  1.8  0.4  0.7  0.9  0.8  -0.471198363594  -0.670419608227
        [2]  3.5  1.7  0.3  1.7  0.6  0.4  -0.549024749481   0.235254068619
        [3]  3.7  1.0  0.5  1.2  0.6  0.3  -0.739501762517   0.468409769639
        [4]  1.5  1.2  0.5  1.4  0.6  0.4    1.44498618058   0.150509319195
        <BLANKLINE>
        [#]  p_3              t_squared_index
        =====================================
        [0]   0.312561560113   0.253649649849
        [1]  -0.228746130528   0.740327252782
        [2]   0.465756549839   0.563086507007
        [3]  -0.386212142456   0.723748467549
        [4]  -0.163359836968   0.719188122813
        >>> model.publish()
        [===Job Progress===]

        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of PrincipalComponentsModel
        :rtype: DaalPrincipalComponentsModel
        """
        raise DocStubCalledError("model:daal_principal_components/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, mean_centered=True, t_squared_index=False, observation_columns=None, c=None, name=None):
        """
        Predict using principal components model.

        Predicting on a dataframe's columns using a PrincipalComponents Model.

        See :doc:`here <new>` for examples.

        :param frame: Frame whose principal components are to be computed.
        :type frame: Frame
        :param mean_centered: (default=True)  Option to mean center the columns. Default is true
        :type mean_centered: bool
        :param t_squared_index: (default=False)  Indicator for whether the t-square index is to be computed. Default is false.
        :type t_squared_index: bool
        :param observation_columns: (default=None)  List of observation column name(s) to be used for prediction. Default is the list of column name(s) used to train the model.
        :type observation_columns: list
        :param c: (default=None)  The number of principal components to be predicted. 'c' cannot be greater than the count used to train the model. Default is the count used to train the model.
        :type c: int32
        :param name: (default=None)  The name of the output frame generated by predict.
        :type name: unicode

        :returns: A frame with existing columns and following additional columns\:
                  'c' additional columns: containing the projections of V on the the frame
                  't_squared_index': column storing the t-square-index value, if requested
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the PrincipalComponentsModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine. This model can
        then be used to compute the principal components and t-squared index(if requested) of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, observation_columns, mean_centered=True, k=None):
        """
        Build Intel DAAL principal components model.

        Creating a PrincipalComponents Model using the observation columns.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model
            on.
        :type frame: Frame
        :param observation_columns: List of column(s) containing
            the observations.
        :type observation_columns: list
        :param mean_centered: (default=True)  Option to mean center the
            columns
        :type mean_centered: bool
        :param k: (default=None)  Principal component count.
            Default is the number of observation columns
        :type k: int32

        :returns: dictionary
                |A dictionary with trained Principal Components Model with the following keys\:
                |'column_means': the list of the means of each observation column
                |'k': number of principal components used to train the model
                |'mean_centered': Flag indicating if the model was mean centered during training
                |'observation_columns': the list of observation columns on which the model was trained,
                |'eigen_vectors': list of a list storing the eigen vectors of the specified columns of the input frame
                |'eigen_values': list storing the eigen values of the specified columns of the input frame
              
        :rtype: dict
        """
        return None



@doc_stub
class GmmModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a gmm model.

        A Gaussian Mixture Model [1]_ represents a distribution where the observations are drawn from one of the k
        Gaussian sub-distributions, each with its own probability. Each observation can belong to only one cluster,
        the cluster representing the distribution with highest probability for that observation.

        The gmm model is initialized, trained on columns of a frame, and used to
        predict cluster assignments for a frame.
        This model runs the MLLib implementation of gmm [2]_ with enhanced
        feature of computing the number of elements in each cluster during training.
        During predict, it computes the cluster assignment of the observations given in the frame.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Mixture_model#Multivariate_Gaussian_mixture_model
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-clustering.html#gaussian-mixture
          

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing two columns.

        >>> frame.inspect()
        [#]  data  name
        ===============
        [0]   2.0  ab
        [1]   1.0  cd
        [2]   7.0  ef
        [3]   1.0  gh
        [4]   9.0  ij
        [5]   2.0  kl
        [6]   0.0  mn
        [7]   6.0  op
        [8]   5.0  qr
        >>> model = ta.GmmModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, ["data"], [1.0], 4)
        [===Job Progress===]
        >>> train_output
        {u'cluster_size': {u'Cluster:0': 4, u'Cluster:1': 5},
         u'gaussians': [[u'mu:[6.79969916638852]',
           u'sigma:List(List(2.2623755196701305))'],
          [u'mu:[1.1984454608177824]', u'sigma:List(List(0.5599200477022921))'],
          [u'mu:[6.6173304476544335]', u'sigma:List(List(2.1848346923369246))']],
         u'weights': [0.2929610525524124, 0.554374326098111, 0.15266462134947675]}
        >>> predicted_frame = model.predict(frame, ["data"])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  data  name  predicted_cluster
        ==================================
        [0]   9.0  ij                    0
        [1]   2.0  ab                    1
        [2]   1.0  cd                    1
        [3]   0.0  mn                    1
        [4]   1.0  gh                    1
        [5]   6.0  op                    0
        [6]   5.0  qr                    0
        [7]   2.0  kl                    1
        [8]   7.0  ef                    0


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: 
        :rtype: GmmModel
        """
        raise DocStubCalledError("model:gmm/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict the cluster assignments for the data points.

        Predicts the clusters for each data point of the frame using the trained model

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations whose clusters are to be predicted.
            By default, we predict the clusters over columns the GMMModel was trained on.
            The columns are scaled using the same values used when training the model.
        :type observation_columns: list

        :returns: Frame
                A new frame consisting of the existing columns of the frame and a new column:
            predicted_cluster : int
                Integer containing the cluster assignment.
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, observation_columns, column_scalings, k=2, max_iterations=100, convergence_tol=0.01, seed=-8485575833015641262):
        """
        Creates a GMM Model from the train frame.

        At training the 'k' cluster centers are computed.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param observation_columns: Columns containing the observations.
        :type observation_columns: list
        :param column_scalings: Column scalings for each of the observation columns. The scaling value is multiplied by the corresponding value in the
            observation column.
        :type column_scalings: list
        :param k: (default=2)  Desired number of clusters. Default is 2.
        :type k: int32
        :param max_iterations: (default=100)  Number of iterations for which the algorithm should run. Default is 100.
        :type max_iterations: int32
        :param convergence_tol: (default=0.01)  Largest change in log-likelihood at which convergence iis considered to have occurred.
        :type convergence_tol: float64
        :param seed: (default=-8485575833015641262)  Random seed
        :type seed: int64

        :returns: dict
                Returns a dictionary the following fields
            cluster_size : dict
                with the key being a string of the form 'Cluster:Id' storing the number of elements in cluster number 'Id'
            gaussians : dict
                Stores the 'mu' and 'sigma' corresponding to the Multivariate Gaussian (Normal) Distribution for each Gaussian

        :rtype: dict
        """
        return None



@doc_stub
class KMeansModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a k-means model.

        k-means [1]_ is an unsupervised algorithm used to partition
        the data into 'k' clusters.
        Each observation can belong to only one cluster, the cluster with the nearest
        mean.
        The k-means model is initialized, trained on columns of a frame, and used to
        predict cluster assignments for a frame.
        This model runs the MLLib implementation of k-means [2]_ with enhanced
        features, computing the number of elements in each cluster during training.
        During predict, it computes the distance of each observation from its cluster
        center and also from every other cluster center.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/K-means_clustering
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-clustering.html#k-means

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing two columns.

        >>> frame.inspect()
        [#]  data  name
        ===============
        [0]   2.0  ab
        [1]   1.0  cd
        [2]   7.0  ef
        [3]   1.0  gh
        [4]   9.0  ij
        [5]   2.0  kl
        [6]   0.0  mn
        [7]   6.0  op
        [8]   5.0  qr
        >>> model = ta.KMeansModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, ["data"], [1], 3)
        [===Job Progress===]
        >>> train_output
        {u'within_set_sum_of_squared_error': 5.3, u'cluster_size': {u'Cluster:1': 5, u'Cluster:3': 2, u'Cluster:2': 2}}
        >>> train_output.has_key('within_set_sum_of_squared_error')
        True
        >>> predicted_frame = model.predict(frame, ["data"])
        [===Job Progress===]
        >>> predicted_frame.column_names
        [u'data', u'name', u'distance_from_cluster_1', u'distance_from_cluster_2', u'distance_from_cluster_3', u'predicted_cluster']
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"KMeans Model","model_class":"org.trustedanalytics.atk.scoring.models.KMeansScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.KMeansModelReaderPlugin","custom_values":{}},"input":[{"name":"data","value":"Double"}],"output":[{"name":"data","value":"Double"},{"name":"score","value":"Int"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2.0', headers=headers)
        >>> r.text
        u'1'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2.0&data=7.0&data=5.0', headers=headers)
        >>> r.text
        u'1,2,2'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses. In the following example, 'data' is the name of the observation column that the model was trained on:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"data": 2.0}]})
        >>> r.text
        u'{"data":[{"data":2.0,"score":1}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"data": 2.0}, {"data": 7.0}, {"data": 5.0}]})
        >>> r.text
        u'{"data":[{"data":2.0,"score":1},{"data":7.0,"score":2},{"data":5.0,"score":2}]}'


        :param name: (default=None)  Name for the model.
        :type name: unicode

        :returns: A new instance of KMeansModel
        :rtype: KMeansModel
        """
        raise DocStubCalledError("model:k_means/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict the cluster assignments for the data points.

        Predicts the clusters for each data point and distance to every cluster center of the frame using the trained model

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose clusters are to be predicted.
            Default is to predict the clusters over columns the KMeans model was trained on.
            The columns are scaled using the same values used when training the
            model.
        :type observation_columns: list

        :returns: Frame
                A new frame consisting of the existing columns of the frame and the following new columns:
                'k' columns : Each of the 'k' columns containing squared distance of that observation to the 'k'th cluster center
                predicted_cluster column: The cluster assignment for the observation
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the KMeansModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine. 
        This model can then be used to predict the cluster assignment of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, observation_columns, column_scalings, k=2, max_iterations=20, epsilon=0.0001, initialization_mode='k-means||'):
        """
        Creates KMeans Model from train frame.

        Creating a KMeans Model using the observation columns.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param observation_columns: Columns containing the
            observations.
        :type observation_columns: list
        :param column_scalings: Column scalings for each of the observation columns.
            The scaling value is multiplied by the corresponding value in the
            observation column.
        :type column_scalings: list
        :param k: (default=2)  Desired number of clusters.
            Default is 2.
        :type k: int32
        :param max_iterations: (default=20)  Number of iterations for which the algorithm should run.
            Default is 20.
        :type max_iterations: int32
        :param epsilon: (default=0.0001)  Distance threshold within which we consider k-means to have converged.
            Default is 1e-4. If all centers move less than this Euclidean distance, we stop iterating one run.
        :type epsilon: float64
        :param initialization_mode: (default=k-means||)  The initialization technique for the algorithm.
            It could be either "random" to choose random points as initial clusters, or "k-means||" to use a parallel variant of k-means++.
            Default is "k-means||".
        :type initialization_mode: unicode

        :returns: dictionary
                A dictionary with trained KMeans model with the following keys\:
            'cluster_size' : dictionary with 'Cluster:id' as the key and the corresponding cluster size is the value
            'within_set_sum_of_squared_error' : The set of sum of squared error for the model.
        :rtype: dict
        """
        return None



@doc_stub
class LdaModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Creates Latent Dirichlet Allocation model

        |LDA| is a commonly-used algorithm for topic modeling, but,
        more broadly, is considered a dimensionality reduction technique.
        For more detail see :ref:`LDA <LdaNewPlugin_Summary>`.

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  doc_id     word_id     word_count
        ======================================
        [0]  nytimes    harry                3
        [1]  nytimes    economy             35
        [2]  nytimes    jobs                40
        [3]  nytimes    magic                1
        [4]  nytimes    realestate          15
        [5]  nytimes    movies               6
        [6]  economist  economy             50
        [7]  economist  jobs                35
        [8]  economist  realestate          20
        [9]  economist  movies               1
        >>> model = ta.LdaModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'doc_id', 'word_id', 'word_count', max_iterations = 3, num_topics = 2)
        [===Job Progress===]
        >>> train_output
        {'topics_given_word': Frame  <unnamed>
        row_count = 8
        schema = [word_id:unicode, topic_probabilities:vector(2)]
        status = ACTIVE  (last_read_date = 2015-10-23T11:07:46.556000-07:00), 'topics_given_doc': Frame  <unnamed>
        row_count = 3
        schema = [doc_id:unicode, topic_probabilities:vector(2)]
        status = ACTIVE  (last_read_date = 2015-10-23T11:07:46.369000-07:00), 'report': u'======Graph Statistics======\nNumber of vertices: 11} (doc: 3, word: 8})\nNumber of edges: 16\n\n======LDA Configuration======\nnumTopics: 2\nalpha: 1.100000023841858\nbeta: 1.100000023841858\nmaxIterations: 3\n', 'word_given_topics': Frame  <unnamed>
        row_count = 8
        schema = [word_id:unicode, topic_probabilities:vector(2)]
        status = ACTIVE  (last_read_date = 2015-10-23T11:07:46.465000-07:00)}
        >>> topics_given_doc = train_output['topics_given_doc']
        [===Job Progress===]
        >>> topics_given_doc.inspect()
        [#]  doc_id       topic_probabilities
        ===========================================================
        [0]  harrypotter  [0.06417509902256538, 0.9358249009774346]
        [1]  economist    [0.8065841283073141, 0.19341587169268581]
        [2]  nytimes      [0.855316939742769, 0.14468306025723088]
        >>> topics_given_doc.column_names
        [u'doc_id', u'topic_probabilities']
        >>> word_given_topics = train_output['word_given_topics']
        [===Job Progress===]
        >>> word_given_topics.inspect()
        [#]  word_id     topic_probabilities
        =============================================================
        [0]  harry       [0.005015572372943657, 0.2916109787103347]
        [1]  realestate  [0.167941871746252, 0.032187084858186256]
        [2]  secrets     [0.026543839878055035, 0.17103864163730945]
        [3]  movies      [0.03704750433384287, 0.003294403360133419]
        [4]  magic       [0.016497495727347045, 0.19676900962555072]
        [5]  economy     [0.3805836266747442, 0.10952481503975171]
        [6]  chamber     [0.0035944004256137523, 0.13168123398523954]
        [7]  jobs        [0.36277568884120137, 0.06389383278349432]
        >>> word_given_topics.column_names
        [u'word_id', u'topic_probabilities']
        >>> topics_given_word = train_output['topics_given_word']
        [===Job Progress===]
        >>> topics_given_word.inspect()
        [#]  word_id     topic_probabilities
        ===========================================================
        [0]  harry       [0.018375903962878668, 0.9816240960371213]
        [1]  realestate  [0.8663322126823493, 0.13366778731765067]
        [2]  secrets     [0.15694172611285945, 0.8430582738871405]
        [3]  movies      [0.9444179131148587, 0.055582086885141324]
        [4]  magic       [0.09026309091077593, 0.9097369090892241]
        [5]  economy     [0.8098866029287505, 0.19011339707124958]
        [6]  chamber     [0.0275551649439219, 0.9724448350560781]
        [7]  jobs        [0.8748608515169193, 0.12513914848308066]
        >>> topics_given_word.column_names
        [u'word_id', u'topic_probabilities']
        >>> prediction = model.predict(['harry', 'secrets', 'magic', 'harry', 'chamber' 'test'])
        [===Job Progress===]
        >>> prediction
        {u'topics_given_doc': [0.3149285399451628, 0.48507146005483726], u'new_words_percentage': 20.0, u'new_words_count': 1}
        >>> prediction['topics_given_doc']
        [0.3149285399451628, 0.48507146005483726]
        >>> prediction['new_words_percentage']
        20.0
        >>> prediction['new_words_count']
        1
        >>> prediction.has_key('topics_given_doc')
        True
        >>> prediction.has_key('new_words_percentage')
        True
        >>> prediction.has_key('new_words_count')
        True
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Lda Model","model_class":"org.trustedanalytics.atk.scoring.models.LdaScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.LdaModelReaderPlugin","custom_values":{}},"input":[{"name":"doc_id","value":"Array[String]"}],"output":[{"name":"doc_id","value":"Array[String]"},{"name":"topics_given_doc","value":"Vector[Double]"},{"name":"new_words_count","value":"Int"},{"name":"new_words_percentage","value":"Double"}]}'

        The LDA model only supports version 2 of the scoring engine.
        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"doc_id": ['harry', 'secrets', 'magic']}]})
        >>> r.text
        u'{"data":[{"doc_id":["harry","secrets","magic"],"topics_given_doc":[0.4841745428992676,0.5158254571007324],"new_words_count":0,"new_words_percentage":0.0}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"doc_id": ['harry', 'secrets', 'magic']}, {"doc_id": ['harry', 'secrets', 'magic']}]})
        >>> r.text
        u'{"data":[{"doc_id":["harry","secrets","magic"],"topics_given_doc":[0.4841745428992676,0.5158254571007324],"new_words_count":0,"new_words_percentage":0.0},{"doc_id":["harry","secrets","magic"],"topics_given_doc":[0.4841745428992676,0.5158254571007324],"new_words_count":0,"new_words_percentage":0.0}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of LdaModel
        :rtype: LdaModel
        """
        raise DocStubCalledError("model:lda/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, document):
        """
        Predict conditional probabilities of topics given document.

        Predicts conditional probabilities of topics given document using trained Latent Dirichlet Allocation model.
        The input document is represented as a list of strings

        See :doc:`here <new>` for examples.

        :param document: Document whose topics are to be predicted. 
        :type document: list

        :returns: Dictionary containing predicted topics.
            The data returned is composed of multiple keys\:

            |   **list of doubles** | *topics_given_doc*
            |       List of conditional probabilities of topics given document.
            |   **int** : *new_words_count*
            |       Count of new words in test document not present in training set.
            |   **double** | *new_words_percentage*
            |       Percentage of new words in test document.
        :rtype: dict
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will used as input to the scoring engine

        Creates a tar file with the trained Latent Dirichlet Allocation model. The tar file is then published on HDFS and this method returns the path to the tar file.
                      The tar file is used as input to the scoring engine to predict the conditional topic probabilities for a document.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, document_column_name, word_column_name, word_count_column_name, max_iterations=20, alpha=None, beta=1.10000002384, num_topics=10, random_seed=None):
        """
        Creates Latent Dirichlet Allocation model

        See the discussion about `Latent Dirichlet Allocation at Wikipedia. <http://en.wikipedia.org/wiki/Latent_Dirichlet_allocation>`__

        See :doc:`here <new>` for examples.

        :param frame: Input frame data.
        :type frame: Frame
        :param document_column_name: Column Name for documents.
            Column should contain a str value.
        :type document_column_name: unicode
        :param word_column_name: Column name for words.
            Column should contain a str value.
        :type word_column_name: unicode
        :param word_count_column_name: Column name for word count.
            Column should contain an int32 or int64 value.
        :type word_count_column_name: unicode
        :param max_iterations: (default=20)  The maximum number of iterations that the algorithm will execute.
            The valid value range is all positive int.
            Default is 20.
        :type max_iterations: int32
        :param alpha: (default=None)  The hyperparameter for document-specific distribution over topics.
            Mainly used as a smoothing parameter in Bayesian inference.
            If set to a singleton list List(-1d), then docConcentration is set automatically.
            If set to singleton list List(t) where t != -1, then t is replicated to a vector of length k during LDAOptimizer.initialize().
            Otherwise, the alpha must be length k.
            Currently the EM optimizer only supports symmetric distributions, so all values in the vector should be the same.
            Values should be greater than 1.0. Default value is -1.0 indicating automatic setting.
        :type alpha: list
        :param beta: (default=1.10000002384)  The hyperparameter for word-specific distribution over topics.
            Mainly used as a smoothing parameter in Bayesian inference.
            Larger value implies that topics contain all words more uniformly and
            smaller value implies that topics are more concentrated on a small
            subset of words.
            Valid value range is all positive float greater than or equal to 1.
            Default is 0.1.
        :type beta: float32
        :param num_topics: (default=10)  The number of topics to identify in the LDA model.
            Using fewer topics will speed up the computation, but the extracted topics
            might be more abstract or less specific; using more topics will
            result in more computation but lead to more specific topics.
            Valid value range is all positive int.
            Default is 10.
        :type num_topics: int32
        :param random_seed: (default=None)  An optional random seed.
            The random seed is used to initialize the pseudorandom number generator
            used in the LDA model. Setting the random seed to the same value every
            time the model is trained, allows LDA to generate the same topic distribution
            if the corpus and LDA parameters are unchanged.
        :type random_seed: int64

        :returns: The data returned is composed of multiple components\:

                          |   **Frame** : *topics_given_doc*
                          |       Conditional probabilities of topic given document.
                          |   **Frame** : *word_given_topics*
                          |       Conditional probabilities of word given topic.
                          |   **Frame** : *topics_given_word*
                          |       Conditional probabilities of topic given word.
                          |   **str** : *report*
                          |       The configuration and learning curve report for Latent Dirichlet
            Allocation as a multiple line str.
        :rtype: dict
        """
        return None



@doc_stub
class LibsvmModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Support Vector Machine model.

        Support Vector Machine [1]_ is a supervised algorithm used to
        perform binary classification.
        A support vector machine constructs a high dimensional hyperplane which is
        said to achieve a good separation when a hyperplane has the largest distance to
        the nearest training-data point of any class. This model runs the
        LIBSVM [2]_ [3]_ implementation of SVM.
        The LIBSVM model is initialized, trained on columns of a frame, used to
        predict the labels of observations in a frame and used to test the predicted
        labels against the true labels.
        During testing, labels of the observations are predicted and tested against
        the true labels using built-in binary Classification Metrics.

        .. rubric: footnotes

        .. [1] https://en.wikipedia.org/wiki/Support_vector_machine
        .. [2] https://www.csie.ntu.edu.tw/~cjlin/libsvm/
        .. [3] https://en.wikipedia.org/wiki/LIBSVM

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing four columns.

        >>> frame.inspect()
            [#]  idNum  tr_row  tr_col  pos_one
            ===================================
            [0]    1.0    -1.0    -1.0      1.0
            [1]    2.0    -1.0     0.0      1.0
            [2]    3.0    -1.0     1.0      1.0
            [3]    4.0     0.0    -1.0      1.0
            [4]    5.0     0.0     0.0      1.0
            [5]    6.0     0.0     1.0      1.0
            [6]    7.0     1.0    -1.0      1.0
            [7]    8.0     1.0     0.0      1.0
            [8]    9.0     1.0     1.0      1.0
        >>> model = ta.LibsvmModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, "idNum", ["tr_row", "tr_col"],svm_type=2,epsilon=10e-3,gamma=1.0/2,nu=0.1,p=0.1)
        [===Job Progress===]
        >>> predicted_frame = model.predict(frame)
        [===Job Progress===]
        >>> predicted_frame.inspect()
            [#]  idNum  tr_row  tr_col  pos_one  predicted_label
            ====================================================
            [0]    1.0    -1.0    -1.0      1.0              1.0
            [1]    2.0    -1.0     0.0      1.0              1.0
            [2]    3.0    -1.0     1.0      1.0             -1.0
            [3]    4.0     0.0    -1.0      1.0              1.0
            [4]    5.0     0.0     0.0      1.0              1.0
            [5]    6.0     0.0     1.0      1.0              1.0
            [6]    7.0     1.0    -1.0      1.0              1.0
            [7]    8.0     1.0     0.0      1.0              1.0
            [8]    9.0     1.0     1.0      1.0              1.0
        >>> test_obj = model.test(frame, "pos_one",["tr_row", "tr_col"])
        [===Job Progress===]
        >>> test_obj.accuracy
        0.8888888888888888
        >>> test_obj.precision
        1.0
        >>> test_obj.f_measure
        0.9411764705882353
        >>> test_obj.recall
        0.8888888888888888
        >>> score = model.score([3,4])
        [===Job Progress===]
        >>> score
        -1.0
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"LibSvm Model","model_class":"org.trustedanalytics.atk.scoring.models.LibSvmModel","model_reader":"org.trustedanalytics.atk.scoring.models.LibSvmModelReaderPlugin","custom_values":{}},"input":[{"name":"tr_row","value":"Double"},{"name":"tr_col","value":"Double"}],"output":[{"name":"tr_row","value":"Double"},{"name":"tr_col","value":"Double"},{"name":"Prediction","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2,17,-6', headers=headers)
        >>> r.text
        u'-1.0'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2,17,-6&data=0,0,0', headers=headers)
        >>> r.text
        u'-1.0,1.0'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses. In the following example, 'tr_row' and 'tr_col' are the names of the observation columns that the model was trained on:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"tr_row": 1.0, "tr_col": 2.6}]})
        >>> r.text
        u'{"data":[{"tr_row":1.0,"tr_col":2.6,"Prediction":-1.0}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"tr_row": 1.0, "tr_col": 2.6},{"tr_row": 3.0, "tr_col": 0.6} ]})
        >>> r.text
        u'{"data":[{"tr_row":1.0,"tr_col":2.6,"Prediction":-1.0},{"tr_row":3.0,"tr_col":0.6,"Prediction":-1.0}]}'










        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of LibsvmModel
        :rtype: LibsvmModel
        """
        raise DocStubCalledError("model:libsvm/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        New frame with new predicted label column.

        Predict the labels for a test frame and create a new frame revision with
        existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.


        :param frame: A frame whose labels are to be predicted.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations whose labels are to be
            predicted.
            Default is the columns the LIBSVM model was trained on.
        :type observation_columns: list

        :returns: A new frame containing the original frame's columns and a column
            *predicted_label* containing the label calculated for each observation.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the LibsvmModel and its implementation into a tar file. The tar file is then published on 
        HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine.
        This model can then be used to predict the class of an observation.
            



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @doc_stub
    def score(self, vector):
        """
        Calculate the prediction label for a single observation.

        See :doc:`here <new>` for examples.


        :param vector: 
        :type vector: None

        :returns: Predicted label.
        :rtype: float64
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
        :type frame: Frame
        :param label_column: Column containing the actual label for each
            observation.
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the observations whose
            labels are to be predicted and tested.
            Default is to test over the columns the LIBSVM model
            was trained on.
        :type observation_columns: list

        :returns: A dictionary with binary classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, svm_type=2, kernel_type=2, weight_label=None, weight=None, epsilon=0.001, degree=3, gamma=None, coef=0.0, nu=0.5, cache_size=100.0, shrinking=1, probability=0, nr_weight=1, c=1.0, p=0.1):
        """
        Train a Lib Svm model

        Creating a lib Svm Model using the observation column and label column of the
        train frame.

        See :doc:`here <new>` for examples.



        :param frame: A frame to train the model on.
        :type frame: Frame
        :param label_column: Column name containing the label for each
            observation.
        :type label_column: unicode
        :param observation_columns: Column(s) containing the
            observations.
        :type observation_columns: list
        :param svm_type: (default=2)  Set type of SVM.
            Default is one-class SVM.

            |   0 -- C-SVC
            |   1 -- nu-SVC
            |   2 -- one-class SVM
            |   3 -- epsilon-SVR
            |   4 -- nu-SVR
        :type svm_type: int32
        :param kernel_type: (default=2)  Specifies the kernel type to be used in the algorithm.
            Default is RBF.

            |   0 -- linear: u\'\*v
            |   1 -- polynomial: (gamma*u\'\*v + coef0)^degree
            |   2 -- radial basis function: exp(-gamma*|u-v|^2)
            |   3 -- sigmoid: tanh(gamma*u\'\*v + coef0)
        :type kernel_type: int32
        :param weight_label: (default=None)  Default is (Array[Int](0))
        :type weight_label: list
        :param weight: (default=None)  Default is (Array[Double](0.0))
        :type weight: list
        :param epsilon: (default=0.001)  Set tolerance of termination criterion
        :type epsilon: float64
        :param degree: (default=3)  Degree of the polynomial kernel function ('poly').
            Ignored by all other kernels.
        :type degree: int32
        :param gamma: (default=None)  Kernel coefficient for 'rbf', 'poly' and 'sigmoid'.
            Default is 1/n_features.
        :type gamma: float64
        :param coef: (default=0.0)  Independent term in kernel function.
            It is only significant in 'poly' and 'sigmoid'.
        :type coef: float64
        :param nu: (default=0.5)  Set the parameter nu of nu-SVC, one-class SVM,
            and nu-SVR.
        :type nu: float64
        :param cache_size: (default=100.0)  Specify the size of the kernel
            cache (in MB).
        :type cache_size: float64
        :param shrinking: (default=1)  Whether to use the shrinking heuristic.
            Default is 1 (true).
        :type shrinking: int32
        :param probability: (default=0)  Whether to enable probability estimates.
            Default is 0 (false).
        :type probability: int32
        :param nr_weight: (default=1)  NR Weight
        :type nr_weight: int32
        :param c: (default=1.0)  Penalty parameter c of the error term.
        :type c: float64
        :param p: (default=0.1)  Set the epsilon in loss function of epsilon-SVR.
        :type p: float64

        :returns: 
        :rtype: _Unit
        """
        return None



@doc_stub
class LinearRegressionModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Linear Regression model.

        Linear Regression [1]_ is used to model the relationship between a scalar
        dependent variable and one or more independent variables.
        The Linear Regression model is initialized, trained on columns of a frame and
        used to predict the value of the dependent variable given the independent
        observations of a frame.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Linear_regression
        .. [2] https://spark.apache.org/docs/1.5.0/ml-linear-methods.html


        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing two columns.

        >>> frame.inspect()
        [#]  x1   y
        ===============
        [0]  0.0    0.0
        [1]  1.0    2.5
        [2]  2.0    5.0
        [3]  3.0    7.5
        [4]  4.0   10.0
        [5]  5.0   12.5
        [6]  6.0   13.0
        [7]  7.0  17.15
        [8]  8.0   18.5
        [9]  9.0   23.5

        >>> model = ta.LinearRegressionModel()
        [===Job Progress===]
        >>> train_output = model.train(frame,'y',['x1'])
        [===Job Progress===]
        >>> train_output
        {u'explained_variance': 49.27592803030301,
         u'intercept': -0.032727272727271384,
         u'iterations': 3,
         u'label': u'y',
         u'mean_absolute_error': 0.5299393939393939,
         u'mean_squared_error': 0.6300969696969692,
         u'objective_history': [0.5, 0.007324606455391047, 0.006312834669731454],
         u'observation_columns': [u'x1'],
         u'r_2': 0.9873743306605371,
         u'root_mean_squared_error': 0.7937864761363531,
         u'weights': [2.4439393939393934]}
        >>> test_output = model.test(frame,'y')
        [===Job Progress===]
        >>> test_output
        {u'explained_variance': 49.27592803030301,
         u'mean_absolute_error': 0.5299393939393939,
         u'mean_squared_error': 0.6300969696969692,
         u'r_2': 0.9873743306605371,
         u'root_mean_squared_error': 0.7937864761363531}
        >>> predicted_frame = model.predict(frame, ["x1"])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  x1   y      predicted_value
        ==================================
        [0]  4.0   10.0      9.74303030303
        [1]  0.0    0.0   -0.0327272727273
        [2]  1.0    2.5      2.41121212121
        [3]  6.0   13.0      14.6309090909
        [4]  3.0    7.5      7.29909090909
        [5]  7.0  17.15      17.0748484848
        [6]  9.0   23.5      21.9627272727
        [7]  8.0   18.5      19.5187878788
        [8]  5.0   12.5       12.186969697
        [9]  2.0    5.0      4.85515151515


        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Linear Regression Model","model_class":"org.apache.spark.ml.regression.LinearRegressionModel","model_reader":"org.trustedanalytics.atk.scoring.models.LinearRegressionModelReaderPlugin","custom_values":{}},"input":[{"name":"x1","value":"Double"}],"output":[{"name":"x1","value":"Double"},{"name":"Prediction","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=4.0', headers=headers)
        >>> r.text
        u'9.743030303030302'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=4.0&data=0.0', headers=headers)
        >>> r.text
        u'9.743030303030302, -0.032727272727271384' #not working

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"x1": 0.0}]})
        >>> r.text
        u'{"data":[{"x1":0.0,"Prediction":[-0.032727272727271384]}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"x1": 0.0}, {"x1": 4.0}]})
        >>> r.text
        u'{"data":[{"x1":0.0,"Prediction":[-0.032727272727271384]},{"x1":4.0,"Prediction":[9.743030303030302]}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of LinearRegressionModel
        :rtype: LinearRegressionModel
        """
        raise DocStubCalledError("model:linear_regression/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        <Missing Doc>

        :param frame: The frame to predict on
        :type frame: Frame
        :param observation_columns: (default=None)  List of column(s) containing the observations
        :type observation_columns: list

        :returns: 
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the LinearRegressionModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine.
        This model can then be used to predict the target value of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, value_column, observation_columns=None):
        """
        <Missing Doc>

        :param frame: The frame to test the linear regression model on
        :type frame: Frame
        :param value_column: Column name containing the value of each observation
        :type value_column: unicode
        :param observation_columns: (default=None)  List of column(s) containing the observations
        :type observation_columns: list

        :returns: 
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, value_column, observation_columns, elastic_net_parameter=0.0, fit_intercept=True, max_iterations=100, reg_param=0.0, standardization=True, tolerance=1e-06):
        """
        Build linear regression model.

        Creating a LinearRegression Model using the observation column and target column of the train frame

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on
        :type frame: Frame
        :param value_column: Column name containing the value for each observation.
        :type value_column: unicode
        :param observation_columns: List of column(s) containing the
            observations.
        :type observation_columns: list
        :param elastic_net_parameter: (default=0.0)  Parameter for the ElasticNet mixing. Default is 0.0
        :type elastic_net_parameter: float64
        :param fit_intercept: (default=True)  Parameter for whether to fit an intercept term. Default is true
        :type fit_intercept: bool
        :param max_iterations: (default=100)  Parameter for maximum number of iterations. Default is 100
        :type max_iterations: int32
        :param reg_param: (default=0.0)  Parameter for regularization. Default is 0.0
        :type reg_param: float64
        :param standardization: (default=True)  Parameter for whether to standardize the training features before fitting the model. Default is true
        :type standardization: bool
        :param tolerance: (default=1e-06)  Parameter for the convergence tolerance for iterative algorithms. Default is 1E-6
        :type tolerance: float64

        :returns: Trained linear regression model
        :rtype: dict
        """
        return None



@doc_stub
class LogisticRegressionModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of logistic regression model.

        Logistic Regression [1]_ is a widely used supervised binary and multi-class classification algorithm.
        The Logistic Regression model is initialized, trained on columns of a frame, predicts the labels
        of observations, and tests the predicted labels against the true labels.
        This model runs the MLLib implementation of Logistic Regression [2]_, with enhanced features |EM|
        trained model summary statistics; Covariance and Hessian matrices; ability to specify the frequency
        of the train and test observations.
        Testing performance can be viewed via built-in binary and multi-class Classification Metrics.
        It also allows the user to select the optimizer to be used - L-BFGS [3]_ or SGD [4]_.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Logistic_regression
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-linear-methods.html#logistic-regression
        .. [3] https://en.wikipedia.org/wiki/Limited-memory_BFGS
        .. [4] https://en.wikipedia.org/wiki/Stochastic_gradient_descent
            

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  Sepal_Length  Petal_Length  Class
        ======================================
        [0]           4.9           1.4      0
        [1]           4.7           1.3      0
        [2]           4.6           1.5      0
        [3]           6.3           4.9      1
        [4]           6.1           4.7      1
        [5]           6.4           4.3      1
        [6]           6.6           4.4      1
        [7]           7.2           6.0      2
        [8]           7.2           5.8      2
        [9]           7.4           6.1      2

        >>> model = ta.LogisticRegressionModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'Class', ['Sepal_Length', 'Petal_Length'],
        ...                                 num_classes=3, optimizer='LBFGS', compute_covariance=True)
        [===Job Progress===]
        >>> train_output.summary_table
                        coefficients  degrees_freedom  standard_errors  \
        intercept_0        -0.780153                1              NaN
        Sepal_Length_1   -120.442165                1  28497036.888425
        Sepal_Length_0    -63.683819                1  28504715.870243
        intercept_1       -90.484405                1              NaN
        Petal_Length_0    117.979824                1  36178481.415888
        Petal_Length_1    206.339649                1  36172481.900910

                        wald_statistic   p_value
        intercept_0                NaN       NaN
        Sepal_Length_1       -0.000004  1.000000
        Sepal_Length_0       -0.000002  1.000000
        intercept_1                NaN       NaN
        Petal_Length_0        0.000003  0.998559
        Petal_Length_1        0.000006  0.998094

        >>> train_output.covariance_matrix.inspect()
        [#]  Sepal_Length_0      Petal_Length_0      intercept_0
        ===============================================================
        [0]   8.12518826843e+14   -1050552809704907   5.66008788624e+14
        [1]  -1.05055305606e+15   1.30888251756e+15   -3.5175956714e+14
        [2]   5.66010683868e+14  -3.51761845892e+14  -2.52746479908e+15
        [3]   8.12299962335e+14  -1.05039425964e+15   5.66614798332e+14
        [4]  -1.05027789037e+15    1308665462990595    -352436215869081
        [5]     566011198950063  -3.51665950639e+14   -2527929411221601

        [#]  Sepal_Length_1      Petal_Length_1      intercept_1
        ===============================================================
        [0]     812299962806401  -1.05027764456e+15   5.66009303434e+14
        [1]  -1.05039450654e+15   1.30866546361e+15  -3.51663671537e+14
        [2]     566616693386615   -3.5243849435e+14   -2.5279294114e+15
        [3]    8.1208111142e+14   -1050119118230513   5.66615352448e+14
        [4]  -1.05011936458e+15   1.30844844687e+15   -3.5234036349e+14
        [5]     566617247774244  -3.52342642321e+14   -2528394057347494

        >>> predicted_frame = model.predict(frame, ['Sepal_Length', 'Petal_Length'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  Sepal_Length  Petal_Length  Class  predicted_label
        =======================================================
        [0]           4.9           1.4      0                0
        [1]           4.7           1.3      0                0
        [2]           4.6           1.5      0                0
        [3]           6.3           4.9      1                1
        [4]           6.1           4.7      1                1
        [5]           6.4           4.3      1                1
        [6]           6.6           4.4      1                1
        [7]           7.2           6.0      2                2
        [8]           7.2           5.8      2                2
        [9]           7.4           6.1      2                2

        >>> test_metrics = model.test(frame, 'Class', ['Sepal_Length', 'Petal_Length'])
        [===Job Progress===]
        >>> test_metrics
        Precision: 1.0
        Recall: 1.0
        Accuracy: 1.0
        FMeasure: 1.0
        Confusion Matrix:
                    Predicted_0.0  Predicted_1.0  Predicted_2.0
        Actual_0.0              3              0              0
        Actual_1.0              0              4              0
        Actual_2.0              0              0              4

        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of LogisticRegressionModel
        :rtype: LogisticRegressionModel
        """
        raise DocStubCalledError("model:logistic_regression/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict labels for data points using trained logistic regression model.

        Predict the labels for a test frame using trained logistic regression model,
                      and create a new frame revision with existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose labels are to be predicted.
            Default is the labels the model was trained on.
        :type observation_columns: list

        :returns: Frame containing the original frame's columns and a column with the predicted label.
        :rtype: Frame
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: Frame whose labels are to be
            predicted.
        :type frame: Frame
        :param label_column: Column containing the actual
            label for each observation.
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose labels are to be predicted and tested.
            Default is to test over the columns the SVM model
            was trained on.
        :type observation_columns: list

        :returns: A dictionary with binary classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, frequency_column=None, num_classes=2, optimizer='LBFGS', compute_covariance=True, intercept=True, feature_scaling=False, threshold=0.5, reg_type='L2', reg_param=0.0, num_iterations=100, convergence_tolerance=0.0001, num_corrections=10, mini_batch_fraction=1.0, step_size=1.0):
        """
        Build logistic regression model.

        Creating a Logistic Regression Model using the observation column and
        label column of the train frame.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param label_column: Column name containing the label for each
            observation.
        :type label_column: unicode
        :param observation_columns: Column(s) containing the
            observations.
        :type observation_columns: list
        :param frequency_column: (default=None)  Optional column containing the frequency of
            observations.
        :type frequency_column: unicode
        :param num_classes: (default=2)  Number of classes
        :type num_classes: int32
        :param optimizer: (default=LBFGS)  Set type of optimizer.
            | LBFGS - Limited-memory BFGS.
            | LBFGS supports multinomial logistic regression.
            | SGD - Stochastic Gradient Descent.
            | SGD only supports binary logistic regression.
        :type optimizer: unicode
        :param compute_covariance: (default=True)  Compute covariance matrix for the
            model.
        :type compute_covariance: bool
        :param intercept: (default=True)  Add intercept column to training
            data.
        :type intercept: bool
        :param feature_scaling: (default=False)  Perform feature scaling before training
            model.
        :type feature_scaling: bool
        :param threshold: (default=0.5)  Threshold for separating positive predictions from
            negative predictions.
        :type threshold: float64
        :param reg_type: (default=L2)  Set type of regularization
            | L1 - L1 regularization with sum of absolute values of coefficients
            | L2 - L2 regularization with sum of squares of coefficients
        :type reg_type: unicode
        :param reg_param: (default=0.0)  Regularization parameter
        :type reg_param: float64
        :param num_iterations: (default=100)  Maximum number of iterations
        :type num_iterations: int32
        :param convergence_tolerance: (default=0.0001)  Convergence tolerance of iterations for L-BFGS.
            Smaller value will lead to higher accuracy with the cost of more
            iterations.
        :type convergence_tolerance: float64
        :param num_corrections: (default=10)  Number of corrections used in LBFGS update.
            Default is 10.
            Values of less than 3 are not recommended;
            large values will result in excessive computing time.
        :type num_corrections: int32
        :param mini_batch_fraction: (default=1.0)  Fraction of data to be used for each SGD
            iteration
        :type mini_batch_fraction: float64
        :param step_size: (default=1.0)  Initial step size for SGD.
            In subsequent steps, the step size decreases by stepSize/sqrt(t)
        :type step_size: float64

        :returns: An object with a summary of the trained model.
            The data returned is composed of multiple components\:

            | **int** : *numFeatures*
            |   Number of features in the training data
            | **int** : *numClasses*
            |   Number of classes in the training data
            | **table** : *summaryTable*
            |   A summary table composed of:
            | **Frame** : *CovarianceMatrix (optional)*
            |   Covariance matrix of the trained model.
            The covariance matrix is the inverse of the Hessian matrix for the trained model.
            The Hessian matrix is the second-order partial derivatives of the model's log-likelihood function.
        :rtype: dict
        """
        return None



@doc_stub
class NaiveBayesModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Naive Bayes model

        Naive Bayes [1]_ is a probabilistic classifier with strong
        independence assumptions between features.
        It computes the conditional probability distribution of each feature given label,
        and then applies Bayes' theorem to compute the conditional probability
        distribution of a label given an observation, and use it for prediction.
        The Naive Bayes model is initialized, trained on columns of a frame, tested against true labels of a frame and used
        to predict the value of the dependent variable given the independent
        observations of a frame and test the performance of the classification on test data.
        This model runs the MLLib implementation of Naive Bayes [2]_.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Naive_Bayes_classifier
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-naive-bayes.html
                     

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  Class  Dim_1          Dim_2
        =======================================
        [0]      1  19.8446136104  2.2985856384
        [1]      1  16.8973559126  2.6933495054
        [2]      1   5.5548729596  2.7777687995
        [3]      0  46.1810010826  3.1611961917
        [4]      0  44.3117586448  3.3458963222
        [5]      0  34.6334526911  3.6429838715

        >>> model = ta.NaiveBayesModel()
        [===Job Progress===]
        >>> model.train(frame, 'Class', ['Dim_1', 'Dim_2'], lambda_parameter=0.9)
        [===Job Progress===]
        >>> predicted_frame = model.predict(frame, ['Dim_1', 'Dim_2'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  Class  Dim_1          Dim_2         predicted_class
        ========================================================
        [0]      1  19.8446136104  2.2985856384              0.0
        [1]      1  16.8973559126  2.6933495054              1.0
        [2]      1   5.5548729596  2.7777687995              1.0
        [3]      0  46.1810010826  3.1611961917              0.0
        [4]      0  44.3117586448  3.3458963222              0.0
        [5]      0  34.6334526911  3.6429838715              0.0

        >>> test_metrics = model.test(frame, 'Class', ['Dim_1','Dim_2'])
        [===Job Progress===]
        >>> test_metrics
        Precision: 1.0
        Recall: 0.666666666667
        Accuracy: 0.833333333333
        FMeasure: 0.8
        Confusion Matrix:
                    Predicted_Pos  Predicted_Neg
        Actual_Pos              2              1
        Actual_Neg              0              3
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> # asdfasdf
        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Naive Bayes Model","model_class":"org.apache.spark.mllib.classification.NaiveBayesScoringModel","model_reader":"org.trustedanalytics.atk.scoring.models.NaiveBayesReaderPlugin","custom_values":{}},"input":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"}],"output":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"},{"name":"score","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446, 2.298585', headers=headers)
        >>> r.text
        u'0.0'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446&data=5.5548729596, 2.7777687995', headers=headers)
        >>> r.text
        u'0.0,1.0'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446, "Dim_2": 2.298585}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446,"Dim_2":2.298585,"score":[0.0]}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446, "Dim_2": 2.298585}, {"Dim_1": 5.5548729596 , "Dim_2": 2.7777687995}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446,"Dim_2":2.298585,"score":[0.0]},{"Dim_1":5.5548729596,"Dim_2":2.7777687995,"score":[1.0]}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of NaiveBayesModel
        :rtype: NaiveBayesModel
        """
        raise DocStubCalledError("model:naive_bayes/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict labels for data points using trained Naive Bayes model.

        Predict the labels for a test frame using trained Naive Bayes model,
              and create a new frame revision with existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the
            observations whose labels are to be predicted.
            By default, we predict the labels over columns the NaiveBayesModel
            was trained on.
        :type observation_columns: list

        :returns: Frame containing the original frame's columns and a column with the predicted label.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a scoring engine tar file.

        Creates a tar file with the trained Naive Bayes Model
        The tar file is used as input to the scoring engine to predict the class of an observation.



        :returns: The HDFS path to the tar file.
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param label_column: Column containing the actual
            label for each observation.
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the
            observations whose labels are to be predicted.
            By default, we predict the labels over columns the NaiveBayesModel
            was trained on.
        :type observation_columns: list

        :returns: A dictionary with binary classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, lambda_parameter=1.0):
        """
        Build a naive bayes model.

        Train a NaiveBayesModel using the observation column, label column of the train frame and an optional lambda value.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param label_column: Column containing the label for each
            observation.
        :type label_column: unicode
        :param observation_columns: Column(s) containing the
            observations.
        :type observation_columns: list
        :param lambda_parameter: (default=1.0)  Additive smoothing parameter
            Default is 1.0.
        :type lambda_parameter: float64

        :returns: 
        :rtype: _Unit
        """
        return None



@doc_stub
class PowerIterationClusteringModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a PowerIterationClustering model.

        Power Iteration Clustering [1]_ is a scalable and efficient algorithm for clustering vertices of a graph given pairwise similarities as edge properties.
        A Power Iteration Clustering model is initialized and the cluster assignments of the vertices can be predicted on specifying the source column, destination column and similarity column of the given frame.

        .. rubric:: footnotes

        .. [1] http://www.cs.cmu.edu/~wcohen/postscript/icm12010-pic-final.pdf
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-clustering.html#power-iteration-clustering-pic

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns denoting the source vertex, destination vertex and corresponding similarity.

        >>> frame.inspect()
        [#]  Source  Destination  Similarity
        ====================================
        [0]       1            2         1.0
        [1]       1            3         0.3
        [2]       2            3         0.3
        [3]       3            0        0.03
        [4]       0            5        0.01
        [5]       5            4         0.3
        [6]       5            6         1.0
        [7]       4            6         0.3

        >>> model = ta.PowerIterationClusteringModel()
        [===Job Progress===]
        >>> predict_output = model.predict(frame, 'Source', 'Destination', 'Similarity', k=3)
        [===Job Progress===]
        >>> predict_output['predicted_frame'].inspect()
        [#]  id  cluster
        ================
        [0]   4        3
        [1]   0        2
        [2]   1        1
        [3]   6        1
        [4]   3        3
        [5]   5        1
        [6]   2        1

        >>> predict_output['cluster_size']
        {u'Cluster:1': 4, u'Cluster:2': 1, u'Cluster:3': 2}
        >>> predict_output['number_of_clusters']
        3


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of PowerIterationClustering Model
        :rtype: PowerIterationClusteringModel
        """
        raise DocStubCalledError("model:power_iteration_clustering/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, source_column, destination_column, similarity_column, k=2, max_iterations=100, initialization_mode='random'):
        """
        Predict the clusters to which the nodes belong to

        Predict the cluster assignments for the nodes of the graph and create a new frame with a column storing node id and a column with corresponding cluster assignment

        See :doc:`here <new>` for examples.

        :param frame: Frame storing the graph to be clustered
        :type frame: Frame
        :param source_column: Name of the column containing the source node
        :type source_column: unicode
        :param destination_column: Name of the column containing the destination node
        :type destination_column: unicode
        :param similarity_column: Name of the column containing the similarity
        :type similarity_column: unicode
        :param k: (default=2)  Number of clusters to cluster the graph into. Default is 2
        :type k: int32
        :param max_iterations: (default=100)  Maximum number of iterations of the power iteration loop. Default is 100
        :type max_iterations: int32
        :param initialization_mode: (default=random)  Initialization mode of power iteration clustering. This can be either "random" to use a
            random vector as vertex properties, or "degree" to use normalized sum similarities. Default is "random".
        :type initialization_mode: unicode

        :returns: Dictionary containing clustering results
            |    predicted_frame : Frame
            |        A new frame with a column 'id' with the node id, and a column 'cluster' with the node's cluster assignment
            |    number_of_clusters : int
            |        Quantity of clusters used
            |    cluster_size : dict
            |        Cluster populations, keyed by names 'Cluster:1' through 'Cluster:n'
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None



@doc_stub
class PrincipalComponentsModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Principal Components model.

        Principal component analysis [1]_ is a statistical algorithm
        that converts possibly correlated features to linearly uncorrelated variables
        called principal components.
        The number of principal components is less than or equal to the number of
        original variables.
        This implementation of computing Principal Components is done by Singular
        Value Decomposition [2]_ of the data, providing the user with an option to
        mean center the data.
        The Principal Components model is initialized; trained on
        specifying the observation columns of the frame and the number of components;
        used to predict principal components.
        The MLLib Singular Value Decomposition [3]_ implementation has been used for
        this, with additional features to 1) mean center the data during train and
        predict and 2) compute the t-squared index during prediction.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Principal_component_analysis
        .. [2] https://en.wikipedia.org/wiki/Singular_value_decomposition
        .. [3] https://spark.apache.org/docs/1.5.0/mllib-dimensionality-reduction.html

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing six columns.

        >>> frame.inspect()
        [#]  1    2    3    4    5    6
        =================================
        [0]  2.6  1.7  0.3  1.5  0.8  0.7
        [1]  3.3  1.8  0.4  0.7  0.9  0.8
        [2]  3.5  1.7  0.3  1.7  0.6  0.4
        [3]  3.7  1.0  0.5  1.2  0.6  0.3
        [4]  1.5  1.2  0.5  1.4  0.6  0.4
        >>> model = ta.PrincipalComponentsModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, ['1','2','3','4','5','6'], mean_centered=True, k=6)
        [===Job Progress===]
        >>> train_output
        {u'k': 6, u'column_means': [2.92, 1.48, 0.4, 1.3, 0.7, 0.52], u'observation_columns': [u'1', u'2', u'3', u'4', u'5', u'6'], u'mean_centered': True, u'right_singular_vectors': [[-0.9906468642089332, 0.11801374544146297, 0.025647010353320242, 0.048525096275535286, -0.03252674285233843, 0.02492194235385788], [-0.07735139793384983, -0.6023104604841424, 0.6064054412059493, -0.4961696216881456, -0.12443126544906798, -0.042940400527513106], [0.028850639537397756, 0.07268697636708575, -0.2446393640059097, -0.17103491337994586, -0.9368360903028429, 0.16468461966702994], [0.10576208410025369, 0.5480329468552815, 0.75230590898727, 0.2866144016081251, -0.20032699877119212, 0.015210798298156058], [-0.024072151446194606, -0.30472267167437633, -0.01125936644585159, 0.48934541040601953, -0.24758962014033054, -0.7782533654748628], [-0.0061729539518418355, -0.47414707747028795, 0.07533458226215438, 0.6329307498105832, -0.06607181431092408, 0.6037419362435869]], u'singular_values': [1.8048170096632419, 0.8835344148403882, 0.7367461843294286, 0.15234027471064404, 5.90167578565564e-09, 4.478916578455115e-09]}
        >>> train_output['column_means']
        [2.92, 1.48, 0.4, 1.3, 0.7, 0.52]
        >>> predicted_frame = model.predict(frame, mean_centered=True, t_squared_index=True, observation_columns=['1','2','3','4','5','6'], c=3)
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  1    2    3    4    5    6    p_1              p_2
        ===================================================================
        [0]  2.6  1.7  0.3  1.5  0.8  0.7   0.314738695012  -0.183753549226
        [1]  3.3  1.8  0.4  0.7  0.9  0.8  -0.471198363594  -0.670419608227
        [2]  3.5  1.7  0.3  1.7  0.6  0.4  -0.549024749481   0.235254068619
        [3]  3.7  1.0  0.5  1.2  0.6  0.3  -0.739501762517   0.468409769639
        [4]  1.5  1.2  0.5  1.4  0.6  0.4    1.44498618058   0.150509319195
        <BLANKLINE>
        [#]  p_3              t_squared_index
        =====================================
        [0]   0.312561560113   0.253649649849
        [1]  -0.228746130528   0.740327252782
        [2]   0.465756549839   0.563086507007
        [3]  -0.386212142456   0.723748467549
        [4]  -0.163359836968   0.719188122813
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Principal Components Model","model_class":"org.trustedanalytics.atk.scoring.models.PrincipalComponentsScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.PrincipalComponentsModelReaderPlugin","custom_values":{}},"input":[{"name":"1","value":"Double"},{"name":"2","value":"Double"},{"name":"3","value":"Double"},{"name":"4","value":"Double"},{"name":"5","value":"Double"},{"name":"6","value":"Double"}],"output":[{"name":"1","value":"Double"},{"name":"2","value":"Double"},{"name":"3","value":"Double"},{"name":"4","value":"Double"},{"name":"5","value":"Double"},{"name":"6","value":"Double"},{"name":"principal_components","value":"List[Double]"},{"name":"t_squared_index","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2.6,  1.7,  0.3,  1.5,  0.8,  0.7', headers=headers)
        >>> r.text
        u'0.8000000000000014'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=2.6,  1.7,  0.3,  1.5,  0.8,  0.7&data=1.5,  1.2,  0.5,  1.4,  0.6,  0.4', headers=headers)
        >>> r.text
        u'0.8000000000000014,0.7999999999999993'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"1": 2.6, "2": 1.7, "3": 0.3, "4": 1.5, "5": 0.8, "6": 0.7}]})
        >>> r.text
        u'{"data":[{"t_squared_index":0.8000000000000014,"4":1.5,"5":0.8,"6":0.7,"1":2.6,"principal_components":[0.31473869501177154,-0.18375354922552106,0.31256156011289404,0.11260310008656331,-1.8388068845354155E-16,2.0816681711721685E-16],"2":1.7,"3":0.3}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"1": 2.6, "2": 1.7, "3": 0.3, "4": 1.5, "5": 0.8, "6": 0.7}, {"1": 1.5, "2": 1.2, "3": 0.5, "4": 1.4, "5": 0.6, "6":0.4}]})
        >>> r.text
        u'{"data":[{"t_squared_index":0.8000000000000014,"4":1.5,"5":0.8,"6":0.7,"1":2.6,"principal_components":[0.31473869501177154,-0.18375354922552106,0.31256156011289404,0.11260310008656331,-1.8388068845354155E-16,2.0816681711721685E-16],"2":1.7,"3":0.3},{"t_squared_index":0.7999999999999993,"4":1.4,"5":0.6,"6":0.4,"1":1.5,"principal_components":[1.4449861805807689,0.15050931919479138,-0.16335983696811784,-0.04330642483363326,7.632783294297951E-17,6.938893903907228E-17],"2":1.2,"3":0.5}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of PrincipalComponentsModel
        :rtype: PrincipalComponentsModel
        """
        raise DocStubCalledError("model:principal_components/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, mean_centered=True, t_squared_index=False, observation_columns=None, c=None, name=None):
        """
        Predict using principal components model.

        Predicting on a dataframe's columns using a PrincipalComponents Model.

        See :doc:`here <new>` for examples.

        :param frame: Frame whose principal components are to be computed.
        :type frame: Frame
        :param mean_centered: (default=True)  Option to mean center the columns. Default is true
        :type mean_centered: bool
        :param t_squared_index: (default=False)  Indicator for whether the t-square index is to be computed. Default is false.
        :type t_squared_index: bool
        :param observation_columns: (default=None)  List of observation column name(s) to be used for prediction. Default is the list of column name(s) used to train the model.
        :type observation_columns: list
        :param c: (default=None)  The number of principal components to be predicted. 'c' cannot be greater than the count used to train the model. Default is the count used to train the model.
        :type c: int32
        :param name: (default=None)  The name of the output frame generated by predict.
        :type name: unicode

        :returns: A frame with existing columns and following additional columns\:
                  'c' additional columns: containing the projections of V on the the frame
                  't_squared_index': column storing the t-square-index value, if requested
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the PrincipalComponentsModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine. This model can
        then be used to compute the principal components and t-squared index(if requested) of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, observation_columns, mean_centered=True, k=None):
        """
        Build principal components model.

        Creating a PrincipalComponents Model using the observation columns.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model
            on.
        :type frame: Frame
        :param observation_columns: List of column(s) containing
            the observations.
        :type observation_columns: list
        :param mean_centered: (default=True)  Option to mean center the
            columns
        :type mean_centered: bool
        :param k: (default=None)  Principal component count.
            Default is the number of observation columns
        :type k: int32

        :returns: dictionary
                |A dictionary with trained Principal Components Model with the following keys\:
                |'column_means': the list of the means of each observation column
                |'k': number of principal components used to train the model
                |'mean_centered': Flag indicating if the model was mean centered during training
                |'observation_columns': the list of observation columns on which the model was trained,
                |'right_singular_vectors': list of a list storing the right singular vectors of the specified columns of the input frame
                |'singular_values': list storing the singular values of the specified columns of the input frame
              
        :rtype: dict
        """
        return None



@doc_stub
class RandomForestClassifierModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Random Forest Classifier model.

        Random Forest [1]_ is a supervised ensemble learning algorithm
        which can be used to perform binary and multi-class classification.
        The Random Forest Classifier model is initialized, trained on columns of a
        frame, used to predict the labels of observations in a frame, and tests the
        predicted labels against the true labels.
        This model runs the MLLib implementation of Random Forest [2]_.
        During training, the decision trees are trained in parallel.
        During prediction, each tree's prediction is counted as vote for one class.
        The label is predicted to be the class which receives the most votes.
        During testing, labels of the observations are predicted and tested against the true labels
        using built-in binary and multi-class Classification Metrics.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Random_forest
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-ensembles.html#random-forests
         

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  Class  Dim_1          Dim_2
        =======================================
        [0]      1  19.8446136104  2.2985856384
        [1]      1  16.8973559126  2.6933495054
        [2]      1   5.5548729596  2.7777687995
        [3]      0  46.1810010826  3.1611961917
        [4]      0  44.3117586448  3.3458963222
        [5]      0  34.6334526911  3.6429838715
        >>> model = ta.RandomForestClassifierModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'Class', ['Dim_1', 'Dim_2'], num_classes=2, num_trees=1, impurity="entropy", max_depth=4, max_bins=100)
        [===Job Progress===]
        >>> train_output
        {u'impurity': u'entropy', u'max_bins': 100, u'observation_columns': [u'Dim_1', u'Dim_2'], u'num_nodes': 3, u'max_depth': 4, u'seed': 157264076, u'num_trees': 1, u'label_column': u'Class', u'feature_subset_category': u'all', u'num_classes': 2}
        >>> train_output['num_nodes']
        3
        >>> train_output['label_column']
        u'Class'
        >>> predicted_frame = model.predict(frame, ['Dim_1', 'Dim_2'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  Class  Dim_1          Dim_2         predicted_class
        ========================================================
        [0]      1  19.8446136104  2.2985856384                1
        [1]      1  16.8973559126  2.6933495054                1
        [2]      1   5.5548729596  2.7777687995                1
        [3]      0  46.1810010826  3.1611961917                0
        [4]      0  44.3117586448  3.3458963222                0
        [5]      0  34.6334526911  3.6429838715                0
        >>> test_metrics = model.test(frame, 'Class', ['Dim_1','Dim_2'])
        [===Job Progress===]
        >>> test_metrics
        Precision: 1.0
        Recall: 1.0
        Accuracy: 1.0
        FMeasure: 1.0
        Confusion Matrix:
                    Predicted_Pos  Predicted_Neg
        Actual_Pos              3              0
        Actual_Neg              0              3
        >>> model.publish()
        [===Job Progress===]


        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Random Forest Classifier Model","model_class":"org.trustedanalytics.atk.scoring.models.RandomForestClassifierScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.RandomForestClassifierModelReaderPlugin","custom_values":{}},"input":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"}],"output":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"},{"name":"Prediction","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446, 2.2985856', headers=headers)
        >>> r.text
        u'1.0'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446, 2.2985856&data=46.1810010826, 3.1611961917', headers=headers)
        >>> r.text
        u'1.0,0.0'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446, "Dim_2": 2.2985856}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446,"Dim_2":2.2985856,"Prediction":1.0}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446, "Dim_2": 2.2985856}, {"Dim_1": 46.1810010826, "Dim_2": 3.1611961917}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446,"Dim_2":2.2985856,"Prediction":1.0},{"Dim_1":46.1810010826,"Dim_2":3.1611961917,"Prediction":0.0}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of RandomForestClassifierModel
        :rtype: RandomForestClassifierModel
        """
        raise DocStubCalledError("model:random_forest_classifier/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict the labels for the data points.

        Predict the labels for a test frame using trained Random Forest Classifier model,
        and create a new frame revision with existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations whose labels are to be predicted.
            By default, we predict the labels over columns the RandomForestModel
            was trained on. 
        :type observation_columns: list

        :returns: A new frame consisting of the existing columns of the frame and
            a new column with predicted label for each observation.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the RandomForestClassifierModel and its implementation into a tar file. 
          The tar file is then published on HDFS and this method returns the path to the tar file. 
          The tar file serves as input to the scoring engine. This model can then be used to predict the cluster assignment of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: The frame whose labels are to be predicted
        :type frame: Frame
        :param label_column: Column containing the true labels of the observations
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the observations whose labels are to be predicted.
            By default, we predict the labels over columns the RandomForest was trained on.
        :type observation_columns: list

        :returns: A dictionary with binary classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, num_classes=2, num_trees=1, impurity='gini', max_depth=4, max_bins=100, seed=-2089304399, categorical_features_info=None, feature_subset_category=None):
        """
        Build Random Forests Classifier model.

        Creating a Random Forests Classifier Model using the observation columns and label column.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on
        :type frame: Frame
        :param label_column: Column name containing the label for each observation
        :type label_column: unicode
        :param observation_columns: Column(s) containing the observations
        :type observation_columns: list
        :param num_classes: (default=2)  Number of classes for classification. Default is 2.
        :type num_classes: int32
        :param num_trees: (default=1)  Number of tress in the random forest. Default is 1.
        :type num_trees: int32
        :param impurity: (default=gini)  Criterion used for information gain calculation. Supported values "gini" or "entropy". Default is "gini".
        :type impurity: unicode
        :param max_depth: (default=4)  Maximum depth of the tree. Default is 4.
        :type max_depth: int32
        :param max_bins: (default=100)  Maximum number of bins used for splitting features. Default is 100.
        :type max_bins: int32
        :param seed: (default=-2089304399)  Random seed for bootstrapping and choosing feature subsets. Default is a randomly chosen seed.
        :type seed: int32
        :param categorical_features_info: (default=None)  Arity of categorical features. Entry (n-> k) indicates that feature 'n' is categorical with 'k' categories indexed from 0:{0,1,...,k-1}.
        :type categorical_features_info: dict
        :param feature_subset_category: (default=None)  Number of features to consider for splits at each node. Supported values "auto","all","sqrt","log2","onethird".  If "auto" is set, this is based on num_trees: if num_trees == 1, set to "all" ; if num_trees > 1, set to "sqrt"
        :type feature_subset_category: unicode

        :returns: dictionary
                  A dictionary with trained Random Forest Classifier model with the following keys\:
                  |'observation_columns': the list of observation columns on which the model was trained,
                  |'label_column': the column name containing the labels of the observations,
                  |'num_classes': the number of classes,
                  |'num_trees': the number of decision trees in the random forest,
                  |'num_nodes': the number of nodes in the random forest,
                  |'feature_subset_category': the map storing arity of categorical features,
                  |'impurity': the criterion used for information gain calculation,
                  |'max_depth': the maximum depth of the tree,
                  |'max_bins': the maximum number of bins used for splitting features,
                  |'seed': the random seed used for bootstrapping and choosing feature subset.
                
        :rtype: dict
        """
        return None



@doc_stub
class RandomForestRegressorModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Random Forest Regressor model.

        Random Forest [1]_ is a supervised ensemble learning algorithm
        used to perform regression.
        A Random Forest Regressor model is initialized, trained on columns of a frame,
        and used to predict the value of each observation in the frame.
        This model runs the MLLib implementation of Random Forest [2]_.
        During training, the decision trees are trained in parallel.
        During prediction, the average over-all tree's predicted value is the predicted
        value of the random forest.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Random_forest
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-ensembles.html#random-forests

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  Class  Dim_1          Dim_2
        =======================================
        [0]      1  19.8446136104  2.2985856384
        [1]      1  16.8973559126  2.6933495054
        [2]      1   5.5548729596  2.7777687995
        [3]      0  46.1810010826  3.1611961917
        [4]      0  44.3117586448  3.3458963222
        [5]      0  34.6334526911  3.6429838715
        >>> model = ta.RandomForestRegressorModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'Class', ['Dim_1', 'Dim_2'], num_trees=1, impurity="variance", max_depth=4, max_bins=100)
        [===Job Progress===]
        >>> train_output
        {u'impurity': u'variance', u'max_bins': 100, u'observation_columns': [u'Dim_1', u'Dim_2'], u'num_nodes': 3, u'max_depth': 4, u'seed': -1632404927, u'num_trees': 1, u'label_column': u'Class', u'feature_subset_category': u'all'}
        >>> train_output['num_nodes']
        3
        >>> train_output['label_column']
        u'Class'
        >>> predicted_frame = model.predict(frame, ['Dim_1', 'Dim_2'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  Class  Dim_1          Dim_2         predicted_value
        ========================================================
        [0]      1  19.8446136104  2.2985856384                1.0
        [1]      1  16.8973559126  2.6933495054                1.0
        [2]      1   5.5548729596  2.7777687995                1.0
        [3]      0  46.1810010826  3.1611961917                0.0
        [4]      0  44.3117586448  3.3458963222                0.0
        [5]      0  34.6334526911  3.6429838715                0.0
        >>> model.publish()
        [===Job Progress===]

        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"Random Forest Regressor Model","model_class":"org.trustedanalytics.atk.scoring.models.RandomForestRegressorScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.RandomForestRegressorModelReaderPlugin","custom_values":{}},"input":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"}],"output":[{"name":"Dim_1","value":"Double"},{"name":"Dim_2","value":"Double"},{"name":"Prediction","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446136, 2.2985856384', headers=headers)
        >>> r.text
        u'1.0'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=19.8446136, 2.2985856384&data=46.1810010826, 3.1611961917', headers=headers)
        >>> r.text
        u'1.0,0.0'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446136, "Dim_2": 2.2985856384}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446136,"Dim_2":2.2985856384,"Prediction":1.0}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"Dim_1": 19.8446136, "Dim_2": 2.2985856384}, {"Dim_1": 46.1810010826, "Dim_2": 3.1611961917}]})
        >>> r.text
        u'{"data":[{"Dim_1":19.8446136,"Dim_2":2.2985856384,"Prediction":1.0},{"Dim_1":46.1810010826,"Dim_2":3.1611961917,"Prediction":0.0}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of RandomForestRegressor Model
        :rtype: RandomForestRegressorModel
        """
        raise DocStubCalledError("model:random_forest_regressor/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict the values for the data points.

        Predict the values for a test frame using trained Random Forest Classifier model, and create a new frame revision with
        existing columns and a new predicted value's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations whose labels are to be predicted.
            By default, we predict the labels over columns the Random Forest model
            was trained on. 
        :type observation_columns: list

        :returns: A new frame consisting of the existing columns of the frame and
            a new column with predicted value for each observation.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the RandomForestRegressorModel and its implementation into a tar file. The tar file is then published
        on HDFS and this method returns the path to the tar file. The tar file serves as input to the scoring engine.
        This model can then be used to predict the target value of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def train(self, frame, value_column, observation_columns, num_trees=1, impurity='variance', max_depth=4, max_bins=100, seed=-324551543, categorical_features_info=None, feature_subset_category=None):
        """
        Build Random Forests Regressor model.

        Creating a Random Forests Regressor Model using the observation columns and target column.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on
        :type frame: Frame
        :param value_column: Column name containing the value for each observation
        :type value_column: unicode
        :param observation_columns: Column(s) containing the observations
        :type observation_columns: list
        :param num_trees: (default=1)  Number of trees in the random forest. Default is 1.
        :type num_trees: int32
        :param impurity: (default=variance)  Criterion used for information gain calculation. Default supported value is "variance".
        :type impurity: unicode
        :param max_depth: (default=4)  Maxium depth of the tree. Default is 4.
        :type max_depth: int32
        :param max_bins: (default=100)  Maximum number of bins used for splitting features. Default is 100.
        :type max_bins: int32
        :param seed: (default=-324551543)  Random seed for bootstrapping and choosing feature subsets. Default is a randomly chosen seed.
        :type seed: int32
        :param categorical_features_info: (default=None)  Arity of categorical features. Entry (n-> k) indicates that feature 'n' is categorical with 'k' categories indexed from 0:{0,1,...,k-1}
        :type categorical_features_info: dict
        :param feature_subset_category: (default=None)  Number of features to consider for splits at each node. Supported values "auto", "all", "sqrt","log2", "onethird".
            If "auto" is set, this is based on numTrees: if numTrees == 1, set to "all"; if numTrees > 1, set to "onethird".
        :type feature_subset_category: unicode

        :returns: dictionary
                  |A dictionary with trained Random Forest Regressor model with the following keys\:
                  |'observation_columns': the list of observation columns on which the model was trained
                  |'label_columns': the column name containing the labels of the observations
                  |'num_trees': the number of decision trees in the random forest
                  |'num_nodes': the number of nodes in the random forest
                  |'categorical_features_info': the map storing arity of categorical features
                  |'impurity': the criterion used for information gain calculation
                  |'max_depth': the maximum depth of the tree
                  |'max_bins': the maximum number of bins used for splitting features
                  |'seed': the random seed used for bootstrapping and choosing featur subset
                
        :rtype: dict
        """
        return None



@doc_stub
class SvmModel(object):
    """
    Auto-generated to contain doc stubs for static program analysis
    """


    def __init__(self, name=None):
        """
            Create a 'new' instance of a Support Vector Machine model.

        Support Vector Machine [1]_ is a supervised algorithm used to
        perform binary classification.
        A Support Vector Machine constructs a high dimensional hyperplane which is
        said to achieve a good separation when a hyperplane has the largest distance
        to the nearest training-data point of any class.
        This model runs the MLLib implementation of SVM [2]_ with SGD [3]_ optimizer.
        The SVMWithSGD model is initialized, trained on columns of a frame, used to
        predict the labels of observations in a frame, and tests the predicted labels
        against the true labels.
        During testing, labels of the observations are predicted and tested against
        the true labels using built-in binary Classification Metrics.

        .. rubric:: footnotes

        .. [1] https://en.wikipedia.org/wiki/Support_vector_machine
        .. [2] https://spark.apache.org/docs/1.5.0/mllib-linear-methods.html#linear-support-vector-machines-svms
        .. [3] https://en.wikipedia.org/wiki/Stochastic_gradient_descent

        Consider the following model trained and tested on the sample data set in *frame* 'frame'.

        Consider the following frame containing three columns.

        >>> frame.inspect()
        [#]  data   label
        =================
        [0]  -48.0  1
        [1]  -75.0  1
        [2]  -63.0  1
        [3]  -57.0  1
        [4]   73.0  0
        [5]  -33.0  1
        [6]  100.0  0
        [7]  -54.0  1
        [8]   78.0  0
        [9]   48.0  0

        >>> model = ta.SvmModel()
        [===Job Progress===]
        >>> train_output = model.train(frame, 'label', ['data'])
        [===Job Progress===]

        >>> predicted_frame = model.predict(frame, ['data'])
        [===Job Progress===]
        >>> predicted_frame.inspect()
        [#]  data   label  predicted_label
        ==================================
        [0]  -48.0  1                    1
        [1]  -75.0  1                    1
        [2]  -63.0  1                    1
        [3]  -57.0  1                    1
        [4]   73.0  0                    0
        [5]  -33.0  1                    1
        [6]  100.0  0                    0
        [7]  -54.0  1                    1
        [8]   78.0  0                    0
        [9]   48.0  0                    0


        >>> test_metrics = model.test(predicted_frame, 'predicted_label')
        [===Job Progress===]

        >>> test_metrics
        Precision: 1.0
        Recall: 1.0
        Accuracy: 1.0
        FMeasure: 1.0
        Confusion Matrix:
                    Predicted_Pos  Predicted_Neg
        Actual_Pos              7              0
        Actual_Neg              0              7

        >>> model.publish()
        [===Job Progress===]


        Take the path to the published model and run it in the Scoring Engine

        >>> import requests
        >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json,text/plain'}

        Posting a request to get the metadata about the model

        >>> r =requests.get('http://mymodel.demotrustedanalytics.com/v2/metadata')
        >>> r.text
        u'{"model_details":{"model_type":"SVM with SGD Model","model_class":"org.trustedanalytics.atk.scoring.models.SVMWithSGDScoreModel","model_reader":"org.trustedanalytics.atk.scoring.models.SVMWithSGDModelReaderPlugin","custom_values":{}},"input":[{"name":"data","value":"Double"}],"output":[{"name":"data","value":"Double"},{"name":"Prediction","value":"Double"}]}'

        Posting a request to version 1 of Scoring Engine supporting strings for requests and response:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=-48.0', headers=headers)
        >>> r.text
        u'1.0'

        Posting a request to version 1 with multiple records to score:

        >>> r = requests.post('http://mymodel.demotrustedanalytics.com/v1/score?data=-48.0&data=73.0', headers=headers)
        >>> r.text
        u'1.0,0.0'

        Posting a request to version 2 of Scoring Engine supporting Json for requests and responses.

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"data": -48.0}]})
        >>> r.text
        u'{"data":[{"data":-48.0,"Prediction":1.0}]}'

        Posting a request to version 2 with multiple records to score:

        >>> r = requests.post("http://mymodel.demotrustedanalytics.com/v2/score", json={"records": [{"data": -48.0},{"data": 73.0}]})
        >>> r.text
        u'{"data":[{"data":-48.0,"Prediction":1.0},{"data":73.0,"Prediction":0.0}]}'


        :param name: (default=None)  User supplied name.
        :type name: unicode

        :returns: A new instance of SvmModel
        :rtype: SvmModel
        """
        raise DocStubCalledError("model:svm/new")


    @property
    @doc_stub
    def last_read_date(self):
        """
        Read-only property - Last time this model's data was accessed.



        :returns: Date string of the last time this model's data was accessed
        :rtype: str
        """
        return None


    @property
    @doc_stub
    def name(self):
        """
        Set or get the name of the model object.

        Change or retrieve model object identification.
        Identification names must start with a letter and are limited to
        alphanumeric characters and the ``_`` character.


        Examples
        --------

        .. code::

            >>> my_model.name
            "abc"

            >>> my_model.name = "xyz"
            >>> my_model.name
            "xyz"




        """
        return None


    @doc_stub
    def predict(self, frame, observation_columns=None):
        """
        Predict the labels for the data points

        Predict the labels for a test frame and create a new frame revision with
        existing columns and a new predicted label's column.

        See :doc:`here <new>` for examples.

        :param frame: A frame whose labels are to be predicted.
            By default, predict is run on the same columns over which the model is
            trained.
        :type frame: Frame
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose labels are to be predicted.
            Default is the labels the model was trained on.
        :type observation_columns: list

        :returns: A frame containing the original frame's columns and a column with the
            predicted label.
        :rtype: Frame
        """
        return None


    @doc_stub
    def publish(self):
        """
        Creates a tar file that will be used as input to the scoring engine

        The publish method exports the SVMModel and its implementation into a tar file.
          The tar file is then published on HDFS and this method returns the path to the tar file.
          The tar file serves as input to the scoring engine. This model can then be used to predict the class of an observation.

        See :doc:`here <new>` for examples.



        :returns: Returns the HDFS path to the trained model's tar file
        :rtype: dict
        """
        return None


    @property
    @doc_stub
    def status(self):
        """
        Read-only property - Current model life cycle status.

        One of three statuses: Active, Dropped, Finalized
           Active:    Entity is available for use
           Dropped:   Entity has been dropped by user or by garbage collection which found it stale
           Finalized: Entity's data has been deleted




        :returns: Status of the model
        :rtype: str
        """
        return None


    @doc_stub
    def test(self, frame, label_column, observation_columns=None):
        """
        Predict test frame labels and return metrics.

        Predict the labels for a test frame and run classification metrics on predicted
        and target labels.

        See :doc:`here <new>` for examples.

        :param frame: Frame whose labels are to be
            predicted.
        :type frame: Frame
        :param label_column: Column containing the actual
            label for each observation.
        :type label_column: unicode
        :param observation_columns: (default=None)  Column(s) containing the observations
            whose labels are to be predicted and tested.
            Default is to test over the columns the SVM model
            was trained on.
        :type observation_columns: list

        :returns: A dictionary with binary classification metrics.
            The data returned is composed of the following keys\:

                          |  'accuracy' : double
                          |  The proportion of predictions that are correctly identified
                          |  'confusion_matrix' : dictionary
                          |  A table used to describe the performance of a classification model
                          |  'f_measure' : double
                          |  The harmonic mean of precision and recall
                          |  'precision' : double
                          |  The proportion of predicted positive instances that are correctly identified
                          |  'recall' : double
                          |  The proportion of positive instances that are correctly identified.
        :rtype: dict
        """
        return None


    @doc_stub
    def train(self, frame, label_column, observation_columns, intercept=True, num_iterations=100, step_size=1.0, reg_type=None, reg_param=0.01, mini_batch_fraction=1.0):
        """
        Build SVM with SGD model

        Creating a SVM Model using the observation column and label column of the train frame.

        See :doc:`here <new>` for examples.

        :param frame: A frame to train the model on.
        :type frame: Frame
        :param label_column: Column name containing the label
            for each observation.
        :type label_column: unicode
        :param observation_columns: List of column(s) containing the
            observations.
        :type observation_columns: list
        :param intercept: (default=True)  Flag indicating if the algorithm adds an intercept.
            Default is true.
        :type intercept: bool
        :param num_iterations: (default=100)  Number of iterations for SGD. Default is 100.
        :type num_iterations: int32
        :param step_size: (default=1.0)  Initial step size for SGD optimizer for the first step.
            Default is 1.0.
        :type step_size: float64
        :param reg_type: (default=None)  Regularization "L1" or "L2".
            Default is "L2".
        :type reg_type: unicode
        :param reg_param: (default=0.01)  Regularization parameter. Default is 0.01.
        :type reg_param: float64
        :param mini_batch_fraction: (default=1.0)  Set fraction of data to be used for each SGD iteration. Default is 1.0; corresponding to deterministic/classical gradient descent.
        :type mini_batch_fraction: float64

        :returns: 
        :rtype: _Unit
        """
        return None


@doc_stub
def drop(*items):
    """
    drop() serves as an alias to drop_frames, drop_graphs, and drop_models.

    It accepts multiple parameters, which can contain strings (the name of the frame, graph, or model),
    proxy objects (the frame, graph, or model object itself), or a list of strings and/or proxy objects.
    If the item provided is a string and no frame, graph, or model is found with the specified name,
    no action is taken.

    If the item type is not recognized (not a string, frame, graph, or model) an ArgumentError is raised.

    Examples
    --------

    Given a frame, model, and graph like:

        .. code::

            >>> my_frame = ta.Frame()

            >>> my_model = ta.KMeansModel()
            [===Job Progress===]

            >>> my_graph = ta.Graph()
            -etc-

    The drop() command can be used to delete the frame, model, and graph from the server.  It returns the number
    of items that have been deleted.

        .. code::

            >>> ta.drop(my_frame, my_model, my_graph)
            3

    Alternatively, we can pass the object's string name to drop() like:

    .. code::

            >>> my_frame = ta.Frame(name='example_frame')

            >>> ta.drop('example_frame')
            1



    :param *items: (default=None)  Deletes the specified frames, graphs, and models from the server.
    :type *items: List of strings (frame, graph, or model name) or proxy objects (the frame, graph, or model object itself).

    :returns: Number of items deleted.
    :rtype: int
    """
    return None

@doc_stub
def drop_frames(items):
    """
    Deletes the frame on the server.

    :param items: Either the name of the frame object to delete or the frame object itself
    :type items: [ str | frame object | list [ str | frame objects ]]

    :returns: Number of frames deleted.
    :rtype: list
    """
    return None

@doc_stub
def drop_graphs(items):
    """
    Deletes the graph on the server.

    :param items: Either the name of the graph object to delete or the graph object itself
    :type items: [ str | graph object | list [ str | graph objects ]]

    :returns: Number of graphs deleted.
    :rtype: list
    """
    return None

@doc_stub
def drop_models(items):
    """
    Deletes the model on the server.

    :param items: Either the name of the model object to delete or the model object itself
    :type items: [ str | model object | list [ str | model objects ]]

    :returns: Number of models deleted.
    :rtype: list
    """
    return None

@doc_stub
def get_frame(identifier):
    """
    Get handle to a frame object.

    :param identifier: Name of the frame to get
    :type identifier: str | int

    :returns: frame object
    :rtype: Frame
    """
    return None

@doc_stub
def get_frame_names():
    """
    Retrieve names for all the frame objects on the server.

    :returns: List of names
    :rtype: list
    """
    return None

@doc_stub
def get_graph(identifier):
    """
    Get handle to a graph object.

    :param identifier: Name of the graph to get
    :type identifier: str | int

    :returns: graph object
    :rtype: Graph
    """
    return None

@doc_stub
def get_graph_names():
    """
    Retrieve names for all the graph objects on the server.

    :returns: List of names
    :rtype: list
    """
    return None

@doc_stub
def get_model(identifier):
    """
    Get handle to a model object.

    :param identifier: Name of the model to get
    :type identifier: str | int

    :returns: model object
    :rtype: Model
    """
    return None

@doc_stub
def get_model_names():
    """
    Retrieve names for all the model objects on the server.

    :returns: List of names
    :rtype: list
    """
    return None


del doc_stub