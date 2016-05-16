# -*- coding: utf-8 -*-

"""
   Pinch.Models.Unit
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class Unit(BaseModel):

    """Implementation of the 'Unit' model.

    TODO: type model description here.

    Attributes:
        reference (string): TODO: type description here.
        tenant_name (string): TODO: type description here.
        floor_number (string): TODO: type description here.
        kind (string): TODO: type description here.
        french_floor_number (string): TODO: type description here.

    """

    def __init__(self, 
                 reference = None,
                 tenant_name = None,
                 floor_number = None,
                 kind = None,
                 french_floor_number = None):
        """Constructor for the Unit class"""
        
        # Initialize members of the class
        self.reference = reference
        self.tenant_name = tenant_name
        self.floor_number = floor_number
        self.kind = kind
        self.french_floor_number = french_floor_number

        # Create a mapping from Model property names to API property names
        self.names = {
            "reference": "reference",
            "tenant_name": "tenant_name",
            "floor_number": "floor_number",
            "kind": "kind",
            "french_floor_number": "french_floor_number",
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
            tenant_name = dictionary.get("tenant_name")
            floor_number = dictionary.get("floor_number")
            kind = dictionary.get("kind")
            french_floor_number = dictionary.get("french_floor_number")
            # Return an object of this model
            return cls(reference,
                       tenant_name,
                       floor_number,
                       kind,
                       french_floor_number)
