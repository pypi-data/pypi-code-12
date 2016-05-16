# -*- coding: utf-8 -*-

"""
   Pinch.Models.Document
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class Document(BaseModel):

    """Implementation of the 'Document' model.

    TODO: type model description here.

    Attributes:
        url (string): Where to retrieve the document

    """

    def __init__(self, 
                 url = None):
        """Constructor for the Document class"""
        
        # Initialize members of the class
        self.url = url

        # Create a mapping from Model property names to API property names
        self.names = {
            "url": "url",
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
            url = dictionary.get("url")
            # Return an object of this model
            return cls(url)
