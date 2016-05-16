# -*- coding: utf-8 -*-

"""
   Pinch.Models.Person
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel

class Person(BaseModel):

    """Implementation of the 'Person' model.

    TODO: type model description here.

    Attributes:
        firstname (string): TODO: type description here.
        lastname (string): TODO: type description here.
        home_phone_number (string): The landline phone number of the resident
            or manager
        mobile_phone_number (string): TODO: type description here.
        role (string): Caretaker, Resident, Manager, ThirdParty

    """

    def __init__(self, 
                 firstname = None,
                 lastname = None,
                 home_phone_number = None,
                 mobile_phone_number = None,
                 role = None):
        """Constructor for the Person class"""
        
        # Initialize members of the class
        self.firstname = firstname
        self.lastname = lastname
        self.home_phone_number = home_phone_number
        self.mobile_phone_number = mobile_phone_number
        self.role = role

        # Create a mapping from Model property names to API property names
        self.names = {
            "firstname": "firstname",
            "lastname": "lastname",
            "home_phone_number": "home_phone_number",
            "mobile_phone_number": "mobile_phone_number",
            "role": "role",
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
            firstname = dictionary.get("firstname")
            lastname = dictionary.get("lastname")
            home_phone_number = dictionary.get("home_phone_number")
            mobile_phone_number = dictionary.get("mobile_phone_number")
            role = dictionary.get("role")
            # Return an object of this model
            return cls(firstname,
                       lastname,
                       home_phone_number,
                       mobile_phone_number,
                       role)
