
import olap.xmla.xmla as xmla
import types
from suds import WebFault
import re
from datetime import datetime, timedelta, time
from sws_tags.sws_utils.messages import *
from sws_tags.sws_utils.decorators import max_sim_execs
from django.utils.datastructures import SortedDict
from lxml import etree
from redis import ConnectionError, TimeoutError
import warnings
import traceback


def createAxisYNamesWithColCube(col_cube, complete_name):
        axis_y_aux = []
        for i in col_cube:
            name = i[0]
            if complete_name:
                name += '*' + i[1]
            axis_y_aux.append(name)
        return axis_y_aux


def new_execute(self, command, dimformat="Multidimensional", axisFormat="ClusterFormat", **kwargs):
    """
      **Description:**
            At begin this function  is from xmla library but we have overwrite because the original waste much time.Execute a new mdx against the cube.
      **Args:**
            command : A string which represent the mdx to execute
      **Returns:**
            A xml file with the result to execute the mdx against the cube
      **Modify:**
            Nothing.
      **Raises:**
            Nothing.
      **Import**::
            Nothing.
      Other information ::
    """
    if isinstance(command, types.StringTypes):
        command = {"Statement": command}
    props = {"Format": dimformat, "AxisFormat": axisFormat}
    props.update(kwargs)
    pl = {"PropertyList": props}
    try:
        medio_root = self.client.service.Execute(command, pl)
        return medio_root
    except WebFault, fault:
        swslog('error', 'Failed method from xmla library', WebFault)
        swslog('error', 'Failed method from xmla library', fault)
        raise XMLAException(fault.message, listify(fault.fault))


