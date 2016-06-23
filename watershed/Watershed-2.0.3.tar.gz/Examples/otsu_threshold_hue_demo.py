#!/usr/bin/env python

##  hist_equalize_demo.py

##  The goal of this script is to demonstrate hue thresholding by applying the
##  Otsu threshold to the hue compoent in the HSV representation of a color image.


from Watershed import *

image_name = "fruitlets2.jpg"

shed = Watershed(
               data_image = image_name,
               binary_or_gray_or_color = "color",
               size_for_calculations = 128,
               sigma = 1,
               gradient_threshold_as_fraction = 0.1,
               level_decimation_factor = 16,
               padding = 50,
       )

shed.apply_otsu_threshold_to_hue(-1)           # or you can choose 1

