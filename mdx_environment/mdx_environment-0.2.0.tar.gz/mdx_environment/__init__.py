##
# BSD 3-clause licence
#
# Copyright (c) 2015, Andrew Robinson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the names of python-md-environment AND/OR mdx_environment nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

'''
A python markdown extension which creates sections of output that can be changed based on Environment Variables

Adds tags (latex style)

\env{ENVVAR}
\env{ENVVAR}{OPERATOR}

where OPERATOR is:
- lower: e.g. hello world
- upper: e.g. HELLO WORLD
- title: e.g. Hello World
- sentence: e.g. Hello world
- default: i.e. left unchanged, which is default operation

....

\ifdef{ENVVAR OPER VALUE}

\endifdef

where OPER:
- 

....

\if{ENVVAR}{VALUE}

\elif{ENVVAR}{VALUE2}

\else

\endif

Created on 21/09/2015
@author: Andrew Robinson
'''

from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import markdown
from markdown.blockprocessors import BlockProcessor, ListIndentProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import os
import re

## Following line updated by util/set-version script, DO NOT EDIT
__version__ = '0.2.0'


# Add warning that the environment might not be loaded
if "_MD_ENV_LOADED_" not in os.environ:
    import logging
    log = logging.getLogger("mkdocs.mdx_environment")
    log.warn("_MD_ENV_LOADED_ environment variable not set when using the mdx_environment extension.  Did you forget to source the environment file?")
    log.info("Maybe you want to run 'source enviro/defaults.sh' or one of the other '.sh' files in 'enviro/'")


################
## \env{} tag

ENVPATTERN1 = r'\\env{(?P<env>[^}]*)}({(?P<oper>[^}]*)})?'
ENVPATTERN2 = r'\\env\[(?P<env>[^}]*)\](\[(?P<oper>[^}]*)\])?'

class EnvironmentPattern(Pattern):
    
    '''Inserts the value of environment variable into the output with the \env{ENVVAR} tag'''
    
    _id = 0
    
    def handleMatch(self, m):
        
        matchVars = m.groupdict()
        
        # get my id
        myid = self._id
        self._id += 1
        
        # compute values
        val = os.environ.get(matchVars['env'])
        oper = matchVars.get('oper', '')
        if oper is None:
            oper = ""
        oper = oper.lower()
        if val is None:
            val = ""
        if oper == 'upper':
            val = val.upper()
        elif oper == 'lower':
            val = val.lower()
        elif oper == 'title':
            val = val.title()
        elif oper == 'sentence':
            val = val.lower()
            if len(val) > 0:
                val = val[0].upper() + val[1:]
        #end if
        
        # make the output
        spanenv = etree.Element('span')
        spanenv.set("id", "env%s" % (myid, ))
        spanenv.set("class", "environment_env")
        spanenv.text = val
        
        return spanenv

class ElementProcessor(BlockProcessor):
    '''Produces an element with MD content'''
    
    REStart = re.compile(r'^(?P<pre>.*)\\element{(?P<name>[a-zA-Z][^}]*)}(?P<post>.*)$',re.DOTALL)
    REEnd = re.compile(r'^(?P<pre>.*)\\endelement(?P<post>.*)$',re.DOTALL)
     
    def test(self, parent, block):
        return bool(self.REStart.search(block)) or bool(self.REEnd.search(block))

    def run(self, parent, blocks):
        raw_block = blocks.pop(0)
        matchStart = self.REStart.search(raw_block)
        if matchStart is not None:
            matchVars = matchStart.groupdict()
            
            # check for children
            myblocks = self._removeUntilMatching(blocks)
            
            # make the element
            self.parser.parseBlocks(parent, [matchVars['pre']])
            
            elm = etree.SubElement(parent, matchVars['name'])
            
            # add children
            self.parser.parseBlocks(elm, myblocks)
             
    def _removeUntilMatching(self, blocks):
         
        myblocks = []
        depth = 1
        while len(blocks) > 0:
            raw_block = blocks.pop(0)
            matchStart = self.REStart.search(raw_block)
            matchEnd = self.REEnd.search(raw_block)
            if matchStart is not None:
                depth += 1
            elif matchEnd is not None:
                if matchEnd.groupdict()['pre'] != "": #.strip()
                    myblocks.append(matchEnd.groupdict()['pre']) # .strip()
                if matchEnd.groupdict()['post'] != "": #.strip()
                    blocks.insert(0, matchEnd.groupdict()['post']) #.strip()
                depth -= 1
                if depth <= 0:
                    break
            # endif
             
            myblocks.append(raw_block)
        # next block
         
        return myblocks