class CUBE:
    """
            This class is used to connnect with the cube, in that moment the dimensions and measures are calculated
            , and to launch queries against cube.

        **Attributes:**
            #. dimensiones: A dict, the keys are tuples with the name of the dimension first, in second place the attribute of this dimension and in third place 'All' (to explore all values of that attribute) or the attribute again to explore one to one . And the values are the dimension like is needed to create in a mdx .Example: dimensiones={('Client','Client','Client'):'[Client].[Client].[Client]'}
            #. medidas: As the attribute dimension but the keys are different only have two values, the first is 'Measures' for all them , and the second is the measure.Example: medidas={('Measures','Calls'):'[Measures].[Calls]'}
            #. connection: An instance of XMLAProvider after connected with the OLAP services, this attribute is needed to all methods which need the cube parameter.
            #. name: A string , the name of the database where is the cube.
            #. key_cache_dimYmed: A string which has the key to add and get the dimensiones and medidas attributes in memcache.
    """
    dimensiones = {}
    medidas = {}
    connection = ''   # Es del tipo XMLASOURCE
    name = ''
    key_cache_dimYmed = ''
    key_cache_MDXS = ''
    redis = ''
    ip = ''

    def __init__(self, limit_sim_exe=0, limit_time=0):
        self.limit_sim_exe = limit_sim_exe
        self.limit_time = limit_time

    def connect(self, ip, bbdd=[], cubes=[], redis=""):
        """
          **Description:**
                Create connection with OLAP services and get the dimension and medidas from the cubes which are in the databases that we want to connnect.
          **Args:**
                #. ip: A string with the IP of OLAP service.
                #. bbdd: A list of strings with the names of databases where are the cubes which we will use.
                #. bbdd: A list of strings with the names of cubes which we will use.
          **Returns:**
                An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> : it`s the connection with OLAP service
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        self.ip = ip
        location = "http://" + self.ip + "/OLAP/msmdpump.dll"

        def addDimension_Medidas_redis(ide, value):
            try:
                if r.get(ide) is None:
                    return r.set(ide, value)
            except ConnectionError:
                swslog('error', 'Connection error Redis adding dimension and measures', '')
            except TimeoutError:
                swslog('error', 'Timeout error Redis adding dimension and measures', '')
            return False

        def getDimension_Medidas_redis(ide):
            try:
                value = eval(r.get(ide))
            except ConnectionError:
                swslog('error', 'Connection error Redis get dimension and measures', '')
                value = [{}, {}]
            except TimeoutError:
                swslog('error', 'Timeout error Redis get dimension and measures', '')
                value = [{}, {}]
            return value[0], value[1]

        def isAdded_redis(ide):
            try:
                res = not (r.get(ide) is None)
            except ConnectionError:
                swslog('error', 'Connection error Redis adding dimension and measures', '')
                res = False
            except TimeoutError:
                swslog('error', 'Timeout error Redis adding dimension and measures', '')
                res = False
            return res

        self.redis = redis
        r = redis
        p = xmla.XMLAProvider()
        self.connection = p.connect(location=location)
        if type(bbdd) is list:
            bbdd = bbdd[0]
        self.set_name_BBDD_used(bbdd)
        self.key_cache_dimYmed = self.name + '_dimYmed'
        if not isAdded_redis(self.key_cache_dimYmed):
            try:
                self.medidas = self.__getMedidas(bbdd, cubes)
                self.dimensiones = self.__getDimensiones(bbdd, cubes)
                value = []
                value.append(self.medidas)
                value.append(self.dimensiones)
                addDimension_Medidas_redis(self.key_cache_dimYmed, value)
            except Exception, e:
                swslog('error', 'Error setting measures and dimensions in redis', e)
        else:
            self.medidas, self.dimensiones = getDimension_Medidas_redis(self.key_cache_dimYmed)
        return self.connection

    def getNamesBBDD(self):
        """
          **Description:**
                Get the names of the databases which are in the ip where we have connected.
          **Args:**
                Nothing.
          **Returns:**
                A lis of strings whit the names of the databases.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        row = []
        try:
            catalogs = self.connection.getCatalogs()
        except Exception:
            redis.delete(self.key_cache_dimYmed)
            swslog('repeat the connect() whith a good location')
        for i in catalogs:
            row.append(i.getUniqueName())
        return row

    def __getDimensiones(self, bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS'], cubes='NO_CUBE_NAMES_IN_SETTINGS'):

        dimensiones = {}
        catalogs = self.connection.getCatalogs()
        for catalogo in catalogs:
            if catalogo.getUniqueName() == bbdd:
                for Cube in catalogo.getCubes():
                        if Cube.getUniqueName() in cubes:
                            for dim in Cube.getDimensions():
                                for jerar in dim.getHierarchies():
                                    for level in jerar.getLevels():
                                        name = level.getUniqueName()
                                        first_name = name[name.find('[') + 1:name.find(']')]
                                        name_aux = name[name.find(']') + 1:]
                                        second_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                                        name_aux = name_aux[name_aux.find(']') + 1:]
                                        third_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                                        third_name = third_name.replace('(', '').replace(')', '')
                                        dimensiones[(first_name, second_name, third_name)] = level.getUniqueName()
        return dimensiones

    def name_dimension(self, axis, complete_name):
        """
          **Description:**
                This method changes the name of dimension from the cubes understand to more readable.
          **Args:**
                #. axis: A list of string which represents a set of dimensions of the cube.
                #. complete_name: A boolean , if it is false return only the name of the dimension , in othre case return the name of the dimension and the attribute , separated by a comma.
          **Returns:**
                A lis of strings whit the names of the dimensions more readable to the human.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        dimensiones = self.dimensiones
        if dimensiones:
            nombres = []
            for dimension in axis:
                for dim in dimensiones:
                    if dimensiones[dim] == dimension:
                        if not complete_name:
                            dim = str(dim[0])
                            nombres.append(dim)
                        else:
                            dim = str(dim[0]) + '*' + str(dim[1])
                            nombres.append(dim)
            return nombres
        else:
            self.redis.delete(self.key_cache_dimYmed)
            return 'cube has not dimensions or it is not good connect'

    def __getMedidas(self, bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS'], cubes=['Cdrt']):

        medidas = {}
        catalogs = self.connection.getCatalogs()
        for catalogo in catalogs:
            if catalogo.getUniqueName() == bbdd:
                for Cube in catalogo.getCubes():
                        if Cube.getUniqueName() in cubes:
                            for medida in Cube.getMeasures():
                                name = medida.getUniqueName()
                                first_name = name[name.find('[') + 1:name.find(']')]
                                name_aux = name[name.find(']') + 1:]
                                second_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                                name_aux = name_aux[name_aux.find(']') + 1:]
                                medidas[(first_name, second_name)] = name
        return medidas

    def get_name_BBDD_used(self):
        """
          **Description:**
                This method return the name which we have the cube.
          **Args:**
                Nothing.
          **Returns:**
                A string that is the name of the database which is using.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        return self.name

    def set_name_BBDD_used(self, name):

        """
          **Description:**
                This method set the name which we have the cube.
          **Args:**
                Nothing.
          **Returns:**
                Nothing.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        self.name = name

    def _get_decorator_params(self):
        return self.name + '_MAX_SIM_EXECS_' + self.ip, self.limit_sim_exe, self.redis, self.limit_time

    @max_sim_execs()
    def launch_query(self, mdx=None):
        """
          **Description:**
                This method launch a query against the cube and return the result in xml format.
          **Args:**
                mdx: A string which represents the mdx to launch against the cube
          **Returns:**
                A xml object which has the result to make the query
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        connexion = self.connection
        connexion.client.set_options(retxml=True)
        connexion.new = new_execute
        result = connexion.new(connexion, mdx, Catalog=self.name)
        connexion.client.set_options(retxml=False)
        return result


class XmlResult:
    """
            This class is used to get the values from the xml which got from launch a mdx against the cube.

        **Attributes:**
            Nothing.
    """
    def returnEmpty(self, error):
        axis_x_names = ''
        axis_y_names = ''
        axis_x_values = []
        axis_y_values = []
        numero_filas = 0
        numero_dimensiones = 0
        numero_celdas = 0
        numero_medidas = 0
        return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)

    def getValues(self, xml1, format_cube=False):
        """
          **Description:**
                This method is to get the values from xml which is the result from launch a mdx against the cube.
          **Args:**
                xml1: A xml which represents the result to launch a mdx against the cube
          **Returns:**
                #. A tuple with 8 elements:
                        #. axis_x_names: A list of strings which have the names of the measures used.
                        #. axis_y_names: A list of strings which have the names of the dimensions used.
                        #. axis_x_values: A list of strings which have the values of the measures used.
                        #. axis_y_values: A list of strings which have the names of the dimensions used.
                        #. numero_filas: An integer which represents the number of rows returns from the cube.
                        #. numero_dimensiones:  An integer which represents the number of dimensions used.
                        #. numero_celdas: A integer which represents the numbers of values returns of all measures.
                        #. numero_medidas: An integer which represents the number of measures used.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        ### Name space
        NS = '{urn:schemas-microsoft-com:xml-analysis:mddataset}'
        if xml1.find('faultcode') > 0 or xml1.find('ErrorCode') > 0:
            if xml1.find('faultcode') > 0:
                error = xml1[xml1.find('<faultstring>')+13:xml1.find('</faultstring>')]
            else:
                error = xml1[xml1.find('Error')+5:]
            return self.returnEmpty(error)
        else:
            try:
                xml = etree.fromstring(xml1)
                axes = xml.findall('.//{0}Axes'.format(NS))[0]
            except Exception, e:
                swslog('error', xml1, '', gettraceback=False)
                return self.returnEmpty(False)
            if len(axes.getchildren()) > 1:
                axis_y = axes.getchildren()[1]
                numero_filas = len(axis_y.getchildren()[0].getchildren())
                if numero_filas == 0:
                    return self.returnEmpty(False)
                numero_dimensiones = len(axis_y.getchildren()[0].getchildren()[0].getchildren())
                axis_y_names = [axis_y.findall('.//{0}Member'.format(NS))[i].findall('.//{0}LName'.format(NS))[0].text for i in range(0, numero_dimensiones)]
                axis_y_values = [i.text for i in axis_y.findall('.//{0}Caption'.format(NS))]
                axis_x = axes.getchildren()[0]
                axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]
                numero_medidas = len(axis_x_names)
                error = False
                celdas = xml.findall('.//{0}CellData'.format(NS))[0].getchildren()
                if len(celdas) > 0:
                    axis_x_values = self.getAxisXValues(celdas, NS, format_cube)
                else:
                    axis_x_values = []
                numero_celdas = len(axis_x_values)
                return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)
            else:
                numero_filas = 1
                numero_dimensiones = 0
                axis_y_names = []
                axis_y_values = []
                axis_x = axes.getchildren()[0]
                axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]
                numero_medidas = len(axis_x_names)
                error = False
                celdas = xml.findall('.//{0}CellData'.format(NS))[0].getchildren()
                if len(celdas) > 0:
                    axis_x_values = self.getAxisXValues(celdas, NS, format_cube)
                else:
                    axis_x_values = []
                numero_celdas = len(axis_x_values)
                return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)

    def getAxisXValues(self, celdas, NS, format_cube):
        if format_cube:
            find = './/{0}FmtValue'
        else:
            find = './/{0}Value'
        axis_x_values_dict = {}
        for celda in celdas:
            key = int(celda.values()[0])
            value = celda.findall(find.format(NS))[0].text.encode('ascii', 'ignore')
            if celda.findall(find.format(NS))[0].values() and find == './/{0}Value':
                cast_type = celda.findall(find.format(NS))[0].values()[0].replace('xsd:', '')
                cast = self.dameCast(cast_type)
                axis_x_values_dict[key] = cast(value)
            else:
                axis_x_values_dict[key] = value
        axis_x_values_final = []
        for i in range(0, int(celdas[len(celdas) - 1].values()[0]) + 1):
            try:
                axis_x_values_final.append(axis_x_values_dict[i])
            except:
                axis_x_values_final.append('----')
        return axis_x_values_final

    def dameCast(self, cast_type):
        if cast_type == 'double':
            return float
        else:
            return int


class Salida_Highcharts:
    """
            This class is used to get  a string format in json for a HighChart.

        **Attributes:**
            Nothing.
    """
    def __init__(self):
        warnings.warn("{0} is a deprecated class, use Format".format(self.__class__.__name__), category=DeprecationWarning)

    def replaceSimbols(self, value, format_cube):
        if format_cube:
            return value
        value = value.replace('%', '')
        value = value.replace('$', '')
        value = value.replace('', '')
        return float(value)

    def getValuesToDict(self, axis_y_values, axis_x_values, axis_x_names, format_cube, numero_dimensiones, numero_medidas):
        dictValues = {}

        if numero_dimensiones == 3:
            for num in range(0, len(axis_y_values) / 3):
                if axis_y_values[3 * num] in dictValues:
                    if axis_y_values[(3*num)+1] in dictValues[axis_y_values[3*num]]:
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                        for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                    else:
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]] = {}
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                        for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                else:
                    dictValues[axis_y_values[3*num]] = {}
                    dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]] = {}
                    dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
        if numero_dimensiones == 2:
            for num in range(0, len(axis_y_values) / 2):
                if axis_y_values[2*num] in dictValues:
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                else:
                    dictValues[axis_y_values[2*num]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
        return dictValues

    def result_to_json(self, cube, result, types={}, xAxis=['Time', 'Date'], dimension_v_name='client', exclude=[], complete_name=False, format_cube=False):
        """
          **Description:**
                This method is to convert the values get from xml to a dict for a highchart.
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. types: A list with types to draw each dimension in the highchart -->  types=['spline','column']
                #. xAxis: A list with the names of the dimension which will appear en the x axis.
                #. dimension_v_name: A string with the value of the dimension which appear in the y axis.
                #. exclude: A dict with the names o f values to exclude and theirs values.
                #. complete_name: A boolean which indicate if the names of the dimension will be the dimension and the attribute (true) or only the dimension.

          **Returns:**
                A dict with the elements need to form a HighChart.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        xml_class = XmlResult()
        types2 = {}
        for i in types:
            types2[i.upper()] = types[i]
        types = types2
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        if not error:
            dictValues = self.getValuesToDict(axis_y_values, axis_x_values, axis_x_names, format_cube, numero_dimensiones, numero_medidas)
            sort_keys = sorted(dictValues.keys())
            v_data = []
            v_name = []
            v_type = []
            v_xAxis = {}
            cont = 0
            v_yAxis_primer = []
            for i in range(0, len(axis_x_names)):
                v_yAxis_primer.append(cont)
                cont += 1

            for key in sort_keys:
                for num_medida in range(0, numero_medidas):
                    v_name.append(key + ' ' + axis_x_names[num_medida].upper())

                for days in dictValues[key].keys():
                    for hours in dictValues[key][days]:
                        key_xAxis = days[0:4] + '-' + days[4:6] + '-' + days[6:8] + ' ' + hours
                        v_xAxis[key_xAxis] = ''

            v_yAxis = []
            for i in range(0, len(v_name)):
                v_yAxis.append(v_yAxis_primer[i % len(v_yAxis_primer)])

            v_xAxis = sorted(v_xAxis.keys())
            for num in range(0, len(v_name)):
                for num_medida in range(0, numero_medidas):
                    if axis_x_names[num_medida].upper() in v_name[num][-len(axis_x_names[num_medida]):]:
                        v_type.append(types[axis_x_names[num_medida].upper()])

            for key in sort_keys:
                data_dict = {}
                for num_medida in range(0, numero_medidas):
                    data_dict[num_medida] = []
                for dia in v_xAxis:
                    day = datetime.strftime(datetime.strptime(dia, '%Y-%m-%d %H:%M'), '%Y%m%d')
                    hour = datetime.strftime(datetime.strptime(dia, '%Y-%m-%d %H:%M'), '%H:%M')
                    for num_medida in range(0, numero_medidas):
                        try:
                            data_dict[num_medida].append(dictValues[key][day][hour][axis_x_names[num_medida]])
                        except:
                            data_dict[num_medida].append(0)

                for num_medida in range(0, numero_medidas):
                    v_data.append(data_dict[num_medida])

            if numero_dimensiones == 2:
                v_xAxis = [k[0:-6] for k in v_xAxis]
            dict_higcharts = {}
            dict_higcharts['v_data'] = v_data  # lista de listas con los valores para cada eje y
            dict_higcharts['v_name'] = v_name  # lista de nombres para cada eje y
            dict_higcharts['v_type'] = v_type  # lista de tipos para cada eje y
            dict_higcharts['v_yAxis'] = v_yAxis  # lista con numeros que indican preferencia de cada eje y
            dict_higcharts['v_xAxis'] = v_xAxis  # lista con valores de eje x fechas normalmente
            if error:
                dict_higcharts['error'] = error

            return dict_higcharts

        else:
            dict_higcharts = {}
            dict_higcharts['v_data'] = []
            dict_higcharts['v_name'] = []
            dict_higcharts['v_type'] = []
            dict_higcharts['v_yAxis'] = []
            dict_higcharts['v_xAxis'] = []
            if error:
                dict_higcharts['error'] = error
            return dict_higcharts


