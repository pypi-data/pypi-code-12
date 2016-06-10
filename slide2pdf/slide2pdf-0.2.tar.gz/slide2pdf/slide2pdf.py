from selenium import webdriver
import os
import glob
import subprocess
import time

class slide2pdf:
    def __init__(self, url, height, width):
        self.url = url
        self.slides = self.__no_of_slides()
        self.browser = webdriver.Firefox()
        self.browser.set_window_size(height, width)
        self.browser.get(self.url)

    def __no_of_slides(self):
        filename = self.url.replace("file://", "")
        s = open(filename, 'r')
        content = s.readlines()
        s.close()

        slide = filter(lambda x: 'class="slide' in x, content)
        return len(slide)

    def snap_shot(self):
        subprocess.call(["xdotool", "key", "Return"])

        for num in range(self.slides):
            self.browser.save_screenshot("frame%02d.png" % num)
            subprocess.call(["xdotool", "key", "space"])
            time.sleep(1)

    def convert_pdf(self):
        filepath = os.path.basename(self.url)
        filename = os.path.splitext(filepath)[0]
        subprocess.call(["convert", "frame*.png", filename + ".pdf"])
        self.__remove_files()
        self.browser.quit()

    def __remove_files(self):
        files = glob.glob("*.png")
        for f in files:
            os.remove(f)
