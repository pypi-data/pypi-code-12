# -*- coding: utf-8 -*-

"""
   Pinch.Models.Ticket
 
   This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
"""
from Pinch.Models.BaseModel import BaseModel
from Pinch.Models.Person import Person
from Pinch.Models.Building import Building
from Pinch.Models.Unit import Unit
from Pinch.Models.Document import Document

class Ticket(BaseModel):

    """Implementation of the 'Ticket' model.

    TODO: type model description here.

    Attributes:
        id (string): TODO: type description here.
        name (string): TODO: type description here.
        description (string): TODO: type description here.
        contacts (list of Person): TODO: type description here.
        status (string): TODO: type description here.
        building (Building): TODO: type description here.
        unit (Unit): TODO: type description here.
        access (string): TODO: type description here.
        agency (string): TODO: type description here.
        manager (string): TODO: type description here.
        documents (list of Document): TODO: type description here.

    """

    def __init__(self, 
                 id = None,
                 name = None,
                 description = None,
                 contacts = None,
                 status = None,
                 building = None,
                 unit = None,
                 access = None,
                 agency = None,
                 manager = None,
                 documents = None):
        """Constructor for the Ticket class"""
        
        # Initialize members of the class
        self.id = id
        self.name = name
        self.description = description
        self.contacts = contacts
        self.status = status
        self.building = building
        self.unit = unit
        self.access = access
        self.agency = agency
        self.manager = manager
        self.documents = documents

        # Create a mapping from Model property names to API property names
        self.names = {
            "id": "id",
            "name": "name",
            "description": "description",
            "contacts": "contacts",
            "status": "status",
            "building": "building",
            "unit": "unit",
            "access": "access",
            "agency": "agency",
            "manager": "manager",
            "documents": "documents",
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
            description = dictionary.get("description")
            # Parameter is an array, so we need to iterate through it
            contacts = None
            if dictionary.get("contacts") != None:
                contacts = list()
                for structure in dictionary.get("contacts"):
                    contacts.append(Person.from_dictionary(structure))
            status = dictionary.get("status")
            building = Building.from_dictionary(dictionary.get("building"))
            unit = Unit.from_dictionary(dictionary.get("unit"))
            access = dictionary.get("access")
            agency = dictionary.get("agency")
            manager = dictionary.get("manager")
            # Parameter is an array, so we need to iterate through it
            documents = None
            if dictionary.get("documents") != None:
                documents = list()
                for structure in dictionary.get("documents"):
                    documents.append(Document.from_dictionary(structure))
            # Return an object of this model
            return cls(id,
                       name,
                       description,
                       contacts,
                       status,
                       building,
                       unit,
                       access,
                       agency,
                       manager,
                       documents)