class Salida_Dict:

    def __init__(self):
        warnings.warn("{0} is a deprecated class, use Format".format(self.__class__.__name__), category=DeprecationWarning)

    def result_to_dict(self, cube, result, database_cube_dict=[], isfilter=False, rowNum=500, page=0, total=False, complete_name=False, format_cube=False):

        """
          **Description:**
                This method correspond with all views whre there are grids which use data from the cube. This function convert the values get from xml (result to launch a mdx ) to a string in json format for a grid.
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. database_cube_dict : A dict with the names of dimension return from the cube like keys and the values with the names that we ant that appear in json string.
                #. isfilter : A boolean which indicate if the result ton convert in json is for a filter or not.
                #. rowNum : A integer which indicate the number of rows that we want in the json.
                #. page : A integer which indicate the number of page that we want in the json. If the rowNum is 200 and the page is 2 ,we will get from 200 row to 400 row. If the page is 0 we will get all the rows.
                #. total : A boolean. If it is true, the json will contain the total of all measures.
                #. complete_name: A boolean which indicate how we want the name of the dimension, if it is true the name will be : name of the dimension * attribute , in other case only the name of the dimension.
          **Returns:**
                A string in json format.
          **Modify:**
                Non modify anything.
          **Raises:**
                IndexError: The errors and warnning of the views are storage in the archive ...
          **Import**::
                Nothing.
          Other information ::


        """
        xml_class = XmlResult()
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)

        if numero_celdas == 0:
            axis_x_names = ''
            axis_y_names = ''
            axis_x_values = []
            axis_y_values = []
            numero_filas = 0
            numero_dimensiones = 0
            numero_celdas = 0
            numero_medidas = 0

        i = 0
        for name in axis_x_names:
            if name == 'ACD':
                index_name = i
            i = i+1

        axis_y_names = cube.name_dimension(axis_y_names, complete_name)

        if isfilter:
            list_dict = []
            # list_dict.append({'text': '----', 'id': 'NULL'})
            if numero_dimensiones == 2:
                for i in range(0, len(axis_y_values) / 2):
                    list_dict.append({'id': str(axis_y_values[(i*2)+1]), 'text': axis_y_values[i * 2]})
                return list_dict
            else:
                for i in range(0, len(axis_y_values)):
                    list_dict.append({'id': str(axis_y_values[(i)]), 'text': axis_y_values[i]})
                return list_dict
        else:
            data = {}
            rows = []
            if page == 0:
                data['total'] = numero_filas
            else:
                numero_filas = numero_filas + 0.0
                total = numero_filas / rowNum
                if total.is_integer():
                    data['total'] = total
                else:
                    if int(str(total)[str(total).find('.') + 1]) > 5:
                        data['total'] = int(str(total)[str(total).find('.') - 1]) + 1
                    else:
                        data['total'] = int(str(total)[str(total).find('.') - 1])
            numero_filas = int(numero_filas)
            data['records'] = numero_filas
            if page == 0:
                index1 = 0
                index2 = numero_filas
            else:
                page = int(page)
                index1 = int((page-1) * rowNum)
                index2 = int(page * rowNum)
                if numero_filas < index2:
                    index2 = numero_filas
            if total:
                totales = {}
                for i in axis_x_names:
                    totales[i] = 0
            cont_ACD_NAN = 0
            for fila in range(0, numero_filas):
                row = SortedDict()
                for i in axis_y_names:
                    row[i] = ''
                for i in axis_x_names:
                    row[i] = ''
                for measure in range(0, numero_medidas):
                    if fila < index2 and fila >= index1:
                        if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                            if format_cube:
                                row[axis_x_names[measure]] = str(axis_x_values[(fila*numero_medidas)+measure])
                            else:
                                row[axis_x_names[measure]] = str(round(float(axis_x_values[(fila*numero_medidas)+measure]), 4))
                        else:
                            row[axis_x_names[measure]] = '0'
                    if total:
                            if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                                if not format_cube:
                                    totales[axis_x_names[measure]] += round(float(axis_x_values[(fila * numero_medidas) + measure]), 4)
                            else:
                                if measure == index_name:  # index for measure ASR
                                    cont_ACD_NAN = cont_ACD_NAN + 1
                if fila < index2 and fila >= index1:
                    for dimension in range(0, numero_dimensiones):
                        if database_cube_dict:
                            for key, value in database_cube_dict.items():
                                if axis_y_names[dimension] == key:
                                    axis_y_names[dimension] = value
                        #### TODO_MAS EL KEY DE DATABASA_CUBE DICT VIENE CON UNA COMA AL PRINCIPIO
                        axis_y_names[dimension] = axis_y_names[dimension].lstrip("'")
                        if isinstance(axis_y_values[(fila * numero_dimensiones) + dimension], unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila * numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila * numero_dimensiones) + dimension])
                    rows.append(row)
            if total:
                if not format_cube:
                    total_cost = 0
                    total_income = 0
                    json_data_new = {}
                    for k, v in totales.items():
                        sign = 1
                        if float(v) < 0:
                            sign = -1
                        v = str(v)
                        p = re.compile('\d+')
                        c = p.findall(v)
                        if len(c) > 1:
                            v = str(c[0]) + '.' + str(c[1])[0:2]
                            v = str(float(v) * sign)
                        if (k.find('Avg') > 0) or (k == 'ASR') or (k == 'ACD'):
                            try:
                                if (k != 'ACD'):
                                    v = str(float(v) / len(rows))
                                else:
                                    div = len(rows) - cont_ACD_NAN
                                    v = str(float(v) / div)
                                v = v[0:6]
                            except Exception, e:
                                swslog('error', 'result_to_dict method : div for 0', e)
                        if k == 'Total Income':
                            total_income = v
                        if k == 'Total Cost':
                            total_cost = v
                        json_data_new[k] = v
                        total_cost = float(total_cost)
                        if total_cost != 0:  # sino dejo el sumatorio
                            benefic = float(total_income) - float(total_cost)
                            json_data_new['Margin'] = float(benefic) / float(total_cost) * 100
                        data['footerData'] = json_data_new
            data['rows'] = rows
            data['page'] = page
            if error:
                data['error'] = error
            obj = data
            return obj


