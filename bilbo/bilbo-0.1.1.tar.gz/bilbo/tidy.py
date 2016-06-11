#!/usr/local/bin/python
# encoding: utf-8
"""
*Tidy up the gollum wiki, updating lists, sidebars, footer, headers, cleaning filenames and md metadata. And more.*

:Author:
    David Young

:Date Created:
    June  8, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import re
import shutil
import random
import codecs
import yaml
import StringIO
from titlecase import titlecase
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class tidy():
    """
    *Tidy up gollum wiki(s) by cleaning filenames, removing cruft, fixing metadata etc*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To trigger all of the tidy methods in one go:

        .. code-block:: python

            from bilbo import tidy
            scrubber = tidy(
                log=log,
                settings=settings
            )
            scrubber.get()
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'tidy' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def get(self):
        """
        *trigger the tidy object*

        **Return:**
            - None
        """
        self.log.info('starting the ``get`` method')

        # FOR EACH WTED LOIKIIN THE SETTINGS FILE ...
        for name, wiki in self.settings["wikis"].iteritems():
            projectDir = wiki["root"] + "/projects"
            self.clean_filenames(
                rootFolder=wiki["root"]
            )
            self._remove_projector_cruft(
                directoryPath=projectDir,
            )
            self.clean_markdown_metadata(
                wikiRoot=wiki["root"]
            )
            self.add_excerpt_marker(
                rootDirectory=wiki["root"]
            )

        self.log.info('completed the ``get`` method')
        return tidy

    def clean_filenames(
            self,
            rootFolder):
        """*Cleanup preexisting wiki file and folder names*

        **Key Arguments:**
            - ``rootFolder`` -- path to the root directory within which to recursively clean.

        **Return:**
            - None

        **Usage:**

            .. code-block:: python

                from bilbo import tidy
                scrubber = tidy(
                    log=log,
                    settings=settings
                )
                scrubber.clean_filenames(
                    rootFolder=pathToWiki
                )
        """
        self.log.info('starting the ``clean_filenames`` method')

        # FOR EVERY FILE/FOLDER IN THE DIRECTORY CLEAN UP THE FILENAME
        for d in os.listdir(rootFolder):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue

            if " " in d:
                source = os.path.join(rootFolder, d)
                destination = os.path.join(rootFolder, d.replace(" ", "-"))
                exists = os.path.exists(destination)
                if not exists:
                    try:
                        self.log.debug("attempting to rename file %s to %s" %
                                       (source, destination))
                        shutil.move(source, destination)
                        print "Renamed `%(d)s` file/folder" % locals()
                    except Exception, e:
                        self.log.error("could not rename file/folder %s to %s - failed with this error: %s " %
                                       (source, destination, str(e),))
                elif os.path.isdir(source) and len(os.listdir(source)) == 0:
                    os.rmdir(source)
                else:
                    self.log.warning(
                        "could not rename file/folder %(source)s to %(destination)s - as the destination already exists" % locals())

        # RUN RECURSIVELY ON THE SUBFOLDERS
        for d in os.listdir(rootFolder):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue

            if os.path.isdir(os.path.join(rootFolder, d)):
                self.clean_filenames(
                    rootFolder=os.path.join(rootFolder, d)
                )

        self.log.info('completed the ``clean_filenames`` method')
        return None

    def _remove_projector_cruft(
            self,
            directoryPath):
        """*Remove extra files added by projector tool*

        **Key Arguments:**
            - ``directoryPath`` -- directory out of which to delete the projector files.

        **Return:**
            - None
        """
        self.log.info('starting the ``_remove_projector_cruft`` method')

        for d in os.listdir(directoryPath):
            if ".remove" in d:
                os.remove(os.path.join(directoryPath, d))
            else:
                pass

        self.log.info('completed the ``_remove_projector_cruft`` method')
        return None

    def clean_markdown_metadata(
            self,
            wikiRoot,
            rootDirectory=False):
        """*clean up the markdown metadata in all MD files*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki
            - ``rootDirectory`` -- the root directory to start cleaning up metadata.

        **Return:**
            - None

        **Usage:**

            .. code-block:: python

                from bilbo import tidy
                scrubber = tidy(
                    log=log,
                    settings=settings
                )
                scrubber.clean_markdown_metadata(
                    wikiRoot=pathToMyWiki
                )
        """
        self.log.info('starting the ``clean_markdown_metadata`` method')

        # THE DEFAULT FRONT MATTER
        defaultFM = self.settings["default frontmatter"]

        if rootDirectory == False:
            rootDirectory = wikiRoot

        # DETERMINE CATEGORY
        category = rootDirectory.replace(wikiRoot, "")
        if len(category) == 0:
            category = False
        else:
            if category[0] == "/":
                category = category[1:]
            category = category.split("/")[0]

        for d in os.listdir(rootDirectory):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue

            # FOR EVERY MARKDOWN FILE IN DIRECTORY
            if d.split(".")[-1] in ["md", "mmd", "markdown"]:
                pathToReadFile = os.path.join(rootDirectory, d)
                try:
                    self.log.debug("attempting to open the file %s" %
                                   (pathToReadFile,))
                    readFile = codecs.open(
                        pathToReadFile, encoding='utf-8', mode='r')
                    thisData = readFile.read().strip()
                    readFile.close()
                except IOError, e:
                    message = 'could not open the file %s' % (
                        pathToReadFile,)
                    self.log.critical(message)
                    raise IOError(message)

                currentFM = {}
                if "---" in thisData[:4]:
                    reFM = re.compile(r'^---\s*?(.*?)\n---', re.S)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        currentFM = matchObject.group(1).strip()
                        currentFM = yaml.load(currentFM)

                # SET A RANDOM IMAGE FOR THE FEATURE IMAGE
                defaultFM["imagefeature"] = random.sample(
                    self.settings["imagefeature list"], 1)[0]

                # CLEAN UP CURRENT FRONT-MATTER, ADD MISSING KEYS
                changedFM = False
                for k, v in defaultFM.iteritems():
                    if k not in currentFM.keys():
                        changedFM = True
                        currentFM[k] = v

                if currentFM["title"] is None:
                    fileName = (".").join(
                        d.split(".")[:-1]).replace("-", " ").replace("_", " ")
                    currentFM["title"] = titlecase(fileName)

                if currentFM["title"] == "Home":
                    fileName = rootDirectory.split(
                        "/")[-1].replace("-", " ").replace("_", " ")
                    currentFM["title"] = titlecase(fileName) + " Home"

                # ADD A CATEGORY IF MISSING
                if currentFM["category"] is None and category is not False:
                    currentFM["category"] = category

                # CONVERT FRONTMATTER TO A STRING
                fakeFile = StringIO.StringIO()
                yaml.dump(currentFM, fakeFile, default_flow_style=False)
                currentFMString = fakeFile.getvalue().strip()
                fakeFile.close()
                currentFMString = "---\n%(currentFMString)s\n---" % locals()
                currentFMString = currentFMString.replace("null", "")

                # REPLACE OLD FRONT-MATTER IN FILE, OR ADD FRONT-MATTER WHERE
                # MISSING
                if changedFM:
                    if "---" in thisData[:4]:
                        reFM = re.compile(r'^---\s*?(.*?)\n---', re.S)
                        thisData = reFM.sub(currentFMString, thisData, count=1)
                    else:
                        thisData = currentFMString + "\n\n" + thisData
                    pathToWriteFile = os.path.join(rootDirectory, d)
                    try:
                        self.log.debug("attempting to open the file %s" %
                                       (pathToWriteFile,))
                        writeFile = codecs.open(
                            pathToWriteFile, encoding='utf-8', mode='w')
                    except IOError, e:
                        message = 'could not open the file %s' % (
                            pathToWriteFile,)
                        self.log.critical(message)
                        raise IOError(message)
                    writeFile.write(thisData)
                    writeFile.close()

        # CONTINUE TO WALK DOWN DIRECTORIES
        for d in os.listdir(rootDirectory):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue
            if os.path.isdir(os.path.join(rootDirectory, d)):

                self.clean_markdown_metadata(
                    wikiRoot=wikiRoot,
                    rootDirectory=os.path.join(rootDirectory, d)
                )

        self.log.info('completed the ``clean_markdown_metadata`` method')
        return None

    def add_excerpt_marker(
            self,
            rootDirectory):
        """*add excerpt marker*

        **Key Arguments:**
            - ``rootDirectory`` -- the root directory to start adding excerpt markers to MD file

        **Return:**
            - None

        **Usage:**

            .. code-block:: python 

                from bilbo import tidy
                scrubber = tidy(
                    log=log,
                    settings=settings
                )
                scrubber.add_excerpt_marker(
                    rootDirectory=pathToMyWiki
                )
        """
        self.log.info('starting the ``add_excerpt_marker`` method')

        marker = self.settings["excerpt marker"]

        for d in os.listdir(rootDirectory):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue

            # FOR EVERY MARKDOWN FILE IN DIRECTORY
            if d.split(".")[-1] in ["md", "mmd", "markdown"]:
                pathToReadFile = os.path.join(rootDirectory, d)
                try:
                    self.log.debug("attempting to open the file %s" %
                                   (pathToReadFile,))
                    readFile = codecs.open(
                        pathToReadFile, encoding='utf-8', mode='r')
                    thisData = readFile.read().strip()
                    readFile.close()
                except IOError, e:
                    message = 'could not open the file %s' % (
                        pathToReadFile,)
                    self.log.critical(message)
                    raise IOError(message)

                # SEARCH FILE FOR THE MARKER AND ADD IT IF MISSING
                if marker in thisData:
                    continue
                else:
                    reFM = re.compile(r'(^---\s*?(.*?)\n---)', re.S)
                    thisData = reFM.sub("\g<1>\n%(marker)s" %
                                        locals(), thisData, count=1)
                    pathToWriteFile = os.path.join(rootDirectory, d)
                    try:
                        self.log.debug("attempting to open the file %s" %
                                       (pathToWriteFile,))
                        writeFile = codecs.open(
                            pathToWriteFile, encoding='utf-8', mode='w')
                    except IOError, e:
                        message = 'could not open the file %s' % (
                            pathToWriteFile,)
                        self.log.critical(message)
                        raise IOError(message)
                    writeFile.write(thisData)
                    writeFile.close()

        # CONTINUE TO WALK DOWN DIRECTORIES
        for d in os.listdir(rootDirectory):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), d, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue
            if os.path.isdir(os.path.join(rootDirectory, d)):
                self.add_excerpt_marker(
                    rootDirectory=os.path.join(rootDirectory, d)
                )

        self.log.info('completed the ``add_excerpt_marker`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
