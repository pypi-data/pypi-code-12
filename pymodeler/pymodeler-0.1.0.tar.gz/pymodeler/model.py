#!/usr/bin/env python
"""
A Model object is just a container for a set of Parameter.
Implements __getattr__ and __setattr__.

The model has a set of default parameters stored in Model._params. 
Careful, if these are changex, they will be changed for all 
subsequent instances of the Model.

The parameters for a given instance of a model are stored in the
Model.params attribute. This attribute is a deepcopy of 
Model._params created during instantiation.

"""
from collections import OrderedDict as odict
import numpy as np
import copy
import yaml

from pymodeler.parameter import *

def indent(string,width=0): 
    """ Helper function to indent lines in printouts
    """
    return '{0:>{1}}{2}'.format('',width,string)

class Model(object):
    """ A base class to manage Parameters and Properties

    Users should define Model sub-classes and override the 
    _params and _mapping static data members to define the
    parameters and mappings they want.

    Example class

    class ModelExample:
       # Define the parameters for this class
       _params = odict([('fuel_rate',Property(default=10.,dtype=float,units="km/l")),
                        ('fuel_type',Property(default="diesel",dtype=str)),
                        ('distance',Parameter(default=10.,units="km")),
                        ('fuel_needed',Derived(units="l"))])
      
       # Define mappings for this class
       _mapping = odict([("dist","distance"),
                         ("rate","fuel_rate")])
       
       # Define the loader function for the fuel_needed Derived property
       def _fuel_needed(self):
         return self.distance / self.fuel_rate


    Interface aspects:

    Construction:

      Default, all Properties take their default values:
      m = ModelExample()

      Setting Properties:
      m = ModelExample(fuel_rate=7, distance=12.)

      Setting Properties using the Mapping:
      m = ModelExample(rate=7, dist=12.)

      Setting Paramter errors / bounds:
      m = ModelExample(distance = dict(value=12,errors=[1.,1.],bounds=[7.,15.]))


    Access to properties:

      Get the value of a Property, Parameter or Derived Parameter:
      m.fuel_rate
      m.distance
      m.fuel_neded
      m.dist                      # Uses the mapping
      
      Get access to a Property, e.g.,to know something about it besides the value,
      note that this can also be used to modify the attributes of the properties:
      m.getp('fuel_rate').dtype  
      m.getp('distance').errors

      Get acess to only the Parameter type properties
      m.get_params()             # Get all of the Parameters
      m.get_params(paramNames)   # Get a subset of the Parameters, by name


    Setting Properties or Paramaters:

      Set the value of a Property or Parameter:
      m.fuel_rate = 8.
      m.fuel_rate = "xx"          # This will throw a TypeError
      m.fuel_type = "gasoline"
      m.distance = 10.            
      m.dist = 10.                # Uses the mapping
     
      Set the attributes of a Property:
      m.setp('fuel_rate',value=7.)    # equivalent to m.fuel_rate = 7.
      m.setp('fuel_rate',value="xx")  # This will throw a TypeError
      m.setp('distance',value=12,errors=[1.,1.],bounds=[7.,15.])

      Set all the Properties using a dictionary or mapping
      m.set_attributes(**kwargs)

      Clear all of the Derived properties (to force recomputation)
      m.clear_derived()

    Output:

      Convert to an ~collections.OrderedDict 
      m.todict()

      Convert to a yaml string:
      m.dump()

      Access the values of all the Parameter objects:
      m.param_values()            # Get all the parameter values
      m.param_values(paramNames)  # Get a subset of the parameter values, by name

      Access the errors of all the Parameter objects:
      m.param_errors()            # Get all the parameter values
      m.param_errors(paramNames)  # Get a subset of the parameter values, by name

    """

    # `_params` is a tuple of Property objects
    # _params = (('parameter name',Property(...)),...)
    _params = odict([])
    # `_mapping` is an alternative name mapping
    # for the parameters in _params
    _mapping = odict([])

    def __init__(self,*args,**kwargs):
        """ C'tor.  Build from a set of keyword arguments.
        """

        self.params = self.defaults
        self._init_properties()
        self.set_attributes(**kwargs)
        # In case no properties were set, cache anyway
        self._cache()

    def __getattr__(self,name):
        """ Access operator, i.e., x = m.name
        """
        # Return 'getp' of parameter
        if name in self._params or name in self._mapping:
            return self.getp(name).value
        else:
            # Raises AttributeError
            return object.__getattribute__(self,name)

    def __setattr__(self, name, value):
        """ Assignement operator, i.e., m.name = x
        """ 
        # Call 'setp' on parameters
        if name in self._params or name in self._mapping:
            self.setp(name, value=value)
        else:
            # Why is this a return statement
            return object.__setattr__(self, name, value)

    def __str__(self,indent=0):
        """ Cast model as a formatted string
        """
        try:
            ret = '{0:>{2}}{1}'.format('',self.name,indent)
        except:
            ret = "%s"%(type(self))
        if len(self.params)==0:
            pass
        else:            
            ret += '\n{0:>{2}}{1}'.format('','Parameters:',indent+2)
            width = len(max(self.params.keys(),key=len))
            for name,value in self.params.items():
                par = '{0!s:{width}} : {1!r}'.format(name,value,width=width)
                ret += '\n{0:>{2}}{1}'.format('',par,indent+4)
        return ret

    @property
    def defaults(self):
        """Ordered dictionary of default parameters."""
        # Deep copy is necessary so that default parameters remain unchanged
        return copy.deepcopy(self._params)

    @property
    def mappings(self):
        """Ordered dictionary of mapping."""
        return copy.deepcopy(self._mapping)

    #@property
    #def name(self):
    #    return self.__class__.__name__

    def getp(self, name):
        """ 
        Get the named parameter.

        Parameters
        ----------
        name : string
            The parameter name.

        Returns
        -------
        param : 
            The parameter object.
        """
        name = self._mapping.get(name,name)
        return self.params[name]

    def setp(self, name, clear_derived=True, value=None, bounds=None, free=None, errors=None):
        """ 
        Set the value (and bounds) of the named parameter.

        Parameters
        ----------
        name : string
            The parameter name.
        value: 
            The value of the parameter
        bounds: None
            The bounds on the parameter
        Returns
        -------
        None
        """
        name = self._mapping.get(name,name)
        self.params[name].set(value=value,bounds=bounds,free=free,errors=errors)
        if clear_derived:
            self.clear_derived()
        self._cache(name)

    def set_attributes(self, **kwargs):
        """
        Set a group of attributes (parameters and members).  Calls
        `setp` directly, so kwargs can include more than just the
        parameter value (e.g., bounds, free, etc.).
        """
        self.clear_derived()
        kwargs = dict(kwargs)
        for name,value in kwargs.items():
            # Raise AttributeError if param not found
            try:
                self.__getattr__(name) 
            except (AttributeError):
                try: self.getp(name)
                except:
                    print ("Warning: %s does not have attribute %s"%(type(self),name))
            # Set attributes
            try: self.setp(name,clear_derived=False,**value)
            except TypeError:
                try: self.setp(name,clear_derived=False,*value)
                except (TypeError,KeyError):  
                    try: self.setp(name,clear_derived=False,value=value)
                    except (TypeError,KeyError):  
                        self.__setattr__(name,value)
            # pop this attribued off the list of missing properties
            self._missing.pop(name,None)
        # Check to make sure we got all the required properties
        if len(self._missing) != 0:
            raise ValueError("One or more required properties are missing ",self._missing.keys())


    def _init_properties(self):
        """ Loop through the list of Properties, 
        extract the derived and required properties and do the
        appropriate book-keeping
        """
        self._missing = {}
        for k,p in self.params.items():
            if p.required:
                self._missing[k] = p
            if isinstance(p,Derived):
               if p.loader is None:
                   # Default to using _<param_name>
                   p.loader = self.__getattribute__("_%s"%k)
               elif isinstance(p.loader,str):
                   p.loader = self.__getattribute__(p.loader)
        
    def get_params(self,pnames=None):
        """ Return a list of Parameter objects

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects
        
        Returns
        -------
        list of Parameters
        """
        l = []
        if pnames is None:
            pnames = self.params.keys()
        for pname in pnames:
            p = self.params[pname]
            if isinstance(p,Parameter):  
                l.append(p)
        return l

    def param_values(self,pnames=None):
        """ Return an array with the parameter values

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects
        
        Returns
        -------
        ~numpy.array of parameter values
        """
        l = self.get_params(pnames)
        v = [p.value for p in l]
        return np.array(v)


    def param_errors(self,pnames=None):
        """ Return an array with the parameter errors

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects
        
        Returns
        -------
        ~numpy.array of parameter errors

        Note that this is a N x 2 array.  
        """
        l = self.get_params(pnames)
        v = [p.errors for p in l]
        return np.array(v)

   
    def clear_derived(self):
        """ Reset the value of all Derived properties to None

        This is called by setp (and by extension __setattr__)
        """
        for k,p in self.params.items():
           if isinstance(p,Derived):  
               p.clear_value()
        
    def todict(self):
        """ Return self cast as an '~collections.OrderedDict' object 
        """
        ret = odict(name = self.__class__.__name__)
        ret.update(self.params)
        return ret

    def dump(self):
        """ Dump this object as a yaml string
        """
        return yaml.dump(self.todict())

    def _cache(self, name=None):
        """ 
        Method called in _setp to cache any computationally
        intensive properties after updating the parameters.

        Parameters
        ----------
        name : string
           The parameter name.

        Returns
        -------
        None
        """
        pass



        
if __name__ == "__main__":

    import argparse
    description = "python script"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('args',nargs=argparse.REMAINDER)
    opts = parser.parse_args(); args = opts.args