class Salida_Grid:
    """
            This class is used to get the filter and a string format in json for a grid

        **Attributes:**
            Nothing.

    """
    def __init__(self):
        warnings.warn("{0} is a deprecated class, use Format".format(self.__class__.__name__), category=DeprecationWarning)

    def result_to_json(self, cube, result, database_cube_dict=[], isfilter=False, rowNum=500, page=0, total=False, complete_name=False, format_cube=False, col_cube=[]):

        """
          **Description:**
                This method correspond with all views whre there are grids which use data from the cube. This function convert the values get from xml (result to launch a mdx ) to a string in json format for a grid.
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. database_cube_dict : A dict with the names of dimension return from the cube like keys and the values with the names that we ant that appear in json string.
                #. isfilter : A boolean which indicate if the result ton convert in json is for a filter or not.
                #. rowNum : A integer which indicate the number of rows that we want in the json.
                #. page : A integer which indicate the number of page that we want in the json. If the rowNum is 200 and the page is 2 ,we will get from 200 row to 400 row. If the page is 0 we will get all the rows.
                #. total : A boolean. If it is true, the json will contain the total of all measures.
                #. complete_name: A boolean which indicate how we want the name of the dimension, if it is true the name will be : name of the dimension * attribute , in other case only the name of the dimension.
          **Returns:**
                A string in json format.
          **Modify:**
                Non modify anything.
          **Raises:**
                IndexError: The errors and warnning of the views are storage in the archive ...
          **Import**::
                Nothing.
          Other information ::


        """
        xml_class = XmlResult()

        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        if numero_celdas == 0:
            axis_x_names = ''
            axis_y_names = ''
            axis_x_values = []
            axis_y_values = []
            numero_filas = 0
            numero_dimensiones = 0
            numero_celdas = 0
            numero_medidas = 0
        i = 0
        for name in axis_x_names:
            if name == 'ACD':
                index_name = i
            i = i + 1
        axis_y_names = cube.name_dimension(axis_y_names, complete_name)
        if col_cube:
            axis_y_names = createAxisYNamesWithColCube(col_cube, complete_name)
        if isfilter:
            list_dict = []
            # list_dict.append({'text': '----', 'id': 'NULL'})
            if numero_dimensiones == 2:
                for i in range(0, len(axis_y_values) / 2):
                    list_dict.append({'id': str(axis_y_values[(i * 2) + 1]), 'text': axis_y_values[i * 2]})
                return list_dict
            else:
                for i in range(0, len(axis_y_values)):
                    list_dict.append({'id': str(axis_y_values[(i)]), 'text': axis_y_values[i]})
                return list_dict
        else:
            data = {}
            rows = []
            if page == 0:
                data['total'] = numero_filas
            else:
                numero_filas = numero_filas + 0.0
                total = numero_filas / rowNum
                if total.is_integer():
                    data['total'] = total
                else:
                    if int(str(total)[str(total).find('.') + 1]) > 5:
                        data['total'] = int(str(total)[str(total).find('.') - 1]) + 1
                    else:
                        data['total'] = int(str(total)[str(total).find('.') - 1])
            numero_filas = int(numero_filas)
            data['records'] = numero_filas
            if page == 0:
                index1 = 0
                index2 = numero_filas
            else:
                page = int(page)
                index1 = int((page-1) * rowNum)
                index2 = int(page*rowNum)
                if numero_filas < index2:
                    index2 = numero_filas
            if total:
                totales = {}
                for i in axis_x_names:
                    totales[i] = 0
            cont_ACD_NAN = 0
            for fila in range(0, numero_filas):
                row = SortedDict()
                for measure in range(0, numero_medidas):
                    if fila < index2 and fila >= index1:
                        if not axis_x_names[measure] in row:
                            row[axis_x_names[measure]] = ''
                        try:
                            if axis_x_values[(fila*numero_medidas) + measure] != 'NaN':
                                if format_cube:
                                    row[axis_x_names[measure]] = str(axis_x_values[(fila*numero_medidas)+measure])
                                else:
                                    row[axis_x_names[measure]] = str(round(float(axis_x_values[(fila * numero_medidas) + measure]), 4))
                            else:
                                row[axis_x_names[measure]] = '0'
                        except:
                            row[axis_x_names[measure]] = '0'

                    if total:
                        try:
                            if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                                if not format_cube:
                                    totales[axis_x_names[measure]] += round(float(axis_x_values[(fila * numero_medidas) + measure]), 4)
                            else:
                                if measure == index_name:  # index for measure ASR
                                    cont_ACD_NAN = cont_ACD_NAN + 1
                        except:
                            row[axis_x_names[measure]] = '0'

                if fila < index2 and fila >= index1:

                    for dimension in range(0, numero_dimensiones):
                        if not axis_y_names[dimension] in row:
                            row[axis_y_names[dimension]] = ''
                        if database_cube_dict:
                            for key, value in database_cube_dict.items():
                                if axis_y_names[dimension] == key:
                                    axis_y_names[dimension] = value

                        #### TODO_MAS EL KEY DE DATABASA_CUBE DICT VIENE CON UNA COMA AL PRINCIPIO
                        axis_y_names[dimension] = axis_y_names[dimension].lstrip("'")
                        if isinstance(axis_y_values[(fila * numero_dimensiones) + dimension], unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)

            if total:
                if not format_cube:
                    total_cost = 0
                    total_income = 0
                    json_data_new = {}
                    for k, v in totales.items():
                        sign = 1
                        if float(v) < 0:
                            sign = -1
                        v = str(v)
                        p = re.compile('\d+')
                        c = p.findall(v)
                        if len(c) > 1:
                            v = str(c[0]) + '.' + str(c[1])[0:2]
                            v = str(float(v) * sign)
                        if (k.find('Avg') > 0) or (k == 'ASR') or (k == 'ACD'):
                            try:
                                if (k != 'ACD'):
                                    v = str(float(v) / len(rows))
                                else:
                                    div = len(rows) - cont_ACD_NAN
                                    v = str(float(v) / div)
                                v = v[0:6]
                            except Exception, e:
                                swslog('error', 'result_to_json : div for 0', e)
                        if k == 'Total Income':
                            total_income = v
                        if k == 'Total Cost':
                            total_cost = v
                        json_data_new[k] = v
                        total_cost = float(total_cost)
                        if total_cost != 0:  # sino dejo el sumatorio
                            benefic = float(total_income) - float(total_cost)
                            json_data_new['Margin'] = float(benefic) / float(total_cost) * 100
                        data['footerData'] = json_data_new
            data['rows'] = rows
            data['page'] = page
            if error:
                data['error'] = error
            obj = json.dumps(data)
            return obj

    def filters(self, query, cube, database_cube_dict, dimensiones=[], exclude_rows=[], dimension_extra='Id'):

        """
          **Description:**
                This function is used to get all the filters acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. dimensiones: A list of dimensions which calculate the mdx to get the filters if it is not used the filters will be calculated according to all dimensions.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        row = ''
        for dim in dimensiones:
                row = self.filter(query, cube, dim, database_cube_dict, exclude_rows, dimension_extra)
        return row

    def filter(self, query, cube, dimension, database_cube_dict=[], exclude_rows=[], dimension_extra='Id'):
        """
          **Description:**
                This function is used to get one filter acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. dimensiones: A string with the dimension which calculate the mdx to get the filter.
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        mdx_class = MDX()
        query_without_select, measure = mdx_class.without_select(query)
        json = ''
        on_rows = []
        on_rows.append(dimension)
        if dimension_extra != 'None':
            dimension_id = (dimension[0], dimension_extra, dimension_extra)
            on_rows.append(dimension_id)
        select = mdx_class.select_for_filter(cube, on_rows=on_rows, medida=measure, exclude_rows=exclude_rows)
        query = select + query_without_select
        res = cube.launch_query(mdx=query.upper())
        json = self.result_to_json(cube, res, database_cube_dict, isfilter=True)
        return json


