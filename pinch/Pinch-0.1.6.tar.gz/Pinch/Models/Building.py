# -*- coding: utf-8 -*-

"""
   Pinch.Models.Building
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class Building(BaseModel):

    """Implementation of the 'Building' model.

    TODO: type model description here.

    Attributes:
        reference (string): TODO: type description here.
        name (string): TODO: type description here.
        address (string): TODO: type description here.
        zip_code (string): TODO: type description here.
        city (string): TODO: type description here.
        country (string): TODO: type description here.
        latitude (float): TODO: type description here.
        longitude (float): TODO: type description here.

    """

    def __init__(self, 
                 reference = None,
                 name = None,
                 address = None,
                 zip_code = None,
                 city = None,
                 country = None,
                 latitude = None,
                 longitude = None):
        """Constructor for the Building class"""
        
        # Initialize members of the class
        self.reference = reference
        self.name = name
        self.address = address
        self.zip_code = zip_code
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

        # Create a mapping from Model property names to API property names
        self.names = {
            "reference": "reference",
            "name": "name",
            "address": "address",
            "zip_code": "zip_code",
            "city": "city",
            "country": "country",
            "latitude": "latitude",
            "longitude": "longitude",
        }

    @classmethod
    def from_dictionary(cls, 
                        dictionary):
        """Creates an instance of this model from a dictionary
       
        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.
            
        Returns:
            object: An instance of this structure class.
            
        """

        if dictionary == None:
            return None
        else:	
            # Extract variables from the dictionary
            reference = dictionary.get("reference")
            name = dictionary.get("name")
            address = dictionary.get("address")
            zip_code = dictionary.get("zip_code")
            city = dictionary.get("city")
            country = dictionary.get("country")
            latitude = dictionary.get("latitude")
            longitude = dictionary.get("longitude")
            # Return an object of this model
            return cls(reference,
                       name,
                       address,
                       zip_code,
                       city,
                       country,
                       latitude,
                       longitude)
