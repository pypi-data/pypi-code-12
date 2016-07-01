#!/usr/local/bin/python
# encoding: utf-8
"""
*Add and maintain sidebars, footers, headers and various listing pages in a gollum wiki*

:Author:
    David Young

:Date Created:
    June 10, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import codecs
import urllib
import re
import yaml
import operator
import collections
from titlecase import titlecase
from fundamentals import tools


class scaffold():
    """
    *Generate and maintain all of the scaffolding for gollum -- blogging workflow, listings, tag page etc*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        .. code-block:: python

            from bilbo import scaffold
            builder = scaffold(
                log=log,
                settings=settings
            )
            builder.get()
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'scaffold' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def get(self):
        """
        *Generate and maintain all of the scaffolding for gollum -- blogging workflow, listings, tag page etc*

        **Return:**
            - None
        """
        self.log.info('starting the ``get`` method')

        # FOR EACH WTED LOIKIIN THE SETTINGS FILE ...
        for name, wiki in self.settings["wikis"].iteritems():
            self.update_root_sidebar(
                rootDirectory=wiki["root"]
            )
            self.update_root_home_pages(
                rootDirectory=wiki["root"]
            )
            self.create_blog_listings(
                wikiRoot=wiki["root"]
            )
            self.create_tag_listings(
                wikiRoot=wiki["root"]
            )

        self.log.info('completed the ``get`` method')
        return

    def update_root_sidebar(
            self,
            rootDirectory):
        """*Add links to the gollum sidebar*

        **Key Arguments:**
            - ``rootDirectory`` -- path to the root of the wiki

        **Return:**
            - None

        **Usage:**

            .. code-block:: python

                from bilbo import scaffold
                fixer = scaffold(
                    log=log,
                    settings=settings
                )
                fixer.update_root_sidebar(
                    rootDirectory=wikiRootPath,
                )
        """
        self.log.info('starting the ``update_root_sidebar`` method')

        # LIST THE ROOT FOLDERS AS MARKDOWN LINKS
        content = ""
        basePath = rootDirectory
        for d in os.listdir(basePath):
            isDir = os.path.isdir(os.path.join(basePath, d))
            if isDir or d == "tags.md":

                # FOLDERS TO AVOID
                matched = False
                for avoid in self.settings["template parameters"]["folder avoid regex"]:
                    matchObject = re.search(
                        r"%(avoid)s" % locals(), d, re.S)
                    if matchObject:
                        matched = True
                if matched:
                    continue

                text = d.replace("-", " ").replace("_",
                                                   " ").replace(".md", "").upper()
                urlString = urllib.quote(d.replace(".md", ""))
                if isDir:
                    content += """[%(text)s](/%(urlString)s/Home)  \n""" % locals()
                else:
                    content += """[%(text)s](/%(urlString)s)  \n""" % locals()

        # ADD THE PROJECT HOME GOLLUM MACRO
        content += "<<ProjectHome()>>"

        # WRITE THE SIDEBAR FILE
        rootSidebar = rootDirectory + "/_Sidebar.md"
        pathToWriteFile = rootSidebar
        try:
            self.log.debug("attempting to open the file %s" %
                           (pathToWriteFile,))
            writeFile = codecs.open(
                pathToWriteFile, encoding='utf-8', mode='w')
        except IOError, e:
            message = 'could not open the file %s' % (pathToWriteFile,)
            self.log.critical(message)
            raise IOError(message)
        writeFile.write(content)
        writeFile.close()

        self.log.info('completed the ``update_root_sidebar`` method')
        return None

    def update_root_home_pages(
            self,
            rootDirectory):
        """*Add and update the catalogory pages in gollum wiki (root folders)*

        **Key Arguments:**
            - ``rootDirectory`` -- path to the root of the wiki

        **Return:**
            - None

        **Usage:**

            .. code-block:: python

                from bilbo import scaffold
                fixer = scaffold(
                    log=log,
                    settings=settings
                )
                fixer.update_root_home_pages(
                    rootDirectory=destinationWiki
                )
        """
        self.log.info('starting the ``update_root_home_pages`` method')

        # WALK THROUGH ROOT FOLDERS
        basePath = rootDirectory
        for rf in os.listdir(basePath):
            if os.path.isdir(os.path.join(basePath, rf)):

                # FOLDERS TO AVOID
                matched = False
                for avoid in self.settings["template parameters"]["folder avoid regex"]:
                    matchObject = re.search(
                        r"%(avoid)s" % locals(), rf, re.S)
                    if matchObject:
                        matched = True
                if matched:
                    continue

                # HOME PAGE CONTENTS -- USING GOLLUM MACROS
                thisFolder = os.path.join(basePath, rf)
                content = """---
footer: false
title: %(rf)s
blogged: false
toc: false
tags: false
---

<<ProjectPages("Pages",0)>>
<<Attachments("Adjacent Files",0)>>
<<SubFolders("Sub-Directories",0)>>
<<Thumbnails("Adjacent Images",0)>>

""" % locals()

                # WRITE OUT THE HOME PAGE
                home = thisFolder + "/Home.md"
                exists = os.path.exists(home)
                if exists:
                    continue
                pathToWriteFile = home
                try:
                    self.log.debug("attempting to open the file %s" %
                                   (pathToWriteFile,))
                    writeFile = codecs.open(
                        pathToWriteFile, encoding='utf-8', mode='w')
                except IOError, e:
                    message = 'could not open the file %s' % (pathToWriteFile,)
                    self.log.critical(message)
                    raise IOError(message)
                writeFile.write(content)
                writeFile.close()

        self.log.info('completed the ``update_root_home_pages`` method')
        return None

    def _get_blogging_workflow_pages(
            self,
            wikiRoot,
            rootDirectory=False,
            blogged={},
            donotblog={},
            undecided={},
            drafts={}):
        """*create blogging admin pages*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki
            - ``rootDirectory`` -- the root directory to start cleaning up metadata.
            - ``blogged`` -- current list of pages that have been blogged
            - ``donotblog`` -- current list of pages that will not be blogged
            - ``undecided`` -- current list of pages that have been blogged yet, but could be (undecided)

        **Return:**
            - ``blogged`` -- current list of pages that have been blogged -- appended to
            - ``donotblog`` -- current list of pages that will not be blogged -- appended to
            - ``undecided`` -- current list of pages that have been blogged yet, but could be (undecided) -- appended to
            - ``drafts`` -- draft blog post, have to be edited and cleaned before release

        """
        self.log.info('starting the ``_get_blogging_workflow_pages`` method')

        # RECURSIVELY CREATE MISSING DIRECTORIES
        if not os.path.exists(wikiRoot + "/admin"):
            os.makedirs(wikiRoot + "/admin")
            self.update_root_home_pages(rootDirectory=wikiRoot)

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
            if matched or d in ["projects", "scratch"]:
                continue

            if rootDirectory != wikiRoot and os.path.isfile(os.path.join(rootDirectory, d)):
                # FOR EVERY MARKDOWN FILE IN DIRECTORY - OPEN AND READ CONTENTS
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

                    # GRAB THE FRONTMATTER IN A DICTIONARY
                    currentFM = {}
                    if "---" in thisData[:4]:

                        reFM = re.compile(r'^---(.*?)---', re.S | re.M)
                        matchObject = reFM.match(thisData)
                        if matchObject:
                            currentFM = matchObject.group(1).strip()
                            currentFM = yaml.load(currentFM)
                        else:
                            self.log.error(
                                "No frontmatter matched in %(pathToReadFile)s" % locals())
                            continue

                    # ADD TO A LIST BASED ON THE `BLOGGED` KEY VALUE
                    try:
                        currentFM["title"] = titlecase(
                            currentFM["title"]).replace("-", " ")
                    except Exception, e:
                        # SOME ERROR IN YAML TITLE
                        thisError = str(e)
                        self.log.error(
                            "%(thisError)s: %(pathToReadFile)s" % locals())
                        continue
                    if "blogged" not in currentFM:
                        path = os.path.join(rootDirectory, d)
                        self.log.warning(
                            "`%(path)s` page has no `blogged:` frontmatter key" % locals())
                    elif (currentFM["blogged"] == None or currentFM["blogged"] == "None") and d.lower() != "home.md":
                        undecided[os.path.join(rootDirectory, d).replace(
                            wikiRoot, "").replace(".md", "")] = currentFM["title"]
                    elif currentFM["blogged"] == False:
                        donotblog[os.path.join(rootDirectory, d).replace(
                            wikiRoot, "").replace(".md", "")] = currentFM["title"]
                    elif currentFM["blogged"] == True:
                        blogged[os.path.join(rootDirectory, d).replace(
                            wikiRoot, "").replace(".md", "")] = currentFM["title"]
                    elif currentFM["blogged"].lower() == "draft":
                        drafts[os.path.join(rootDirectory, d).replace(
                            wikiRoot, "").replace(".md", "")] = currentFM["title"]

            # RECURSE INTO SUB-FOLDERS
            if os.path.isdir(os.path.join(rootDirectory, d)):
                (blogged, donotblog, undecided, drafts) = self._get_blogging_workflow_pages(
                    wikiRoot=wikiRoot,
                    rootDirectory=os.path.join(rootDirectory, d),
                    blogged=blogged,
                    donotblog=donotblog,
                    undecided=undecided,
                    drafts=drafts
                )

        self.log.info('completed the ``_get_blogging_workflow_pages`` method')
        return (blogged, donotblog, undecided, drafts)

    def create_blog_listings(
            self,
            wikiRoot):
        """*Create listings of blogged, undecided and never to be blogged pages in gollum wiki*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki

        **Return:**
            - None

        **Usage:**

            .. code-block:: python 

                from bilbo import scaffold
                fixer = scaffold(
                    log=log,
                    settings=settings
                )
                fixer.create_blog_listings(
                    wikiRoot=wikiRootPath
                )
        """
        self.log.info('starting the ``create_blog_listings`` method')

        # GET 3 DICTIONARIES OF ALL THE BLOGGING WORKFLOW LISTS
        (blogged, donotblog, undecided, drafts) = self._get_blogging_workflow_pages(
            wikiRoot=wikiRoot,
            blogged={},
            donotblog={},
            undecided={},
            drafts={}
        )

        # PAGE TITLES
        pages = [
            "Potential Blog Posts",
            "Blogged Pages",
            "Non-Blog Pages",
            "Draft Blog Posts"
        ]

        # FOR EACH LIST, PRINT THE PAGE IN ADMIN FOLDER
        for p, l in zip(pages, [undecided, blogged, donotblog, drafts]):
            l = sorted(l.items(), key=operator.itemgetter(1))
            content = """---
footer: false
title: %(p)s
blogged: false
toc: false
tags: false
---

""" % locals()

            # CREATE MARKDOWN LINK LIST
            for post in l:
                v = post[1]
                k = post[0]
                urlString = urllib.quote(k)
                k = post[0].split("/")
                if len(k) > 2:
                    k = ("/").join(k[:-1])
                    k = k[1:] + "/"
                else:
                    k = k[1]
                content += """[%(v)s](%(urlString)s "%(k)s")  \n""" % locals()

            # WRITE THE FILE TO DISK
            p = p.replace(" ", "-")
            pathToWriteFile = wikiRoot + "/admin/%(p)s.md" % locals()
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToWriteFile,))
                writeFile = codecs.open(
                    pathToWriteFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToWriteFile,)
                self.log.critical(message)
                raise IOError(message)
            writeFile.write(content)
            writeFile.close()

        self.log.info('completed the ``create_blog_listings`` method')
        return None

    def _get_all_wiki_tags(
            self,
            wikiRoot,
            rootDirectory=False,
            tags={},
            untagged={}
    ):
        """*create blogging admin pages*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki
            - ``rootDirectory`` -- the root directory to start cleaning up metadata.
            - ``tags`` -- a dictionary of tag name keys and list of pages as values
            - ``untagged`` -- untagged pages

        **Return:**
            - ``tags`` -- a dictionary of tag name keys and list of pages as values -- appended to
        """
        self.log.info('starting the ``_get_all_wiki_tags`` method')

        # RECURSIVELY CREATE MISSING DIRECTORIES
        if not os.path.exists(wikiRoot + "/admin"):
            os.makedirs(wikiRoot + "/admin")
            self.update_root_home_pages(rootDirectory=wikiRoot)

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

            addToUntagged = True
            if "/projects" in rootDirectory or "/scratch" in rootDirectory or d.lower() == "home.md":
                addToUntagged = False

            if rootDirectory != wikiRoot and os.path.isfile(os.path.join(rootDirectory, d)):
                # FOR EVERY MARKDOWN FILE IN DIRECTORY - OPEN AND READ CONTENTS
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

                    # GRAB THE FRONTMATTER IN A DICTIONARY
                    currentFM = {}
                    if "---" in thisData[:4]:
                        reFM = re.compile(r'^---(.*?)---', re.S | re.M)
                        matchObject = reFM.match(thisData)
                        if matchObject:
                            currentFM = matchObject.group(1).strip()
                            currentFM = yaml.load(currentFM)

                    # ADD TO A LIST BASED ON THE `BLOGGED` KEY VALUE
                    if "title" in currentFM:
                        currentFM["title"] = titlecase(
                            currentFM["title"]).replace("-", " ")
                        if "tags" not in currentFM or currentFM["tags"] == None or currentFM["tags"] == "None":
                            if addToUntagged == True:
                                untagged[os.path.join(rootDirectory, d).replace(
                                    wikiRoot, "").replace(".md", "")] = currentFM["title"]
                        elif currentFM["tags"] != False and currentFM["tags"] != "None":
                            theseTags = str(
                                currentFM["tags"]).strip().split(" ")
                            for t in theseTags:
                                t = t.replace(",", "").strip()
                                if t not in tags:
                                    tags[t] = {}
                                tags[t][os.path.join(rootDirectory, d).replace(
                                    wikiRoot, "").replace(".md", "")] = currentFM["title"]

            # RECURSE INTO SUB-FOLDERS
            if os.path.isdir(os.path.join(rootDirectory, d)):
                (tags, untagged) = self._get_all_wiki_tags(
                    wikiRoot=wikiRoot,
                    rootDirectory=os.path.join(rootDirectory, d),
                    tags=tags,
                    untagged=untagged
                )

        self.log.info('completed the ``_get_all_wiki_tags`` method')
        return (tags, untagged)

    def create_tag_listings(
            self,
            wikiRoot):
        """*Create listings of tags and untagged pages in gollum wiki*

        **Key Arguments:**
            - ``wikiRoot`` -- the root directory of the wiki

        **Return:**
            - None

        **Usage:**

            .. code-block:: python 

                from bilbo import scaffold
                fixer = scaffold(
                    log=log,
                    settings=settings
                )
                fixer.create_tag_listings(
                    wikiRoot=wikiRootPath
                )
        """
        self.log.info('starting the ``create_tag_listings`` method')

        # GET 2 DICTIONARIES OF ALL THE TAGGING WORKFLOW LISTS
        (tags, untagged) = self._get_all_wiki_tags(
            wikiRoot=wikiRoot,
            tags={},
            untagged={}
        )

        # PAGE TITLES
        pages = [
            "Untagged Posts"
        ]

        # FOR EACH LIST, PRINT THE PAGE IN ADMIN FOLDER
        for p, l in zip(pages, [untagged]):
            l = sorted(l.items(), key=operator.itemgetter(1))
            content = """---
footer: false
title: %(p)s
blogged: false
toc: false
tags: false
---

""" % locals()

            # CREATE MARKDOWN LINK LIST
            for post in l:
                v = post[1]
                k = post[0]
                urlString = urllib.quote(k)
                k = post[0].split("/")
                if len(k) > 2:
                    k = ("/").join(k[:-1])
                    k = k[1:] + "/"
                else:
                    k = k[1]
                content += """[%(v)s](%(urlString)s "%(k)s")  \n""" % locals()

            # WRITE THE FILE TO DISK
            p = p.replace(" ", "-")
            pathToWriteFile = wikiRoot + "/admin/%(p)s.md" % locals()
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToWriteFile,))
                writeFile = codecs.open(
                    pathToWriteFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToWriteFile,)
                self.log.critical(message)
                raise IOError(message)
            writeFile.write(content)
            writeFile.close()

        # THE TAG PAGE
        pages = [
            "tags"
        ]

        # FOR EACH LIST, PRINT THE PAGE IN ADMIN FOLDER
        for p, l in zip(pages, [tags]):

            otags = collections.OrderedDict(sorted(l.items()))
            content = """---
footer: false
title: %(p)s
blogged: false
toc: false
tags: false
---

""" % locals()

            # CREATE MARKDOWN LINK LIST
            for t, allPages in otags.iteritems():
                content += """\n### <a href="#%(t)s"><i class="fa fa-tag" aria-hidden="true"></i> %(t)s</a>  \n\n""" % locals(
                )
                allPages = sorted(allPages.items(), key=operator.itemgetter(1))
                for post in allPages:
                    v = post[1]
                    urlString = urllib.quote(post[0])
                    k = post[0].split("/")
                    if len(k) > 2:
                        k = ("/").join(k[:-1])
                        k = k[1:] + "/"
                    else:
                        k = k[1]

                    content += """- [%(v)s](%(urlString)s "%(k)s")  \n""" % locals()

            # WRITE THE FILE TO DISK
            p = p.replace(" ", "-")
            pathToWriteFile = wikiRoot + "/%(p)s.md" % locals()
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToWriteFile,))
                writeFile = codecs.open(
                    pathToWriteFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToWriteFile,)
                self.log.critical(message)
                raise IOError(message)
            writeFile.write(content)
            writeFile.close()

        self.log.info('completed the ``create_tag_listings`` method')
        return None
    # use the tab-trigger below for new method
    # xt-class-method
