#!/usr/local/bin/python
# encoding: utf-8
"""
*Add projects from wikis to taskpaper files to keep track of project tasks*

:Author:
    David Young

:Date Created:
    June  6, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import urllib
import re
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class tasks():
    """
    *Add projects from wikis to taskpaper files to keep track of project tasks*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        .. code-block:: python

            from bilbo import tasks
            this = tasks(
                log=log,
                settings=settings
            )
            this.get()
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,
    ):
        self.log = log
        log.debug("instansiating a new 'tasks' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def get(self):
        """

        **Return:**
            - None
        """
        self.log.info('starting the ``get`` method')

        for name, wiki in self.settings["wikis"].iteritems():
            print "Updating %(name)s wiki tasks" % locals()
            taskpaperPath = wiki["taskpaper"]
            projectDir = wiki["root"] + "/projects"
            rootUrl = wiki["baseurl"]
            email = wiki["email"]
            self._populate_taskpaper_files(
                taskpaperPath=taskpaperPath,
                projectDirectory=projectDir,
                baseUrl=rootUrl,
                email=email
            )

        self.log.info('completed the ``get`` method')
        return None

    def _populate_taskpaper_files(
            self,
            taskpaperPath,
            projectDirectory,
            baseUrl,
            email):
        """*populate taskpaper files*

        **Key Arguments:**
            - ``taskpaperPath`` -- path to the taskpaper file.
            - ``projectDirectory`` -- path to the wiki project directory.
            - ``baseUrl`` -- the root url of the wiki.
            - ``email`` -- email address associated with the wiki.
        """
        self.log.info('starting the ``_populate_taskpaper_files`` method')

        # READ DATA FROM PROJECTS FILE
        import codecs
        pathToReadFile = taskpaperPath
        try:
            self.log.debug("attempting to open the file %s" %
                           (pathToReadFile,))
            readFile = codecs.open(
                pathToReadFile, encoding='utf-8', mode='r')
            projectData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            self.log.warning(message)
            projectData = "Inbox:\n"

        # COMBINE WITH DATA FROM SOMEDAY FILE (IF IT EXISTS)
        taskpaperData = projectData
        startProjectData = projectData
        pathToReadFile = taskpaperPath.replace("projects", "someday")
        try:
            self.log.debug("attempting to open the file %s" %
                           (pathToReadFile,))
            readFile = codecs.open(
                pathToReadFile, encoding='utf-8', mode='r')
            somedayData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            self.log.warning(message)
            somedayData = "Inbox:\n"
        taskpaperData = taskpaperData + somedayData

        # FIND NEW PORJECTS TO ADD TO TASKPAPER
        basePath = projectDirectory
        for d in os.listdir(projectDirectory):
            if os.path.isdir(os.path.join(basePath, d)) and "_archive" not in d.lower():
                projectName = d.replace(
                    "-", " ").replace("_", " ").replace("  ", " ").replace("  ", " ").title() + ":"

                # ADD PROJECT TITLE, FINDER AND GOLLUM LINKS TO TASKPAPER
                dryxReveal = "dryx-reveal://" + urllib.quote("%(projectDirectory)s/%(d)s" % locals(
                ))
                gollumLink = "%(baseUrl)s/projects/%(d)s/Home" % locals()
                emailEncode = urllib.quote(email)
                mailProjectName = urllib.quote(d.replace(
                    "-", " ").replace("_", " ").replace("  ", " ").replace("  ", " ").title())
                mailplane = "mailplane://%(emailEncode)s/#label/projects%%2F%(mailProjectName)s" % locals()
                enLink = "dryx-en://" + urllib.quote(d.replace(
                    "-", " ").replace("_", " ").replace("  ", " ").replace("  ", " "))
                if projectName.lower() not in taskpaperData.lower():
                    projectData += """

%(projectName)s
    %(dryxReveal)s
    %(gollumLink)s
    %(mailplane)s
    %(enLink)s 
""" % locals()
                else:
                    # ADD SUPPLIMENTARY LINKS IF THEY DON"T EXIST
                    for link in [dryxReveal, gollumLink, mailplane, enLink]:
                        if link not in projectData:
                            # print '^(%(projectName)s.*?)' % locals()
                            regex = re.compile(
                                r'(%(projectName)s.*?\n)' % locals(), re.I)
                            thisIter = regex.finditer(projectData)
                            for item in thisIter:
                                this = item.group()
                            projectData = regex.sub(
                                "\g<1>\t%(link)s\n" % locals(), projectData, count=1)

        # WRITE NEW FILE IF EXTRA PROJECTS/DATA HAS BEEN ADDED
        if startProjectData != projectData:
            pathToWriteFile = taskpaperPath
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToWriteFile,))
                writeFile = codecs.open(
                    pathToWriteFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToWriteFile,)
                self.log.critical(message)
                raise IOError(message)

            writeFile.write(projectData)
            writeFile.close()

        self.log.info('completed the ``_populate_taskpaper_files`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