class Format:
    """
            This class is used to get differents format to filters, highcharts ...

        **Attributes:**
            Nothing.

    """

    def replaceSimbols(self, value, format_cube):
        if value == '----':
            value = '0'
        if format_cube:
            return value
        value = str(value).replace('%', '')
        value = str(value).replace('$', '')
        value = str(value).replace('', '')
        return float(value)

    def getValuesToDict(self, axis_y_values, axis_x_values, axis_x_names, format_cube, numero_dimensiones, numero_medidas):
        dictValues = {}

        if numero_dimensiones == 3:
            for num in range(0, len(axis_y_values) / 3):
                if axis_y_values[3 * num] in dictValues:
                    if axis_y_values[(3*num)+1] in dictValues[axis_y_values[3*num]]:
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                        for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                    else:
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]] = {}
                        dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                        for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                else:
                    dictValues[axis_y_values[3*num]] = {}
                    dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]] = {}
                    dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[3*num]][axis_y_values[(3*num)+1]][axis_y_values[(3*num)+2]][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
        if numero_dimensiones == 2:
            for num in range(0, len(axis_y_values) / 2):
                if axis_y_values[2*num] in dictValues:
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
                else:
                    dictValues[axis_y_values[2*num]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]] = {}
                    dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'] = {}
                    for num_medida in range(0, numero_medidas):
                            dictValues[axis_y_values[2*num]][axis_y_values[(2*num)+1]]['00:00'][axis_x_names[num_medida]] = self.replaceSimbols(axis_x_values[(numero_medidas * num) + num_medida], format_cube)
        return dictValues

    def highchart(self, cube, result, types={}, xAxis=['Time', 'Date'], dimension_v_name='client', exclude=[], complete_name=False, format_cube=False):
        """
          **Description:**
                This method is to convert the values get from xml to a dict for a highchart.
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. types: A list with types to draw each dimension in the highchart -->  types=['spline','column']
                #. xAxis: A list with the names of the dimension which will appear en the x axis.
                #. dimension_v_name: A string with the value of the dimension which appear in the y axis.
                #. exclude: A dict with the names o f values to exclude and theirs values.
                #. complete_name: A boolean which indicate if the names of the dimension will be the dimension and the attribute (true) or only the dimension.

          **Returns:**
                A dict with the elements need to form a HighChart.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        xml_class = XmlResult()
        types2 = {}
        for i in types:
            types2[i.upper()] = types[i]
        types = types2
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        if not error:
            dictValues = self.getValuesToDict(axis_y_values, axis_x_values, axis_x_names, format_cube, numero_dimensiones, numero_medidas)
            sort_keys = sorted(dictValues.keys())
            v_data = []
            v_name = []
            v_type = []
            v_xAxis = {}
            cont = 0
            v_yAxis_primer = []
            for i in range(0, len(axis_x_names)):
                v_yAxis_primer.append(cont)
                cont += 1

            for key in sort_keys:
                for num_medida in range(0, numero_medidas):
                    v_name.append(key + ' ' + axis_x_names[num_medida].upper())

                for days in dictValues[key].keys():
                    for hours in dictValues[key][days]:
                        key_xAxis = days[0:4] + '-' + days[4:6] + '-' + days[6:8] + ' ' + hours
                        v_xAxis[key_xAxis] = ''

            v_yAxis = []
            for i in range(0, len(v_name)):
                v_yAxis.append(v_yAxis_primer[i % len(v_yAxis_primer)])

            v_xAxis = sorted(v_xAxis.keys())
            for num in range(0, len(v_name)):
                for num_medida in range(0, numero_medidas):
                    if axis_x_names[num_medida].upper() in v_name[num][-len(axis_x_names[num_medida]):]:
                        v_type.append(types[axis_x_names[num_medida].upper()])

            for key in sort_keys:
                data_dict = {}
                for num_medida in range(0, numero_medidas):
                    data_dict[num_medida] = []
                for dia in v_xAxis:
                    day = datetime.strftime(datetime.strptime(dia, '%Y-%m-%d %H:%M'), '%Y%m%d')
                    hour = datetime.strftime(datetime.strptime(dia, '%Y-%m-%d %H:%M'), '%H:%M')
                    for num_medida in range(0, numero_medidas):
                        try:
                            data_dict[num_medida].append(dictValues[key][day][hour][axis_x_names[num_medida]])
                        except:
                            data_dict[num_medida].append(0)

                for num_medida in range(0, numero_medidas):
                    v_data.append(data_dict[num_medida])

            if numero_dimensiones == 2:
                v_xAxis = [k[0:-6] for k in v_xAxis]
            dict_higcharts = {}
            dict_higcharts['v_data'] = v_data  # lista de listas con los valores para cada eje y
            dict_higcharts['v_name'] = v_name  # lista de nombres para cada eje y
            dict_higcharts['v_type'] = v_type  # lista de tipos para cada eje y
            dict_higcharts['v_yAxis'] = v_yAxis  # lista con numeros que indican preferencia de cada eje y
            dict_higcharts['v_xAxis'] = v_xAxis  # lista con valores de eje x fechas normalmente
            if error:
                dict_higcharts['error'] = error

            return dict_higcharts

        else:
            dict_higcharts = {}
            dict_higcharts['v_data'] = []
            dict_higcharts['v_name'] = []
            dict_higcharts['v_type'] = []
            dict_higcharts['v_yAxis'] = []
            dict_higcharts['v_xAxis'] = []
            if error:
                dict_higcharts['error'] = error
            return dict_higcharts

    def grid(self, cube, result, database_cube_dict=[], isfilter=False, rowNum=500, page=0, total=False, complete_name=False, format_cube=False, col_cube=[]):

        """
          **Description:**
                This method correspond with all views whre there are grids which use data from the cube. This function convert the values get from xml (result to launch a mdx ) to a string in json format for a grid.
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. database_cube_dict : A dict with the names of dimension return from the cube like keys and the values with the names that we ant that appear in json string.
                #. isfilter : A boolean which indicate if the result ton convert in json is for a filter or not.
                #. rowNum : A integer which indicate the number of rows that we want in the json.
                #. page : A integer which indicate the number of page that we want in the json. If the rowNum is 200 and the page is 2 ,we will get from 200 row to 400 row. If the page is 0 we will get all the rows.
                #. total : A boolean. If it is true, the json will contain the total of all measures.
                #. complete_name: A boolean which indicate how we want the name of the dimension, if it is true the name will be : name of the dimension * attribute , in other case only the name of the dimension.
          **Returns:**
                A string in json format.
          **Modify:**
                Non modify anything.
          **Raises:**
                IndexError: The errors and warnning of the views are storage in the archive ...
          **Import**::
                Nothing.
          Other information ::


        """
        xml_class = XmlResult()
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        if numero_celdas == 0:
            axis_x_names = ''
            axis_y_names = ''
            axis_x_values = []
            axis_y_values = []
            numero_filas = 0
            numero_dimensiones = 0
            numero_celdas = 0
            numero_medidas = 0
        i = 0
        for name in axis_x_names:
            if name == 'ACD':
                index_name = i
            i = i + 1
        axis_y_names = cube.name_dimension(axis_y_names, complete_name)
        if col_cube:
            axis_y_names = createAxisYNamesWithColCube(col_cube, complete_name)
        if isfilter:
            list_dict = []
            # list_dict.append({'text': '----', 'id': 'NULL'})
            if numero_dimensiones == 2:
                for i in range(0, len(axis_y_values) / 2):
                    list_dict.append({'id': str(axis_y_values[(i * 2) + 1]), 'text': axis_y_values[i * 2]})
                return list_dict
            else:
                for i in range(0, len(axis_y_values)):
                    list_dict.append({'id': str(axis_y_values[(i)]), 'text': axis_y_values[i]})
                return list_dict
        else:
            data = {}
            rows = []
            if page == 0:
                data['total'] = numero_filas
            else:
                numero_filas = numero_filas + 0.0
                total = numero_filas / rowNum
                if total.is_integer():
                    data['total'] = total
                else:
                    if int(str(total)[str(total).find('.') + 1]) > 5:
                        data['total'] = int(str(total)[str(total).find('.') - 1]) + 1
                    else:
                        data['total'] = int(str(total)[str(total).find('.') - 1])
            numero_filas = int(numero_filas)
            data['records'] = numero_filas
            if page == 0:
                index1 = 0
                index2 = numero_filas
            else:
                page = int(page)
                index1 = int((page-1) * rowNum)
                index2 = int(page * rowNum)
                if numero_filas < index2:
                    index2 = numero_filas
            if total:
                totales = {}
                for i in axis_x_names:
                    totales[i] = 0
            cont_ACD_NAN = 0
            for fila in range(0, numero_filas):
                row = SortedDict()
                for i in axis_y_names:
                    row[i] = ''
                for i in axis_x_names:
                    row[i] = ''
                for measure in range(0, numero_medidas):
                    if fila < index2 and fila >= index1:
                        try:
                            if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                                if format_cube:
                                    row[axis_x_names[measure]] = str(axis_x_values[(fila*numero_medidas)+measure])
                                else:
                                    row[axis_x_names[measure]] = axis_x_values[(fila*numero_medidas)+measure]
                            else:
                                row[axis_x_names[measure]] = '0'
                        except:
                            row[axis_x_names[measure]] = '0'
                    if total:
                        try:
                            if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                                if not format_cube:
                                    totales[axis_x_names[measure]] += round(float(axis_x_values[(fila*numero_medidas)+measure]), 4)
                            else:
                                if measure == index_name:  # index for measure ASR
                                    cont_ACD_NAN = cont_ACD_NAN + 1
                        except:
                            row[axis_x_names[measure]] = '0'
                if fila < index2 and fila >= index1:
                    for dimension in range(0, numero_dimensiones):
                        if database_cube_dict:
                            for key, value in database_cube_dict.items():
                                if axis_y_names[dimension] == key:
                                    axis_y_names[dimension] = value
                        #### TODO_MAS EL KEY DE DATABASA_CUBE DICT VIENE CON UNA COMA AL PRINCIPIO
                        axis_y_names[dimension] = axis_y_names[dimension].lstrip("'")
                        if isinstance(axis_y_values[(fila*numero_dimensiones)+dimension], unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)
            if total:
                if not format_cube:
                    total_cost = 0
                    total_income = 0
                    json_data_new = {}
                    for k, v in totales.items():
                        sign = 1
                        if float(v) < 0:
                            sign = -1
                        v = str(v)
                        p = re.compile('\d+')
                        c = p.findall(v)
                        if len(c) > 1:
                            v = str(c[0]) + '.' + str(c[1])[0:2]
                            v = str(float(v) * sign)
                        if (k.find('Avg') > 0) or (k == 'ASR') or (k == 'ACD'):
                            try:
                                if (k != 'ACD'):
                                    v = str(float(v) / len(rows))
                                else:
                                    div = len(rows) - cont_ACD_NAN
                                    v = str(float(v) / div)
                                v = v[0:6]
                            except Exception, e:
                                swslog('error', 'formatting to grid : div for 0', e)
                        if k == 'Total Income':
                            total_income = v
                        if k == 'Total Cost':
                            total_cost = v
                        json_data_new[k] = v
                        total_cost = float(total_cost)
                        if total_cost != 0:  # sino dejo el sumatorio
                            benefic = float(total_income) - float(total_cost)
                            json_data_new['Margin'] = float(benefic) / float(total_cost) * 100
                        data['footerData'] = json_data_new
            data['rows'] = rows
            data['page'] = page
            if error:
                data['error'] = error
            obj = json.dumps(data)
            return obj

    def filters(self, query, cube, database_cube_dict, dimensiones=[], exclude_rows=[], dimension_extra='Id'):

        """
          **Description:**
                This function is used to get all the filters acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. dimensiones: A list of dimensions which calculate the mdx to get the filters if it is not used the filters will be calculated according to all dimensions.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        row = ''
        for dim in dimensiones:
                row = self.filter(query, cube, dim, database_cube_dict, exclude_rows, dimension_extra)
        return row

    def filter(self, query, cube, dimension, database_cube_dict=[], exclude_rows=[], dimension_extra='Id'):
        """
          **Description:**
                This function is used to get one filter acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. dimensiones: A string with the dimension which calculate the mdx to get the filter.
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """

        mdx_class = MDX()
        query_without_select, measure = mdx_class.without_select(query)
        json = ''
        on_rows = []
        on_rows.append(dimension)
        if dimension_extra != 'None':
            dimension_id = (dimension[0], dimension_extra, dimension_extra)
            on_rows.append(dimension_id)
        select = mdx_class.select_for_filter(cube, on_rows=on_rows, medida=measure, exclude_rows=exclude_rows)
        query = select + query_without_select
        res = cube.launch_query(mdx=query.upper())
        json = self.grid(cube, res, database_cube_dict, isfilter=True)
        return json

    def dict(self, cube, result, complete_name=False, format_cube=False):
        """
          **Description:**
                This function is used to get one filter acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. dimensiones: A string with the dimension which calculate the mdx to get the filter.
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        xml_class = XmlResult()
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        list_result = []
        for fila in range(0, numero_filas):
            item = {}
            for dimension in range(0, numero_dimensiones):
                act = (fila * numero_dimensiones) + dimension
                item[axis_y_names[dimension]] = axis_y_values[act]

            for medida in range(0, numero_medidas):
                act = (fila * numero_medidas) + medida
                try:
                    item[axis_x_names[medida]] = axis_x_values[act]
                except:
                    item[axis_x_names[medida]] = 0
            list_result.append(item)
        return list_result


class MDX:

    """
            This class is used to create mdx to launch against the cube.
        **Attributes:**
            Nothing.

    """
    def __init__(self):
        self.dim_date = ('Date', 'Id', 'Id')
        self.dim_time = ('Time', 'Time Field', 'Time Field')

    def without_select(self, query):

        """
          **Description:**
                This function is used to return the same mdx that we pass but without select part, then it will be modify.
          **Args:**
                query: A string which has the mdx.
          **Returns:**
                This function  return a string which is the same mdx that we pass but without select part
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::


        """
        query = query.lower()
        inicio = query.find('rows')+4
        medida = query[inicio:]
        inicio = medida.find('[')
        medida = medida[inicio:]
        final = medida.find('.')
        medida_aux = medida[final:]
        final += medida_aux.find(']')
        medida = medida[:final+1]
        position_rows = query.find('from')
        query = query[position_rows:]
        return query, medida

    def without_rows(self, query):

        """
          **Description:**
                This function is used to return the same mdx that we pass but without select part, then it will be modify.
          **Args:**
                query: A string which has the mdx.
          **Returns:**
                This function  return a string which is the same mdx that we pass but without select part
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::


        """
        query = query.lower()
        inicio = query.find('rows')
        rows = query[inicio:]
        coma = rows.find(',')+1
        query = rows[coma:]
        return query

    def __non_empty(self, part_NON_EMPTY):
        if part_NON_EMPTY:
            return ' non empty '
        else:
            return' '

    def __rows_or_columns2(self, cube, rows, part=[], range_rows={}, exclude_rows={}, part_order={}, part_filter={}):
        dimensiones = cube.dimensiones
        medidas = cube.medidas
        order = ''
        for i in part_order:
            if i in dimensiones:
                order = 'dim'
            elif i in medidas:
                order = 'med'
            else:
                order = 'null'
        mdx = ''
        if part_order and order == 'dim':
            part.remove(part_order.keys()[0])
            part.insert(0, part_order.keys()[0])
        if order != 'dim':
            if part_order and order != 'null':
                if part_order[part_order.keys()[0]] == 'ASC' or part_order[part_order.keys()[0]] == 'BASC':
                    mdx += 'bottomcount('
                else:
                    mdx += 'topcount('
        if part:
            if rows:
                mdx += ' ( '
            else:
                mdx += ' { '
            for i in range(0, len(part)):
                on_row = part[i]
                if on_row in dimensiones:
                    if on_row in range_rows:
                        position = dimensiones[on_row].find('.') + 1
                        dim = dimensiones[on_row][position:]
                        position += dim.find('.') + 1
                        mdx += dimensiones[on_row][:position] + '&[' + str(range_rows[on_row][0]) + ']:'
                        mdx += dimensiones[on_row][:position] + '&[' + str(range_rows[on_row][1]) + ']'
                        if on_row in exclude_rows:
                            for dim in exclude_rows[on_row]:
                                mdx += '-' + dimensiones[on_row][:position] + '&[' + dim + ']'
                        mdx += ','
                    elif not on_row in part_filter:
                        position = dimensiones[on_row].find('.') + 1
                        dim = dimensiones[on_row][position:]
                        position += dim.find('.') + 1
                        mdx += dimensiones[on_row]
                        for exclude in exclude_rows:
                            if on_row in exclude:
                                mdx += '-' + dimensiones[on_row][:position] + '&[' + str(exclude[on_row]) + ']'
                        mdx += ','
                elif on_row in medidas:
                    mdx += medidas[on_row] + ','
                else:
                    swslog('error', 'Failed MDX class 2 : on_row is not in measures neither dimensions', '<<error in {0} >>'.format(str(on_row)))
                    mdx += '<<error in {0} >>'.format(str(on_row))
            mdx = mdx[0:len(mdx) - 1]
            for fil in part_filter:
                if fil in dimensiones:
                    position = dimensiones[fil].find('.') + 1
                    dim = dimensiones[fil][position:]
                    position += dim.find('.') + 1
                    if len(part) == 1:
                        mdx_aux = '{'
                    else:
                        mdx_aux = ',{'
                    for i in range(0, len(part_filter[fil])):
                        mdx_aux += dimensiones[fil][:position] + '&[' + str(part_filter[fil][i]) + '],'
                    mdx += mdx_aux[:-1] + '}'
            if rows:
                mdx += ') '
            else:
                mdx += '} '
            if part_order and order == 'dim':
                mdx = mdx
            elif part_order and order == 'med':
                medida = part_order.keys()[0]
                medida_mdx = '[' + str(medida[0]) + ']' + '.[' + str(medida[1]) + ']'
                mdx += ',100000000,' + medida_mdx+')'
        return mdx

    def __partDate(self, cube, part_where, from_to):

        """
          **Description:**
                This function is used to create the part where when we use date and time dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. fecha:  A string which contain the date that we used.
                #. cube: The cube object which has been used
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :

        """
        mdx = ''
        same_day = False
        same_day = part_where[self.dim_date][0].date() == part_where[self.dim_date][1].date()
        dim = '['+self.dim_date[0]+'].['+self.dim_date[1]+']'
        mdx += '(' + dim + '.&[' + part_where[self.dim_date][from_to].strftime('%Y%m%d') + '] ) *'
        dim = '[' + self.dim_time[0] + '].[' + self.dim_time[1] + ']'
        if not same_day:
            if from_to == 0:
                mdx += '(' + dim + '.&[' + part_where[self.dim_date][from_to].strftime('%H%M') + '] : ' + dim + '.&[2359]) *'
            else:
                mdx += '(' + dim + '.&[0] : ' + dim + '.&[' + part_where[self.dim_date][from_to].strftime('%H%M') + ']) *'
        else:
            mdx += '(' + dim + '.&[' + str(int(part_where[self.dim_date][0].strftime('%H%M'))) + '] : ' + dim + '.&[' + str(int(part_where[self.dim_date][1].strftime('%H%M'))) + ']) *'
        mdx = mdx[:-1]
        return mdx

    def __partComplete(self, cube, part_where, set_time):
        """
          **Description:**
                This function is used to create the part where when we use data dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. nuevas_fechas:  A list of string which contain the dates that we used.
                #. cube: The cube object which has been used
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :

        """
        mdx = ''
        dim = '['+self.dim_date[0]+'].['+self.dim_date[1]+']'
        mdx += '(' + dim + '.&[' + part_where[self.dim_date][0].strftime('%Y%m%d') + '] : ' + dim + '.&[' + part_where[self.dim_date][1].strftime('%Y%m%d') + '])'
        if set_time:
            dim_time = '['+self.dim_time[0]+'].['+self.dim_time[1]+']'
            mdx += ' * (' + dim_time + '.&[' + str(int(part_where[self.dim_date][0].strftime('%H%M'))) + '] : ' + dim_time + '.&[' + str(int(part_where[self.dim_date][1].strftime('%H%M'))) + '])'
        return mdx

    def partRest(self, cube, part_where):
        mdx = ''
        for i in part_where:
            if not ('Date' in i or 'Time' in i):
                if i in cube.dimensiones:
                    dim = '['+i[0]+'].['+i[1]+']'
                    if type(part_where[i])is str or type(part_where[i]) is unicode or type(part_where[i]) is int:
                        part_where_aux = part_where[i]
                        if type(part_where[i]) in [str, unicode]:
                            part_where_aux = part_where[i].split(',')
                        if type(part_where[i]) is int:
                            part_where_aux = [part_where[i]]
                        mdx += ',{'
                        for one in part_where_aux:
                            mdx += dim + '.&['+str(one) + '],'
                        mdx = mdx[0:-1]
                        mdx += '}'
                    elif (type(part_where[i]) is tuple or type(part_where[i]) is list):
                        if part_where[i][0] == '-' and type(part_where[i][1]) == list:
                            exclude = ''
                            for n in part_where[i][1]:
                                exclude = exclude + str(part_where[i][0]) + dim + '.&[' + n + '] '
                            mdx += ',{(' + dim + '.' + '['+str(i[2])+']' + exclude + ' )}'

                        elif part_where[i][0] == '' and type(part_where[i][1]) == list:
                            exclude = ''
                            for n in part_where[i][1]:
                                exclude = exclude + '-' + dim + '.&[' + n + '] '
                            mdx += ',{(' + dim + '.' + '[' + str(i[2]) + ']' + exclude + ' )}'
                        else:
                            mdx += ',{'
                            for n in part_where[i]:
                                mdx += '(' + dim + '.&[' + str(n) + '] ),'
                            mdx = mdx[:-1]
                            mdx += '}'
        return mdx

    def __where_dict(self, cube, part_where):
        mdx = ''
        time_from = int(part_where[self.dim_date][0].time().strftime('%H%M')) == 0
        time_to = int(part_where[self.dim_date][1].time().strftime('%H%M')) == 2359
        if time_from and time_to:
            mdx += '{' + self.__partComplete(cube, part_where, False) + '} '
        else:
            if part_where[self.dim_date][0].date() == part_where[self.dim_date][1].date():
                mdx += '{' + self.__partDate(cube, part_where, 0) + '} '
            else:
                if not time_from:
                    mdx += '{' + self.__partDate(cube, part_where, 0) + '} +'
                    part_where[self.dim_date][0] = datetime.combine(part_where[self.dim_date][0] + timedelta(days=1), time.min)

                if not time_to:
                    mdx += '{' + self.__partDate(cube, part_where, 1) + '} +'
                    part_where[self.dim_date][1] = datetime.combine(part_where[self.dim_date][1] - timedelta(days=1), time.max)

                if not(part_where[self.dim_date][0] > part_where[self.dim_date][1]):
                    mdx += '{' + self.__partComplete(cube, part_where, True) + '} '
                else:
                    mdx = mdx[:-1]
        mdx += self.partRest(cube, part_where)
        return ' ( ' + mdx + ' ) '

    # def __order(self, cube, order, part_order):
    #     dimensiones = cube.dimensiones
    #     medidas = cube.medidas
    #     mdx = ', '
    #     if order in dimensiones:
    #         dimension = dimensiones[order]
    #         p_pto = dimension.find('.') + 1
    #         d = dimension[p_pto:]
    #         p_pto += d.find('.')
    #         dimension = dimension[0:p_pto + 1] + 'membervalue'
    #         mdx += dimension + ', ' + part_order[order]
    #     elif order in medidas:
    #         mdx += medidas[order] + ', ' + part_order[order]
    #     else:
    #         swslog('error', 'Failed MDX class 3 : on_row is not in measures neither dimensions', '<<error in order {0}>> '.format(str(order)))
    #         mdx += '<<error in order {0}>> '.format(str(order))
    #     mdx += ' ) '
    #     return mdx

    def __part_order(self, cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter):
        mdx = ''
        for order in part_order:
            if part_order[order] == 'ASC' or part_order[order] == 'DESC' or part_order[order] == 'BASC' or part_order[order] == 'BDESC':
                mdx += self.__rows_or_columns2(cube, True, part_on_rows, range_rows, exclude_rows, part_order, part_filter)
            else:
                mdx += self.__rows_or_columns2(cube, True, part_on_rows, range_rows, exclude_rows, part_filter=part_filter)
        return mdx

    # def __filter(self, cube, part_filter, part_on_rows, range_rows, exclude_rows):
    #     mdx = ''
    #     medidas = cube.medidas
    #     filtrada = False
    #     dimensiones = cube.dimensiones
    #     mdx += 'filter( '
    #     mdx += self.__rows_or_columns2(cube, True, part_on_rows, range_rows, exclude_rows) + ', '
    #     for filte in part_filter:
    #         if filtrada:
    #             mdx += ' and '
    #         if filte in dimensiones:
    #             dimension = dimensiones[filte]
    #             position = dimension.find('.')
    #             dimension = dimension[position+1:]
    #             position += dimension.find('.')+1
    #             dimension = dimensiones[filte][:position]
    #             mdx += dimension+'.&['+part_filter[filte]+']'
    #         elif filte in medidas:
    #             mdx += medidas[filte]+filte[filte][0] + filte[filte][1]
    #         else:
    #             swslog('error', 'Failed MDX class 4 : filter is not in dimensions neither measures', '<<error in filter {0}>> '.format(str(filte)))
    #             mdx += '<<error in filter {0}>> '.format(str(filte))
    #         filtrada = True
    #     return mdx+'  ) '

    def __on_row(self, cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter):
        mdx = ''
        if part_order:
            if len(part_order) == 1:
                mdx += self.__part_order(cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter)
            else:
                swslog('error', 'Failed MDX class 5 : try to order by more than two dimensions', '<< part_order must be like {0}>>'.format(str({('Measures', 'Calls'): 'ASC'})))
                mdx += '<< part_order must be like {0}>>'.format(str({('Measures', 'Calls'): 'ASC'}))
        else:
            mdx += self.__rows_or_columns2(cube, True, part_on_rows, range_rows, exclude_rows, part_filter=part_filter)
        return mdx

    # Pasandole unos parametros se forma la mdx
    # [('client','client'),('client','id'),...] part_on_rows y part_on_columns del mismo tipo
    # range rows= {('client','fechask'):[('value1'),('value2')]}
    # part_from un string indicando el nombre del cubo
    # part_where {('cdrfint','fechask'):('20130101000000','20130125000000'),('client','id'):'54'...}
    # part_order {('measure','calls'):'ASC'} ASC , DESC , BASC , BDESC
    # part_filter {('measure','calls'):'>1000'}
    # NON_EMPTY es un boolean para indicar si se quiere ese campo
    def __with_set_member_part(self, cube, part_rows=[], part_ranking=[]):
        mdx = ''
        mdx += 'WITH SET orderedDimension as topcount(['+part_rows[0][0]+'].['+part_rows[0][1]+'].['+part_rows[0][2]+'].members,100000000,['+part_ranking[2][0]+'].['+part_ranking[2][1]+'])'
        mdx += ' MEMBER ranking_medida as RANK(['+part_rows[0][0]+'].['+part_rows[0][1]+'].CurrentMember,orderedDimension)'
        return mdx

    def __select_rank(self, cube, part_rows=[], part_ranking=[]):
        mdx = ''
        mdx += 'select '
        if part_ranking[0] == "ASC" or part_ranking[0] == "BASC":
            mdx += 'bottomcount('
        else:
            mdx += 'topcount('
        mdx += 'orderedDimension,' + part_ranking[1] + ') on rows,'
        return mdx

    def __mdx_rank(self, cube, part_rows=[], part_columns=[], part_ranking=[], range_rows=[], exclude_rows=[]):
        mdx = ''
        mdx += self.__with_set_member_part(cube, part_rows, part_ranking)
        mdx += self.__select_rank(cube, part_rows, part_ranking)
        mdx += self.__rows_or_columns2(cube, False, part_columns, range_rows, exclude_rows)
        mdx += ' on columns'
        return mdx

    def mdx(self, cube, part_rows=[], range_rows=[], exclude_rows={}, part_columns=[], part_from='', part_where={}, part_order=[], part_NON_EMPTY=True, total_data=False, part_ranking=[]):

        """
          **Description:**
                This function is used to create the mdx which we will use to launch against the cube.
          **Args:**
                #. cube: An object cube which we have used to create the connection.
                #. part_rows: A list of tuples with three values to indicate the dimension to browse : [('client','client','client'),('client','id','all'),...]
                #. range_rows: A dict where we put the dimension which we want aplicate the range and like value the values of the range.
                #. exclude_rows: A list of dict for the columns and value to exclude: [{('client','client'):2345},{('client','id'):...}]
                #. part_columns: A list of tuples for the columns to indicate the measures to browse: [('Measure','Calls'),('Measure','Attempts'),...]
                #. part_from  A string with the name of the cube :'[stoneworksolutions dev]'
                #. part_where:  A dict. The key is the dimension and the value is the value which want put in the where :{('client','client'):'Aryans',('cdrfint','fecha'):('2013101010101010','2013101110101010')....}
                #. part_order: A dict with only one key.The key is the measure or dimension to order and the value indicate the order to do, it can be('ASC','DESC','BASC','BDESC') :{('measure','calls'):'ASC'}

                #. part_NON_EMPTY: A booleann that indicate if is True that we want the clausule 'non empty' in the mdx , by contrast we don`t want non empty in the mdx
                #. total_data: A boolean. If it is true in the part rows will be put the dimension [Destination].[Destination].[Destination] only so the values will be gruped.
                #. part_ranking: A list with differents values. An example is part_rank=["ASC","10",('Measure','Calls')]. The first value indicates how we want the order, the second how many rows will be return and the third the measure on which will do the ranking.


                # EXAMPLESSSSSSSS
                # from sws_tags.sws_utils.cube_utils import *
                # mdx=MDX()
                # cube=CUBE()
                # cube.connect('apollo','sultan2014',['Cdrt','ChannelUSage'],redis_conn)
                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # mdx.mdx(cube,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Provider','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Provider','Id','Id'),('Client','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Destination','Id','Id'),('Provider','Id','Id'),('Client','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

          **Returns:**
                This function return a string which is a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
              Nothing.
          Other information ::


        """
        #select
        ##MIRAR SI EN SELECT Y EN WHERE ESTA LA MISMA DIMENION DE SER ASI DEJARLA SOLO EL SELECT Y UTILIZAR FILTER
        part_filter = {}
        part_rows = self.quitarDuplicados(part_rows)
        part_filter, part_where = self.__whereInSelect(part_where, part_rows, part_filter)
        mdx = ''
        if cube.dimensiones:
            if part_ranking:
                mdx = self.__mdx_rank(cube, part_rows=part_rows, part_columns=part_columns, part_ranking=part_ranking, range_rows=range_rows, exclude_rows=exclude_rows)
            else:
                mdx = 'select'
                mdx += self.__non_empty(part_NON_EMPTY)
                if len(part_rows) > 0:
                    mdx += self.__on_row(cube, part_rows, range_rows, exclude_rows, part_order, part_filter)
                    mdx += 'on rows, '
                if total_data is True:
                    mdx = 'select non empty ([Destination].[Destination].[Destination])'
                    mdx += 'on rows, '
                mdx += self.__rows_or_columns2(cube, False, part_columns, range_rows, exclude_rows)
                mdx += ' on columns'
            if part_where:
                if not type(part_where[self.dim_date][0]) is datetime:
                    if type(part_where[self.dim_date]) is tuple:
                        part_where[self.dim_date] = list(part_where[self.dim_date])
                    part_where[self.dim_date][0] = datetime.strptime(part_where[self.dim_date][0], '%Y%m%d%H%M%S')
                    part_where[self.dim_date][1] = datetime.strptime(part_where[self.dim_date][1], '%Y%m%d%H%M%S')
                mdx += ' from (select '
                mdx += self.__where_dict(cube, part_where)
                mdx += ' on columns from ' + part_from + ' ) '
            else:
                mdx += ' from ' + part_from
            return mdx
        else:
            swslog('error', 'Failed MDX 7 class : cube has not dimensions or it is not good connect', '')
            return 'cube has not dimensions or it is not good connect'

    def quitarDuplicados(self, col_cube):
        new_col_cube = []
        for i in col_cube:
            if not i in new_col_cube:
                new_col_cube.append(i)
        return new_col_cube

    def __whereInSelect(self, part_where, part_rows, part_filter):
        dimensiones = []
        for i in part_where:
            for j in part_rows:
                if i == j:
                    dimensiones.append(i)
        return self.__quitar_where_poner_filter(dimensiones, part_where, part_filter)

    def __quitar_where_poner_filter(self, dimensiones, part_where, part_filter):
        new_filter = {}
        for dimension in dimensiones:
            valor_filter = part_where[dimension]
            del part_where[dimension]
            if isinstance(valor_filter, types.ListType):
                new_filter[dimension] = valor_filter
            else:
                new_filter[dimension] = [valor_filter]
        return new_filter, part_where

    def select_for_filter(self, cube, on_rows=[], medida='', exclude_rows={}):

        """
          **Description:**
                This function is used only from the method filter and is used to create his select part.
          **Args:**
                #. cube: A cube instance.
                #. on_rows: A list whit the dimensions to use.
                #. medida: A string which indicate a measure to put.
          **Returns:**
                A string which is a mdx but only the select
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
              Nothing.
          Other information ::

        """
        select = 'select non empty'
        select += self.__rows_or_columns2(cube, True, part=on_rows, range_rows={}, exclude_rows=exclude_rows)
        select += ' on rows, {'+medida+'} on columns '
        return select

################################################################################################################################################
################################################################################################################################################
