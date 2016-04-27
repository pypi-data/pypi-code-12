import cf
import numpy
import os
import unittest

class ExamplesTest(unittest.TestCase):
    def test_example1(self):
        f = cf.Field()
        print_f = str(f)
        
        self.assertTrue(
            print_f == 
            ' field summary\n--------------\n\n')
        #--- End: def

    def test_example2(self):
            f = cf.Field(properties={'standard_name': 'air_temperature',
                                     'long_name': 'temperature of air'})
            print_f = str(f)
        
            self.assertTrue(
                print_f ==
                'air_temperature field summary\n-----------------------------\n\n')
    #--- End: def

    def test_example3(self):
        data = cf.Data(numpy.arange(90.).reshape(10, 9), 'm s-1')
        properties = {'standard_name': 'eastward_wind'}
        dim0 = cf.DimensionCoordinate(data=cf.Data(range(10), 'degrees_north'),
                                      properties={'standard_name': 'latitude'})
        dim1 = cf.DimensionCoordinate(data=cf.Data(range(9), 'degrees_east'))
        dim1.standard_name = 'longitude'
        domain = cf.Domain(dim=[dim0, dim1])
        f = cf.Field(properties=properties, data=data, domain=domain)
        print_f = str(f)

        self.assertTrue(
            print_f == 
'''eastward_wind field summary
---------------------------
Data           : eastward_wind(latitude(10), longitude(9)) m s-1
Axes           : longitude(9) = [0, ..., 8] degrees_east
               : latitude(10) = [0, ..., 9] degrees_north
''')

        aux = cf.AuxiliaryCoordinate(data=cf.Data(['alpha','beta','gamma','delta','epsilon',
                                                   'zeta','eta','theta','iota','kappa']))

        aux.long_name = 'extra'
        f.insert_aux(aux, axes=['dim0'])
        f.cell_methods = cf.CellMethods('latitude: point')
        f.long_name = 'wind' 
        print_f = str(f)

        self.assertTrue(
            print_f == '''eastward_wind field summary
---------------------------
Data           : eastward_wind(latitude(10), longitude(9)) m s-1
Cell methods   : latitude: point
Axes           : longitude(9) = [0, ..., 8] degrees_east
               : latitude(10) = [0, ..., 9] degrees_north
Aux coords     : long_name:extra(latitude(10)) = [alpha, ..., kappa]
''')

        f.remove_item({'long_name': 'extra'})
        del f.cell_methods
        print_f = str(f)

        self.assertTrue(
            print_f == '''eastward_wind field summary
---------------------------
Data           : eastward_wind(latitude(10), longitude(9)) m s-1
Axes           : longitude(9) = [0, ..., 8] degrees_east
               : latitude(10) = [0, ..., 9] degrees_north
''')
    #--- End: def

    def test_example4(self):
        #---------------------------------------------------------------------
        # 1. CREATE the field's domain items
        #---------------------------------------------------------------------
        # Create a grid_latitude dimension coordinate
        Y = cf.DimensionCoordinate(properties={'standard_name': 'grid_latitude'},
                                      data=cf.Data(numpy.arange(10.), 'degrees'))
        
        # Create a grid_longitude dimension coordinate
        X = cf.DimensionCoordinate(data=cf.Data(numpy.arange(9.), 'degrees'))
        X.standard_name = 'grid_longitude'
        
        # Create a time dimension coordinate (with bounds)
        bounds = cf.CoordinateBounds(
            data=cf.Data([0.5, 1.5], cf.Units('days since 2000-1-1', calendar='noleap')))
        T = cf.DimensionCoordinate(properties=dict(standard_name='time'),
                                   data=cf.Data(1, cf.Units('days since 2000-1-1',
                                                            calendar='noleap')),
                                   bounds=bounds)
        
        # Create a longitude auxiliary coordinate
        lat = cf.AuxiliaryCoordinate(data=cf.Data(numpy.arange(90).reshape(10, 9),
                                                  'degrees_north'))
        lat.standard_name = 'latitude'
        
        # Create a latitude auxiliary coordinate
        lon = cf.AuxiliaryCoordinate(properties=dict(standard_name='longitude'),
                                     data=cf.Data(numpy.arange(1, 91).reshape(9, 10),
                                                  'degrees_east'))
        
        # Create a rotated_latitude_longitude grid mapping coordinate reference
        grid_mapping = cf.CoordinateReference('rotated_latitude_longitude',
                                              grid_north_pole_latitude=38.0,
                                              grid_north_pole_longitude=190.0)
        
        # --------------------------------------------------------------------
        # 2. Create the field's domain from the previously created items
        # --------------------------------------------------------------------
        domain = cf.Domain(dim=[T, Y, X],
                           aux=[lat, lon],
                           ref=grid_mapping)

        #---------------------------------------------------------------------
        # 3. Create the field
        #---------------------------------------------------------------------
        # Create CF properties
        properties = {'standard_name': 'eastward_wind',
                      'long_name'    : 'East Wind',
                      'cell_methods' : cf.CellMethods('latitude: point')}
        
        # Create the field's data array
        data = cf.Data(numpy.arange(90.).reshape(9, 10), 'm s-1')
        
        # Finally, create the field
        f = cf.Field(properties=properties,
                     domain=domain,
                     data=data)
        
        print_f = str(f)

        self.assertTrue(
            print_f == '''eastward_wind field summary
---------------------------
Data           : eastward_wind(grid_longitude(9), grid_latitude(10)) m s-1
Cell methods   : latitude: point
Axes           : time(1) = [2000-01-02 00:00:00] noleap
               : grid_longitude(9) = [0.0, ..., 8.0] degrees
               : grid_latitude(10) = [0.0, ..., 9.0] degrees
Aux coords     : latitude(grid_latitude(10), grid_longitude(9)) = [[0, ..., 89]] degrees_north
               : longitude(grid_longitude(9), grid_latitude(10)) = [[1, ..., 90]] degrees_east
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
''')
    #--- End: def

    def test_example5(self):
        import cf
        import numpy
        
     
        #---------------------------------------------------------------------
        # 1. CREATE the field's domain items
        #---------------------------------------------------------------------
        # Create a grid_latitude dimension coordinate
        Y = cf.DimensionCoordinate(properties={'standard_name': 'grid_latitude'},
                                      data=cf.Data(numpy.arange(10.), 'degrees'))
        
        # Create a grid_longitude dimension coordinate
        X = cf.DimensionCoordinate(data=cf.Data(numpy.arange(10.), 'degrees'))
        X.standard_name = 'grid_longitude'
        
        # Create a time dimension coordinate (with bounds)
        bounds = cf.CoordinateBounds(
            data=cf.Data([0.5, 1.5], cf.Units('days since 2000-1-1', calendar='noleap')))
        T = cf.DimensionCoordinate(properties=dict(standard_name='time'),
                                   data=cf.Data(1, cf.Units('days since 2000-1-1',
                                                            calendar='noleap')),
                                   bounds=bounds)
        
        # Create a longitude auxiliary coordinate
        lat = cf.AuxiliaryCoordinate(data=cf.Data(numpy.arange(100).reshape(10, 10),
                                                  'degrees_north'))
        lat.standard_name = 'latitude'
        
        # Create a latitude auxiliary coordinate
        lon = cf.AuxiliaryCoordinate(properties=dict(standard_name='longitude'),
                                     data=cf.Data(numpy.arange(1, 101).reshape(10, 10),
                                                  'degrees_east'))
        
        # Create a rotated_latitude_longitude grid mapping coordinate reference
        grid_mapping = cf.CoordinateReference('rotated_latitude_longitude',
                                              grid_north_pole_latitude=38.0,
                                              grid_north_pole_longitude=190.0)
        
        # --------------------------------------------------------------------
        # 2. Create the field's domain from the previously created items
        # --------------------------------------------------------------------
        domain = cf.Domain(dim=[T, Y, X],
                           aux={'aux0': lat, 'aux1': lon},
                           ref=grid_mapping,
     		      assign_axes={'aux0': ['grid_latitude', 'grid_longitude'],
                               	   'aux1': ['grid_longitude', 'grid_latitude']})
     
        #---------------------------------------------------------------------
        # 3. Create the field
        #---------------------------------------------------------------------
        # Create CF properties
        properties = {'standard_name': 'eastward_wind',
                      'long_name'    : 'East Wind',
                      'cell_methods' : cf.CellMethods('latitude: point')}
        
        # Create the field's data array
        data = cf.Data(numpy.arange(100.).reshape(10, 10), 'm s-1')
        
        # Finally, create the field
        f = cf.Field(properties=properties,
                     domain=domain,
                     data=data,
                     axes=['grid_latitude', 'grid_longitude'])
         
        print_f = str(f)

        self.assertTrue(
            print_f == '''eastward_wind field summary
---------------------------
Data           : eastward_wind(grid_latitude(10), grid_longitude(10)) m s-1
Cell methods   : latitude: point
Axes           : time(1) = [2000-01-02 00:00:00] noleap
               : grid_longitude(10) = [0.0, ..., 9.0] degrees
               : grid_latitude(10) = [0.0, ..., 9.0] degrees
Aux coords     : latitude(grid_latitude(10), grid_longitude(10)) = [[0, ..., 99]] degrees_north
               : longitude(grid_longitude(10), grid_latitude(10)) = [[1, ..., 100]] degrees_east
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
''')
    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)

