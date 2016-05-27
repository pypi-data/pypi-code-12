# -*- coding: utf-8 -*-
import glob
import os

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]

__doc__ = """
Relatively simplistic configuration file loader, parser, and writer.

Has the ability to cross-link sections and load into completely de-serialized
Python dictionaries.

Example of configuration format:

.. code-block:: ini

    ; filename: example.ini

    [server]
    address = 127.0.0.1
    port = 1234

    [default_route]
    uri = /
    controller = example_project.views.ExampleView

    [static_content]
    uri = /other_place
    content = +url:https://maio.me/~pirogoeth/VIRUS.txt

    [file_content]
    uri = /another_place
    content = +file:/var/data/content.txt

    [routes]
    routes = +list:["@default_route"]

Usage:

.. code-block:: python

    from malibu.config import configuration
    conf = configuration.Configuration()
    conf.load("example.ini")

    # Grab a section
    srv_opts = conf.get_section("server")

    # Iterate over sections
    for section in conf.sections:
        # do section...
        pass

    # Add a section
    data = {
        "value": "abc",
        "num": 123
    }

    conf.add_section("test", data)
    conf.add_section("test2", data)

    # Remove a section
    conf.remove_section("test2")

    # Save the changed configuration
    conf.save()

    # Or, save to a new file
    conf.save(filename = "/var/data/config2.ini")

.. automodule:: malibu.config.configuration
   :members:

"""
