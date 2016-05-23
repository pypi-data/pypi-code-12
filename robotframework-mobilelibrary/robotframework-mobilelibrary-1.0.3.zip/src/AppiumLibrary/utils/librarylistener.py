# -*- coding: utf-8 -*-
import re

import events as event
import os
from PIL import Image
import images2gif
from robot.libraries.BuiltIn import BuiltIn
import shutil



class LibraryListener(object):

    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, name, attrs):
        event.dispatch( 'scope_start', attrs['longname'] )

    def end_suite(self, name, attrs):
        event.dispatch( 'scope_end', attrs['longname'] )

    def start_test(self, name, attrs):
        event.dispatch( 'scope_start', attrs['longname'] )

    def end_test(self, name, attrs):
        my_variables = BuiltIn().get_variables()
        current_output_dir = os.path.abspath(my_variables['${OUTPUTDIR}'])
        test_output_dir = os.path.join(current_output_dir,name)
        gif_name  = my_variables['${SUITE_NAME}'] + '.' + my_variables['${TEST_NAME}']
        gif_name = re.sub(r'\s+','_',gif_name)
        gif_name = gif_name + '.gif'
        gif_path = os.path.join(current_output_dir,gif_name)

        myPicList = self.GetDirImageList(os.path.abspath(my_variables['${OUTPUTDIR}']),False)
        #human sort png list eg: [1,11,2] -- > [1,2,11]
        myPicList = self.sort_nicely(myPicList)

        if myPicList:
            self.GetGifAnimationFromImages(gif_path, myPicList)
        else:
            print '[!!!] NONE PICTURE'

        if os.path.isdir(test_output_dir):
            shutil.rmtree(test_output_dir)
        os.mkdir(test_output_dir)

        for item in os.listdir(current_output_dir):
            if  re.search(r'.*gif.*png',item):
                shutil.move(os.path.join(current_output_dir,item),os.path.join(test_output_dir,item))

        event.dispatch( 'scope_end', attrs['longname'] )

    #gif gen fx()
    def GetGifAnimationFromImages(self,targetGifFilePath, srcImageFilePaths):
        images = []
        heightAndFilePaths = []

        for imageFilePath in srcImageFilePaths:
            fp = open(imageFilePath, "rb")
            width,height = Image.open(fp).size
            heightAndFilePaths.append((height, imageFilePath))
            fp.close()

        heightAndFilePaths.sort(key=lambda item: item[0], reverse=True)

        for heightAndFilePath in heightAndFilePaths:
            img = Image.open(heightAndFilePath[1])
            images.append(img)

        images2gif.writeGif(targetGifFilePath, images, duration=1, nq=0.1)

    def GetDirImageList(self,dir_proc, recusive = True):
        resultList = []
        for file in os.listdir(dir_proc):
            if re.search(r'.*gif.*png',file):   # <------ select specified picture type
                    if os.path.isdir(os.path.join(dir_proc, file)):
                        if (recusive):
                            resultList.append(self.GetDirImageList(os.path.join(dir_proc, file), recusive))
                        continue
                    resultList.append(os.path.join(dir_proc, file))

        # if run fail: append the last failure screenshot to gen-gif png list
        for file in os.listdir(dir_proc):
            if re.search(r'appium.*png',file):   # <------ select specified picture type
                if os.path.isdir(os.path.join(dir_proc, file)):
                    if (recusive):
                        resultList.append(self.GetDirImageList(os.path.join(dir_proc, file), recusive))
                    continue
                # rename appium-screenshot-x.png --> screenshot-x.png
                new_name = str(file).replace('appium-','Appium-')
                shutil.move(os.path.join(dir_proc,file),os.path.join(dir_proc,new_name))
                resultList.append(os.path.join(dir_proc, new_name))
        return resultList

    # human sort
    def tryint(self,s):
        try:
            return int(s)
        except:
            return s

    def alphanum_key(self,s):
        return [ self.tryint(c) for c in re.split('([0-9]+)', s) ]

    def sort_nicely(self,l):
        l.sort(key=self.alphanum_key)
        return l
