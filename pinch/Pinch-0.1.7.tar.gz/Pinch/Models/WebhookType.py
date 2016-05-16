# -*- coding: utf-8 -*-

"""
   Pinch.Models.WebhookType
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class WebhookType(BaseModel):

    """Implementation of the 'Webhook Type' model.

    TODO: type model description here.

    Attributes:
        id (int): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self, 
                 id = None,
                 name = None):
        """Constructor for the WebhookType class"""
        
        # Initialize members of the class
        self.id = id
        self.name = name

        # Create a mapping from Model property names to API property names
        self.names = {
            "id": "id",
            "name": "name",
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
            id = dictionary.get("id")
            name = dictionary.get("name")
            # Return an object of this model
            return cls(id,
                       name)
