#!/usr/local/bin/python
# encoding: utf-8
"""
*Take pages that have been flagged to be posted as a Jekyll blog post, format them correctly and post them*

:Author:
    David Young

:Date Created:
    June 30, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import re
import shutil
from datetime import datetime, date, time
import codecs
import yaml
import StringIO
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class blog():
    """
    *Take pages that have been flagged to be posted as a Jekyll blog post, format them correctly and post them*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        .. code-block:: python 

            from bilbo import blog
            poster = blog(
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
        log.debug("instansiating a new 'blog' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def get(self):
        """
        *get the blog object*

        **Return:**
            - ``None``
        """
        self.log.info('starting the ``get`` method')

        # FOR EACH WTED LOIKIIN THE SETTINGS FILE ...
        for name, wiki in self.settings["wikis"].iteritems():
            self._send_flagged_pages_to_jekyll_posts(
                wikiRoot=wiki["root"]
            )

        self.log.info('completed the ``get`` method')
        return None

    def _send_flagged_pages_to_jekyll_posts(
            self,
            wikiRoot,
            rootDirectory=False):
        """*If a page has been marked with the name of a Jekyll blog in the ``blogged`` front-matter keyword value, then format and send to the posts folder.*

        **Key Arguments:**
             ``wikiRoot`` -- the root directory of the wiki
            - ``rootDirectory`` -- the root directory to start cleaning up metadata.

        **Return:**
            - ``None``
        """
        self.log.info(
            'starting the ``_send_flagged_pages_to_jekyll_posts`` method')

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

            # FOR EVERY MARKDOWN FILE IN DIRECTORY
            if d.split(".")[-1] in ["md", "mmd", "markdown"] and d.lower() != "home.md":
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

                # GRAB THE FRONT-MATTER
                currentFM = {}
                oldFM = ""
                if "---" in thisData[:10]:
                    reFM = re.compile(r'^---(.*?)---',  re.S | re.M)
                    matchObject = reFM.match(thisData)
                    if matchObject:
                        oldFM = matchObject.group().strip()
                        currentFM = matchObject.group(1).strip()
                        currentFM = yaml.load(currentFM)
                mdContent = thisData.replace(oldFM, "")

                # CHECK FOR BLOG FLAGS
                if "blogged" in currentFM and currentFM["blogged"] not in [True, False] and currentFM["blogged"].lower() not in ["none", "false", "true", "draft"]:

                    now = datetime.now()
                    # SCAN SETTINGS FOR BASEURL
                    blogUrl = False
                    blogPostDir = False
                    for sb in self.settings["blogs"]:
                        if sb == currentFM["blogged"]:
                            # DETERMINE DESTINATION INFO
                            basename = os.path.basename(rootDirectory)
                            blogUrl = self.settings["blogs"][sb][
                                "baseurl"] + now.strftime("/%Y/%m/%d/") + basename + "-index"
                            if "private" in currentFM and currentFM["private"]:
                                blogPostDir = self.settings[
                                    "blogs"][sb]["private directory"]
                            else:
                                blogPostDir = self.settings[
                                    "blogs"][sb]["post directory"]
                            if "http" not in blogUrl:
                                blogUrl = "http://" + blogUrl
                            blogPostFolderName = now.strftime(
                                "%Y-%m-%d-") + basename
                            currentFM["otherlocations"] = blogUrl
                            currentFM["blogged"] = True
                            currentFM["date"] = now.strftime(
                                "%Y-%m-%d %H:%M:%S")

                    for k, v in currentFM.iteritems():
                        if v == None:
                            currentFM[k] = "None"

                    if blogUrl:
                        # CONVERT FRONTMATTER TO A STRING
                        fakeFile = StringIO.StringIO()
                        yaml.dump(currentFM, fakeFile,
                                  default_flow_style=False)
                        currentFMString = fakeFile.getvalue().strip()
                        fakeFile.close()
                        currentFMString = "---\n%(currentFMString)s\n---" % locals()
                        currentFMString = currentFMString.replace("null", "")

                        # REPLACE OLD FRONT-MATTER IN FILE
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

                        # COPY FOLDER TO TMP
                        try:
                            shutil.rmtree("/tmp/" + blogPostFolderName)
                        except:
                            pass
                        shutil.copytree(
                            rootDirectory, "/tmp/" + blogPostFolderName)
                        try:
                            shutil.rmtree(
                                "/tmp/" + blogPostFolderName + "/non-wiki")
                            os.remove(
                                "/tmp/" + blogPostFolderName + "/Home.md")
                            os.remove(
                                "/tmp/" + blogPostFolderName + "/home.md")
                        except:
                            pass

                        # REMOVE INDEX FILE AND REMOVE CRUFT
                        try:
                            source = "/tmp/" + blogPostFolderName + "/" + d
                            destination = "/tmp/" + blogPostFolderName + "/index.md"
                            self.log.debug("attempting to rename file %s to %s" %
                                           (source, destination))
                            os.rename(source, destination)
                        except Exception, e:
                            self.log.error(
                                "could not rename file %s to %s - failed with this error: %s " % (source, destination, str(e),))
                            raise e

                        # MOVE TO JEKYLL
                        try:
                            source = "/tmp/" + blogPostFolderName
                            destination = blogPostDir + "/" + blogPostFolderName
                            self.log.debug("attempting to rename file %s to %s" %
                                           (source, destination))
                            os.rename(source, destination)
                        except Exception, e:
                            self.log.error(
                                "could not rename file %s to %s - failed with this error: %s " % (source, destination, str(e),))
                            raise e

                continue

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

                    self._send_flagged_pages_to_jekyll_posts(
                        wikiRoot=wikiRoot,
                        rootDirectory=os.path.join(rootDirectory, d)
                    )

        self.log.info(
            'completed the ``_send_flagged_pages_to_jekyll_posts`` method')
        return None

    # xt-class-method
