#!/usr/local/bin/python
# encoding: utf-8
"""
*Add template files and folders into new Gollum wiki projects and directories*

:Author:
    David Young

:Date Created:
    June  3, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import re
import shutil
os.environ['TERM'] = 'vt100'
from frankenstein import electric
from fundamentals import tools


class templates():
    """
    *Add template files and folders into new Gollum wiki projects and directories*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        .. code-block:: python 

            from bilbo import templates
            templates(
                log=log,
                settings=settings
            ).get() 

    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'templates' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def get(self):
        """
        *populate the wiki with template content*
        """
        self.log.info('starting the ``get`` method')

        pathToTemplate = os.path.dirname(
            __file__) + "/resources/project-template"

        # FOR EACH WTED LOIKIIN THE SETTINGS FILE ...
        for name, wiki in self.settings["wikis"].iteritems():
            projectDir = wiki["root"] + "/projects"
            self._add_project_template(
                directoryPath=wiki["root"],
                pathToTemplate=pathToTemplate
            )

        self.log.info('completed the ``get`` method')
        return templates

    def _add_project_template(
            self,
            directoryPath,
            pathToTemplate):
        """*Populate new projects in wiki with template files and folders*

        **Key Arguments:**
            - ``directoryPath`` -- path to the folder to populate with the tmeplate.
            - ``pathToTemplate`` -- path to the template to be used to populated the folder.
        """
        self.log.info('starting the ``_add_project_template`` method')

        # FOR EVERY DIRECTORY IN PROJECT ROOT
        for d in os.listdir(directoryPath):
            if os.path.isdir(os.path.join(directoryPath, d)):

                # FOLDERS TO AVOID
                matched = False
                for avoid in self.settings["template parameters"]["folder avoid regex"]:
                    matchObject = re.search(
                        r"%(avoid)s" % locals(), d, re.S)
                    if matchObject:
                        matched = True
                if matched:
                    continue

                # REMOVE SPACES FROM PROJECT FOLDERS
                if " " in d:
                    newD = d.replace(" ", "-")
                    source = os.path.join(directoryPath, d)
                    destination = os.path.join(directoryPath, newD)
                    exists = os.path.exists(destination)
                    if not exists:
                        try:
                            self.log.debug("attempting to rename file %s to %s" %
                                           (source, destination))
                            shutil.move(source, destination)
                        except Exception, e:
                            self.log.error("could not rename file %s to %s - failed with this error: %s " %
                                           (source, destination, str(e),))
                            sys.exit(0)
                    d = newD

                pathToDestination = os.path.join(directoryPath, d)
                self.settings["template parameters"]["fixed placeholders"][
                    "project_name"] = d.replace(" ", "-")
                # DUPLICATE SETTINGS INTO FRANKENSTEIN KEY
                self.settings["frankenstein"] = self.settings[
                    "template parameters"]

                # USE FRANKENSTEIN ELECTRIC TO POPULATE THE FOLDERS IN THE WIKI
                electric(
                    log=self.log,
                    pathToTemplate=pathToTemplate,
                    pathToDestination=pathToDestination,
                    settings=self.settings,
                    ignoreExisting=True
                ).get()

                # NOW WALK THROUGH SUB-FOLDERS
                pathToSubprojectTemplate = os.path.dirname(
                    __file__) + "/resources/sub-project-template"
                self._add_project_template(
                    directoryPath=pathToDestination,
                    pathToTemplate=pathToSubprojectTemplate
                )

        self.log.info('completed the ``_add_project_template`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