class EnvironmentIfProcessor(BlockProcessor):
    """Create sections of output that can be changed based on Environment Variables"""
    
    REIfStart = re.compile(r'^(?P<pre>.*)\\if{(?P<env>[a-zA-Z!]\w*?)(\s*(?P<op>[<>!=]+)\s*(?P<val>[^}]*))?}(?P<post>.*)$',re.DOTALL)
    REIfEnd = re.compile(r'^(?P<pre>.*)\\endif(?P<post>.*)$',re.DOTALL)
    
    _id = 0
    _first = True
     
    def test(self, parent, block):
        return bool(self.REIfStart.search(block)) or bool(self.REIfEnd.search(block))
     
    def run(self, parent, blocks):
        raw_block = blocks.pop(0)
        matchStart = self.REIfStart.search(raw_block)
        if matchStart is not None:
            matchVars = matchStart.groupdict()
            
            # get my id
            myid = self._id
            self._id += 1
            
            # push the rest back into queue for processing
            inline = False
            if matchVars['post'] != "" and matchVars['post'] is not None:
                inline = self._isInline(matchVars['post'])
                blocks.insert(0, matchVars['post'])
            
            # check for children
            myblocks = self._removeUntilMatching(blocks)
            
            # check if the value should be displayed
            show = False
            envName = matchVars['env'].strip()
            envVal = os.environ.get(envName)
            
            if matchVars['op'] is not None and matchVars['op'] != "":
                op = matchVars['op'].strip()
                if op == "==":
                    show = envVal == matchVars['val']
                elif op == "!=":
                    show = envVal != matchVars['val']
                elif op in (">=", ">", "<", "<="):
                    try:
                        envVal = float(envVal)
                    except:
                        envVal = 0.0
                    try:
                        val = float(matchVars['val'])
                    except:
                        val = 0.0
                    
                    if op == ">=":
                        show = op >= val
                    elif op == "<=":
                        show = op <= val
                    elif op == ">":
                        show = op > val
                    elif op == "<":
                        show = op < val
            elif envName is not None and envName != "":
                if envName.lstrip().startswith("!"):
                    envName = envName[1:]
                    envVal = os.environ[envName]
                    show = envName not in os.environ or envVal.strip().lower() in ("0", "", "false", "f", "no", "n")
                else:
                    show = envName in os.environ and envVal.strip().lower() not in ("0", "", "false", "f", "no", "n")
            else:
                import logging
                log = logging.getLogger("mkdocs.mdx_environment")
                log.error("Missing environment variable name")
            
            # construct me if necessary
            if inline:
                b = blocks.pop(0)
                if show:
                    mb = myblocks.pop(0)
                    b = matchVars['pre'] + mb + b
                    blocks.insert(0, b)
                else:
                    b = matchVars['pre'] + b
                    blocks.insert(0, b)
            else:
                if show:
                    self.parser.parseBlocks(parent, [matchVars['pre']])
                    
                    elm = etree.SubElement(parent, 'div')
                    elm.set("id", "ifenv%s" % (myid, ))
                    elm.set("class", "environment_if")
                    
                    # add children
                    self.parser.parseBlocks(elm, myblocks)
                else:
                    blocks.insert(0,matchVars['pre'])
                
            # endif
            
        # endif
    # end run()
             
    def _removeUntilMatching(self, blocks):
         
        myblocks = []
        depth = 1
        while len(blocks) > 0:
            raw_block = blocks.pop(0)
            matchStart = self.REIfStart.search(raw_block)
            matchEnd = self.REIfEnd.search(raw_block)
            if matchStart is not None:
                depth += 1
            elif matchEnd is not None:
                if matchEnd.groupdict()['pre'] != "": #.strip()
                    myblocks.append(matchEnd.groupdict()['pre']) # .strip()
                if matchEnd.groupdict()['post'] != "": #.strip()
                    blocks.insert(0, matchEnd.groupdict()['post']) #.strip()
                depth -= 1
                if depth <= 0:
                    break
            # endif
             
            myblocks.append(raw_block)
        # next block
         
        return myblocks
    
    def _isInline(self, str):
        blocks = [str]
        depth = 1
        while len(blocks) > 0:
            raw_block = blocks.pop(0)
            matchStart = self.REIfStart.search(raw_block)
            matchEnd = self.REIfEnd.search(raw_block)
            if matchStart is not None:
                if matchStart.groupdict()['post'] != "": #.strip()
                    blocks.insert(0, matchStart.groupdict()['post'].strip())
                depth += 1
            elif matchEnd is not None:
                if matchEnd.groupdict()['post'] != "": #.strip()
                    blocks.insert(0, matchEnd.groupdict()['post'].strip())
                depth -= 1
                if depth <= 0:
                    return True
            # endif
        # next block
         
        return False
# end EnvironmentIfProcessor


class EnvironmentExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of EnvironmentExtension to BlockParser. """
        md.parser.blockprocessors.add('environment', EnvironmentIfProcessor(md.parser), '_begin')
        md.parser.blockprocessors.add('element', ElementProcessor(md.parser), '_begin')
        md.inlinePatterns.add('environmentpattern1', EnvironmentPattern(ENVPATTERN1), '_begin')
        md.inlinePatterns.add('environmentpattern2', EnvironmentPattern(ENVPATTERN2), '_begin')
        
        
def makeExtension(*args, **kwargs):
    return EnvironmentExtension(*args, **kwargs)




