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
                wikiRoot=wiki["root"],
                wikiName=name
            )
            self.add_excerpt_marker(
                rootDirectory=wiki["root"]
            )
            self.rename_markdownfile_files_to_metadata_title(
                rootDirectory=wiki["root"] + "/scratch"
            )
            self.move_files_to_category_folders(
                wikiRoot=wiki["root"]
            )
            self.move_single_category_files_into_dedicated_folder(
                wikiRoot=wiki["root"]
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
            wikiName,
            rootDirectory=False):
        """*clean up the markdown metadata in all MD files*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki
            - ``wikiName`` -- name of the wiki
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
                oldFM = ""
                if "---" in thisData[:10]:
                    reFM = re.compile(r'^---(.*?)---',  re.S | re.M)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        oldFM = matchObject.group().strip()
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

                if "category" in currentFM and " " in currentFM["category"]:
                    changedFM = True
                    currentFM["category"] = currentFM[
                        "category"].replace(" ", "-").lower()

                if currentFM["title"] is None or currentFM["title"] == "None":
                    fileName = (".").join(
                        d.split(".")[:-1]).replace("-", " ").replace("_", " ")
                    currentFM["title"] = titlecase(fileName)

                if currentFM["title"] == "Home":
                    fileName = rootDirectory.split(
                        "/")[-1].replace("-", " ").replace("_", " ")
                    currentFM["title"] = titlecase(fileName) + " Home"

                # ADD A CATEGORY IF MISSING
                if (currentFM["category"] is None or currentFM["category"] == "None") and category is not False and category not in ["projects", "scratch"]:
                    currentFM["category"] = category

                # ADD WIKINAME IF MISSING
                if (currentFM["wiki"] is None or currentFM["wiki"] == "None"):
                    currentFM["wiki"] = wikiName

                # FIND HASH TAGS IN MD CONTENT - CONVERT TO FRONTMATTER TAGS
                mdContent = thisData.replace(oldFM, "")
                matchObject = re.finditer(
                    r"##(\w(\w|\d)+)",
                    mdContent,
                    flags=re.S | re.M  # re.S
                )
                count = 1
                if currentFM["tags"] and currentFM["tags"] != "None":
                    currentFM["tags"] = str(currentFM["tags"])
                else:
                    currentFM["tags"] = None

                for t in matchObject:
                    changedFM = True
                    thisTag = str(t.group().replace("#", ""))
                    if thisTag and currentFM["tags"] and (thisTag.lower() not in currentFM["tags"].lower()):
                        currentFM["tags"] = currentFM["tags"] + ", " + thisTag
                    elif currentFM["tags"] == None:
                        currentFM["tags"] = thisTag
                    mdContent = mdContent.replace(str(t.group()), thisTag)

                matchObject = re.search(r":\s*\n", oldFM, re.S)
                if matchObject:
                    changedFM = True

                for k, v in currentFM.iteritems():
                    if v == None:
                        currentFM[k] = "None"

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
                    thisData = currentFMString + "\n\n" + mdContent
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
                    wikiName=wikiName,
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
                    reFM = re.compile(r'(^---(.*?)---)', re.S)
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

    def rename_markdownfile_files_to_metadata_title(
            self,
            rootDirectory):
        """*Rename markdown files to match the title in their metadata*

        **Key Arguments:**
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
                scrubber.rename_markdownfile_files_to_metadata_title(
                    rootDirectory=pathToMyWiki + "/scratch"
                )

        """
        self.log.info(
            'starting the ``rename_markdownfile_files_to_metadata_title`` method')

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

                # FIND CURRENT METADATA
                currentFM = {}
                if "---" in thisData[:4]:
                    reFM = re.compile(r'^---(.*?)---', re.S | re.M)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        currentFM = matchObject.group(1).strip()
                        currentFM = yaml.load(currentFM)
                else:
                    self.log.warning("NO METADATA for %(d)s" % locals())
                    continue

                if "title" not in currentFM:
                    self.log.warning(
                        "no title in metadata for %(d)s" % locals())
                    continue

                # MATCH FILENAME AND TITLE - RENAME FILE ON MISMATCH
                filename = (".").join(
                    d.split(".")[:-1]).lower().replace(" ", "-").replace("'", "")
                title = currentFM["title"]
                if title.lower().strip().replace("  ", " ").replace("  ", " ").replace(" ", "-").replace("'", "") != filename:
                    newfileName = title.lower().strip().replace("  ", " ").replace(
                        "  ", " ").replace(" ", "-").replace("'", "") + ".md"
                    source = pathToReadFile
                    destination = os.path.join(rootDirectory, newfileName)
                    self.log.info(
                        'renaming the file: %(filename)s to %(newfileName)s' % locals())
                    exists = os.path.exists(destination)
                    if exists:
                        self.log.warning(
                            'the file %(newfileName)s already exists - not renaming %(filename)s' % locals())
                        continue
                    else:
                        os.rename(source, destination)

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
                self.rename_markdownfile_files_to_metadata_title(
                    rootDirectory=os.path.join(rootDirectory, d)
                )

        self.log.info(
            'completed the ``rename_markdownfile_files_to_metadata_title`` method')
        return None

    def move_files_to_category_folders(
            self,
            wikiRoot,
            rootDirectory=False):
        """*Move files from projects and scratch areas whenever the category field has been added.*

        The file is moved from its current location to the matching root category folder.

        **Key Arguments:**
             ``wikiRoot`` -- the root directory of the wiki
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
                scrubber.move_files_to_category_folders(
                    wikiRoot=pathToMyWiki
                ) 
        """
        self.log.info('starting the ``move_files_to_category_folders`` method')

        if rootDirectory == False:
            rootDirectory = wikiRoot

        # DETERMINE ROOT FOLDER NAME
        rootFolderCategory = rootDirectory.replace(wikiRoot, "")
        if len(rootFolderCategory) == 0:
            rootFolderCategory = False
        else:
            if rootFolderCategory[0] == "/":
                rootFolderCategory = rootFolderCategory[1:]
            rootFolderCategory = rootFolderCategory.split("/")[0]

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
                fileName = (".").join(
                    d.split(".")[:-1]).replace(" ", "-")
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
                    self.log.warning(message)
                    continue

                currentFM = {}
                if "---" in thisData[:4]:
                    reFM = re.compile(r'^---(.*?)---', re.S | re.M)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        currentFM = matchObject.group(1).strip()
                        currentFM = yaml.load(currentFM)

                if "category" in currentFM:
                    currentFM["category"] = currentFM[
                        "category"].lower().replace(" ", "-")

                # MOVE TO NEW LOCATION IF CATEGORY KEYWORD SET
                if "category" in currentFM and currentFM["category"] and currentFM["category"].lower() != "none" and rootFolderCategory in ["projects", "scratch"]:
                    newCategory = currentFM["category"]

                    containingFolder = pathToReadFile.replace(
                        wikiRoot + "/" + rootFolderCategory + "/", "")
                    depth = len(containingFolder.split("/"))
                    if (rootFolderCategory == "scratch" and depth == 1) or (rootFolderCategory == "projects" and (depth == 1 or depth == 2)):
                        # Recursively create missing directories
                        container = wikiRoot + "/" + \
                            currentFM["category"] + "/" + fileName
                        if not os.path.exists(container):
                            os.makedirs(container)
                        os.rename(pathToReadFile, container + "/" + d)
                    elif (rootFolderCategory == "scratch" and depth > 1) or (rootFolderCategory == "projects" and depth > 2):
                        folderToMove = (
                            "/").join(pathToReadFile.split("/")[:-1])
                        # Recursively create missing directories
                        if not os.path.exists(wikiRoot + "/" + currentFM["category"]):
                            os.makedirs(wikiRoot + "/" + currentFM["category"])

                        destination = wikiRoot + "/" + \
                            currentFM["category"] + "/" + \
                            pathToReadFile.split("/")[-2]

                        try:
                            os.rename(folderToMove, destination)
                        except Exception, e:
                            error = str(e)
                            self.log.warning(
                                "can't move %(folderToMove)s to %(destination)s. Error; %(error)s, %(d)s " % locals())

        # CONTINUE TO WALK DOWN DIRECTORIES
        if os.path.exists(rootDirectory):

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

                    self.move_files_to_category_folders(
                        wikiRoot=wikiRoot,
                        rootDirectory=os.path.join(rootDirectory, d)
                    )

        self.log.info(
            'completed the ``move_files_to_category_folders`` method')
        return None

    def transfer_pages_between_wikis(
            self,
            wikiRoot,
            wikiName,
            rootDirectory=False):
        """*Transfer pages and folders between wikis if the wiki keyword points to another wiki and the category keywaords is set.*

        The file is moved from its current location to the matching root category folder of another wiki.

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki
            - ``wikiName`` -- name of the wiki
            - ``rootDirectory`` -- the root directory to start cleaning up metadata.

        **Return:**
            - None

        **Usage:**


            The method requires the name of the current wiki. Any markdown file with a ``wiki`` keyword value other than the current wiki name will be moved to another wiki (if it's details are found in the settings file)

            .. code-block:: python 

                from bilbo import tidy
                scrubber = tidy(
                    log=log,
                    settings=settings
                )
                scrubber.transfer_pages_between_wikis(
                    wikiRoot=pathToMyWiki,
                    wikiName="nameOfMyWiki"
                )
        """
        self.log.info('starting the ``transfer_pages_between_wikis`` method')

        if rootDirectory == False:
            rootDirectory = wikiRoot

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

            # DETERMINE ROOT FOLDER NAME
            rootFolderCategory = rootDirectory.replace(wikiRoot, "")
            if len(rootFolderCategory) == 0:
                rootFolderCategory = False
            else:
                if rootFolderCategory[0] == "/":
                    rootFolderCategory = rootFolderCategory[1:]
                rootFolderCategory = rootFolderCategory.split("/")[0]

            # FOR EVERY MARKDOWN FILE IN DIRECTORY
            if d.split(".")[-1] in ["md", "mmd", "markdown"]:
                pathToReadFile = os.path.join(rootDirectory, d)
                fileName = (".").join(
                    d.split(".")[:-1]).replace(" ", "-")
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
                    self.log.warning(message)
                    continue

                currentFM = {}
                if "---" in thisData[:4]:
                    reFM = re.compile(r'^---(.*?)---', re.S | re.M)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        currentFM = matchObject.group(1).strip()
                        currentFM = yaml.load(currentFM)

                # MOVE TO NEW LOCATION IF CATEGORY KEYWORD SET
                if "category" in currentFM and currentFM["category"] and "wiki" in currentFM and currentFM["wiki"] != wikiName and rootFolderCategory not in ["projects", "scratch"]:

                    if currentFM["wiki"].strip() not in self.settings["wikis"]:
                        thisWikiName = currentFM["wiki"]
                        self.log.warning(
                            'the wiki name %(thisWikiName)s is not found in the bilbo settings file' % locals())
                        continue

                    otherWikiRoot = self.settings["wikis"][
                        currentFM["wiki"].strip()]["root"]

                    wikiCategory = currentFM["category"]

                    containingFolder = pathToReadFile.replace(
                        wikiRoot + "/" + rootFolderCategory + "/", "")
                    depth = len(containingFolder.split("/"))
                    if depth == 1:
                        # Recursively create missing directories
                        container = otherWikiRoot + "/" + \
                            currentFM["category"] + "/" + fileName
                        if not os.path.exists(container):
                            os.makedirs(container)
                        os.rename(pathToReadFile, container + "/" + d)
                    else:
                        folderToMove = (
                            "/").join(pathToReadFile.split("/")[:-1])
                        # Recursively create missing directories
                        if not os.path.exists(otherWikiRoot + "/" + currentFM["category"]):
                            os.makedirs(otherWikiRoot + "/" +
                                        currentFM["category"])

                        destination = otherWikiRoot + "/" + \
                            currentFM["category"] + "/" + \
                            pathToReadFile.split("/")[-2]

                        try:
                            os.rename(folderToMove, destination)
                        except Exception, e:
                            error = str(e)
                            self.log.warning(
                                "can't move %(folderToMove)s to %(destination)s. Error; %(error)s, %(d)s " % locals())

        # CONTINUE TO WALK DOWN DIRECTORIES
        if os.path.exists(rootDirectory):

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

                    self.transfer_pages_between_wikis(
                        wikiRoot=wikiRoot,
                        wikiName=wikiName,
                        rootDirectory=os.path.join(rootDirectory, d)
                    )

        self.log.info('completed the ``transfer_pages_between_wikis`` method')
        return None

    def move_single_category_files_into_dedicated_folder(
            self,
            wikiRoot):
        """*move single category files into dedicated folder*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki

        **Return:**
            - None

        **Usage:**

            .. code-block:: python 

                from bilbo import tidy
                scrubber = tidy(
                    log=log,
                    settings=settings
                )
                scrubber.move_single_category_files_into_dedicated_folder(
                    wikiRoot=destinationWiki1
                )
        """
        self.log.info(
            'starting the ``move_single_category_files_into_dedicated_folder`` method')

        for category in os.listdir(wikiRoot):
            # FOLDERS TO AVOID
            matched = False
            for avoid in self.settings["template parameters"]["folder avoid regex"]:
                matchObject = re.search(
                    r"%(avoid)s" % locals(), category, re.S)
                if matchObject:
                    matched = True
            if matched:
                continue

            if os.path.isdir(os.path.join(wikiRoot, category)) and category not in ["projects", "scratch", "admin"]:
                thispath = os.path.join(wikiRoot, category)
                for d in os.listdir(thispath):
                    if os.path.isfile(os.path.join(thispath, d)) and d.split(".")[-1] in ["md", "mmd", "markdown"] and d.lower() != "home.md":
                        # Recursively create missing directories
                        newDir = thispath + "/" + (".").join(d.split(".")[:-1])
                        if not os.path.exists(newDir):
                            os.makedirs(newDir)
                        source = os.path.join(thispath, d)
                        destination = os.path.join(newDir, d)
                        try:
                            self.log.debug("attempting to rename file %s to %s" %
                                           (source, destination))
                            os.rename(source, destination)
                        except Exception, e:
                            self.log.error(
                                "could not rename file %s to %s - failed with this error: %s " % (source, destination, str(e),))

        return

        self.log.info(
            'completed the ``move_single_category_files_into_dedicated_folder`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
