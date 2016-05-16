# -*- coding: utf-8 -*-

"""
   Pinch.Models.Webhook
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class Webhook(BaseModel):

    """Implementation of the 'Webhook' model.

    TODO: type model description here.

    Attributes:
        id (int): TODO: type description here.
        url (string): TODO: type description here.
        webhook_type (int): TODO: type description here.

    """

    def __init__(self, 
                 id = None,
                 url = None,
                 webhook_type = None):
        """Constructor for the Webhook class"""
        
        # Initialize members of the class
        self.id = id
        self.url = url
        self.webhook_type = webhook_type

        # Create a mapping from Model property names to API property names
        self.names = {
            "id": "id",
            "url": "url",
            "webhook_type": "webhook_type",
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
            url = dictionary.get("url")
            webhook_type = dictionary.get("webhook_type")
            # Return an object of this model
            return cls(id,
                       url,
                       webhook_type)
