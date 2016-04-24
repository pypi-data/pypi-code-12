'''
Copyright 2015 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

from dsgnutils.utils import *

from dsgnutils.xgplReadOnly import g__gpl
from dsgnutils.xgplReadOnly import g__lgpl

class XGPL_FileType(object):
    def __init__(
        self,
        nom,
        signatures,
    ):
        self.nom=nom
        self.signatures=signatures
    def match(self,filename):
        ret=None
        for x in self.signatures:
            if re.match(x,filename):
                ret=self
                break
        return ret
    def conditionInput(self,lineLs):
        ret=' '.join(lineLs)
        ret=re.sub(r' +',' ',ret)
        return ret
    def pullShebang(self,ls):
        shebang=[]
        lines=[x for x in ls] #deep copy
        if lines and re.match(r'^\#\!',lines[0]):
            shebang=[lines.pop(0),'']
            while lines and not lines[0]:
                lines.pop(0)
        return (shebang,lines)
    def hasLicense(self,license,fullFileName):
        lineLs=readLines(fullFileName)
        (_,lineLs)=self.pullShebang(lineLs)
        lineLs=self.conditionInput(lineLs)
        match=re.match(license['regex'],lineLs)
        return True if match else False
    def mangleOutput(self,template,maxLen=g__pep8LineLen):
        paragraphs=[]
        os=0
        for (i,x) in enumerate(template[:-1]):
            if template[i]=='\n' and template[i+1]=='\n':
                para=re.sub('\n',' ',template[os:i])
                para=re.sub(' +',' ',para)
                para=' '.join([re.sub(r'\.$','. ',x) for x in para.split(' ')])
                paragraphs.append(para.strip())
                os=i+2
        paragraphs=paragraphs[1:]
        final=[]
        for para in paragraphs:
            aRR=para.split(' ')
            buckets=[]
            holder=''
            while 0!=len(aRR):
                word=aRR.pop(0)
                test='%s %s'%(holder,word) if holder else word
                if len(test)<maxLen:
                    holder=test
                else:
                    buckets.append(holder)
                    holder=word
            if holder:
                buckets.append(holder)
            final.append('%s\n'%('\n'.join(buckets)))
        final[-1]=final[-1][:-1]
        return final
    def writeLicense(self,license,fullFileName,author,proj):
        template=license['template'].format(TimeStamp().sys.year,author,proj)
        template=self.mangleOutput(template)
        fileContents=readLines(fullFileName)
        (shebang,fileContents)=self.pullShebang(fileContents)
        payload=shebang+template+['']+fileContents
        payload='\n'.join(payload)
        with open(fullFileName,'w') as f:
            f.write(payload)

class XGPL_ML(XGPL_FileType):
    def __init__(
        self,
        nom,
        signatures,
        begin,
        end
    ):
        super().__init__(nom,signatures)
        self.begin=begin
        self.end=end
    def conditionInput(self,lineLs):
        ret=super().conditionInput(lineLs)
        ret=re.sub(self.begin,'',ret,count=1)
        return ret[1:]
    def mangleOutput(self,template):
        template=[self.begin]+super().mangleOutput(template)+[self.end]
        return template

class XGPL_L(XGPL_FileType):
    def __init__(
        self,
        nom,
        signatures,
        line
    ):
        super().__init__(nom,signatures)
        self.line=line
    def conditionInput(self,lineLs):
        for (i,x) in enumerate(lineLs):
            lineLs[i]=re.sub(r'^%s'%(self.line),'',x).lstrip()
        ret=super().conditionInput(lineLs)
        return ret
    def mangleOutput(self,template):
        template=super().mangleOutput(
            template,
            maxLen=g__pep8LineLen-(len(self.line)+1)
        )
        for i in range(len(template)):
            aRR=template[i].split('\n')
            for j in range(len(aRR)):
                aRR[j]='%s %s'%(self.line,aRR[j]) if aRR[j] else self.line
            template[i]='\n'.join(aRR)
        return template

class XGPL_Text(XGPL_FileType):
    def __init__(
        self,
        nom,
        signatures,
    ):
        super().__init__(nom,signatures)

class XGPL_Ignore(XGPL_FileType):
    def __init__(
        self,
        nom,
        signatures,
    ):
        super().__init__(nom,signatures)
    def hasLicense(self,license,fullFileName):
        return True

fTs=[
    XGPL_Ignore(
        'xgpl definition',
        [
            '^LICENSE$',
            '^LICENSE.txt$',
        ]
    ),
    XGPL_Text('README',['^README$']),
    XGPL_L('gitignore',['^\.gitignore$'],'#'),
    XGPL_ML('python',['.*\.py$'],'\'\'\'','\'\'\''),
    XGPL_ML('bash',['.*\.sh$'],'<<LICENSE','LICENSE'),
    XGPL_ML('C',['.*\.c$'],'/*','*/'),
    XGPL_L('nasm',['.*\.asm$'],';'),
    XGPL_L('makefile',['^makefile$','^Makefile$'],'#'),
    XGPL_L('requirements.txt',['^requirements.txt$'],'#'),
    XGPL_Text('text',['.*\.txt$']),
    XGPL_L('coveragerc',['^\.coveragerc$'],'#'),
]

def mapFileType(arg):
    ret=None
    for x in fTs:
        if x.match(arg):
            ret=x
            break
    return ret

def writeXGPL_Stamps(license,author,program,fLs,exclusions,force):
    '''
        Offers to write xgpl for all known filetypes in git repo.  Add
        filetypes to fTs as you please.  XGPL_ML class has multiline comment
        type, XGPL_L has line comment type.  The base class XGPL_FileType
        assumes that no comment is required.
    '''
    verbose=True if not force else False
    for fullFileName in fLs:
        if verbose:
            print('CHECKING %s...'%(fullFileName),end='')
        fileName=fullFileName.split('/')[-1]
        typ=mapFileType(fileName)
        if None==typ:
            if verbose:
                print('UNRECOGNIZED TYPE...SKIPING...')
            continue
        if typ.hasLicense(license,fullFileName):
            if verbose:
                print('FOUND!')
        else:
            write=False
            if force:
                write=True
            else:
                if 'y'==input('MISSING! WRITE LICENSE? [y/any]: '):
                    write=True
            if write:
                typ.writeLicense(license,fullFileName,author,program)

def hasXGPL_Definition(
    license,
    fLs,
    exclusions,
    force,
    xgplFilename='LICENSE'
):
    hasXGPL=False
    for x in fLs:
        if xgplFilename==x:
            contents=None
            try:
                with open(x,'r') as f:
                    contents=f.read()
                if contents==license['license']:
                    hasXGPL=True
                    break
            except FileNotFoundError:
                pass
    if not hasXGPL:
        writeDefinition=False
        if force:
            writeDefinition=True
        else:
            if 'y'==input('MISSING XGPL DEFINITION FILE... WRITE? [y/any]: '):
                writeDefinition=True
        if writeDefinition:
            with open(xgplFilename,'w') as f:
                f.write(license['license'])
            errMsg='''
                XGPL DEFINITION HAD NOW BEEN WRITTEN TO THE FILE: {0}.  MAKE
                SURE YOU COMMIT THIS FILE TO YOUR GIT REPOSITORY.
            '''.format(xgplFilename)
            pErr('\n\n'+massageMultiline(errMsg))
        hasXGPL=True
    return hasXGPL

def writeXGPL(
    license,
    author,
    program,
    fLs=None,
    exclusions=None,
    force=False,
    xgplFilename='LICENSE'
):
    if None==fLs:
        useGit=True
        br=BashIOE('git ls-tree -r --full-tree --name-only master')
        fLs=[x for x in br.out if x]
    if hasXGPL_Definition(license,fLs,exclusions,force,xgplFilename):
        writeXGPL_Stamps(license,author,program,fLs,exclusions,force)

def xgplInterface(authorString,programName,license='GPL'):
    if 'GPL'==license.upper():
        license=g__gpl
    elif 'LGPL'==license.upper():
        license=g__lgpl
    else:
        raise NotImplementedError
    writeXGPL(license,authorString,programName)

if '__main__'==__name__:
    import argparse

    parser = argparse.ArgumentParser(description='Write/Maintain xGPL stamps')
    parser.add_argument('author', type=str, help='copyright author')
    parser.add_argument('project', type=str, help='project name')
    parser.add_argument(
        '--LGPL',
        dest='lgpl',
        action='store_true',
        default=False,
        help='use LGPL insterad of GPL',
    )
    args = parser.parse_args()
    license='GPL'
    if True==args.lgpl:
        license = 'LGPL'
    xgplInterface(args.author, args.project, license)
    


