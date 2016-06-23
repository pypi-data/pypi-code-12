#!/usr/bin/env python

##  hist_equalize_demo.py

##  The goal of this script is to demonstrate contrast enhancement with histogram
##  thresholding.

from Watershed import *

image_name = "fruitlets.jpg"

shed = Watershed(
               data_image = image_name,
               binary_or_gray_or_color = "color",
               size_for_calculations = 128,
               sigma = 1,
               gradient_threshold_as_fraction = 0.1,
               level_decimation_factor = 16,
               padding = 20,
       )

shed.histogram_equalize()

