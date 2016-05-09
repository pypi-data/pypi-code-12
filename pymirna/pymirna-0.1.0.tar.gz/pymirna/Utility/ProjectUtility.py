from pymirna.Utility.FileReader import *
import os


PROJECT_NAME_TAG = "[PROJECT_NAME]"
FILE_LIST_TAG = "[FILE_LIST]"
INITIAL_ID = "[INITIAL_ID]"
PROJECT_EXTENSION = ".pmi"

class ProjectManager:

    def __init__(self):
        self.__initAttribute__()


    def __initAttribute__(self):
        self.__filelist = []
        self.__projectName = ""
        self.__directory = ""
        self.__initID = [1,1,1]

    def createProject(self, path, name):
        if(path[len(path)-1] is not '/'):
            path += '/'

        self.__projectName = name
        self.__directory = path

        cmd = "mkdir -p " + path
        os.system(cmd)

        file = open(path+name+PROJECT_EXTENSION, 'w')
        file.writelines(PROJECT_NAME_TAG+'\n')
        file.writelines(name+'\n')
        file.writelines(FILE_LIST_TAG+'\n')
        file.writelines(INITIAL_ID+'\n')
        file.writelines('1,1,1'+'\n')
        file.close()

        cmd = "mkdir -p " + path + "Profile"
        os.system(cmd)
        cmd = "mkdir -p " + path + "Result/PreProcessing"
        os.system(cmd)
        cmd = "mkdir -p " + path + "Result/miRNA_Discovery"
        os.system(cmd)
        cmd = "mkdir -p " + path + "Result/Target_Prediction"
        os.system(cmd)
        cmd = "mkdir -p " + path + "file_list"
        os.system(cmd)

    def openProject(self, path):
        if( not checkFile(path) ):
            return False
        fext = '.'+getFileExtension(path)
        if( fext != PROJECT_EXTENSION ):
            return False

        readingFile = False

        file = open(path, 'r')
        temp = file.readline().split('\n')[0]
        while(temp is not ''):
            if(temp == PROJECT_NAME_TAG):
                self.__projectName = file.readline().split('\n')[0]
            elif(temp == FILE_LIST_TAG):
                readingFile = True
                temp = file.readline().split('\n')[0]
                continue
            elif(temp == INITIAL_ID):
                readingFile = False
                temp = file.readline().split('\n')[0].split(',')
                for i in range(0,len(temp)):
                    temp[i] = eval(temp[i])
                self.__initID = temp


            if(readingFile):
                self.__filelist.append(temp)

            temp = file.readline().split('\n')[0]

        self.__directory = path[0:len(path)-len(self.__projectName+PROJECT_EXTENSION):]
        file.close()

    def closeProject(self):
        self.__filelist = []
        self.__directory = ''
        self.__projectName = ''

    def saveProject(self):

        file = open(self.__directory+self.__projectName+PROJECT_EXTENSION, 'w')

        file.writelines(PROJECT_NAME_TAG+'\n')
        file.writelines(self.__projectName+'\n')
        file.writelines(FILE_LIST_TAG+'\n')
        for i in self.__filelist:
            file.writelines(i+'\n')

        file.writelines(INITIAL_ID+'\n')
        file.writelines(str(self.__initID[0])+','+str(self.__initID[1])+','+str(self.__initID[2])+'\n')
        file.close()

    def getFileList(self):
        return self.__filelist

    def addFile(self, file):
        if(not checkFile(file)):
            return False
        self.__filelist.append(file)

    def removeFile(self, file):
        for i in self.__filelist:
            if(i == file):
                self.__filelist.remove(i)
                return

    def getProjectName(self):
        return self.__projectName

    def changeProjectName(self, n):
        self.__projectName = n

    def getDirectory(self):
        return self.__directory

    def setInitialID(self, idlist):
        self.__initID = idlist

    def getInitialID(self):
        return self.__initID