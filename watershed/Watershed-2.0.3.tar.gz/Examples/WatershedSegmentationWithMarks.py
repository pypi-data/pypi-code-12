#!/usr/bin/env python

## WatershedSegmentationWithMarks.py


'''
This is the main script for demonstrating user-assisted Watershed
segmentation of an image.

It first elicits from the user a delineation of polygonal regions in the
image that should be subject to gradient modification.  

IMPORTANT: Note that each localized region is supplied SEPARATELY by
           clicking clockwise on the boundary of where you think the
           gradients are best set to zero.

For the orchid image that is used in this demonstration, you are likey to
supply half-a-dozen such regions iteratively --- through as many separate
interactions with the image.

For the orchid image that is supplied to the constructor of the Watershed
module through the `data_image' parameter, the segmentation produced is
shown in the following image

    _output_segmentation_for_orchid_with_marks.jpg

The marks that were used for this segmentation are shown in

    _composite_image_with_all_marks_orchid0001.jpg

Since the marks shown are in three different colors, that means that are
the result of three separate interactions between the user and the image.
'''


from Watershed import *

shed = Watershed(
               data_image = "orchid0001.jpg",
               binary_or_gray_or_color = "color",
               size_for_calculations = 128,
               sigma = 1,
               gradient_threshold_as_fraction = 0.10,
               level_decimation_factor = 16,
       )

shed.extract_data_pixels() 
print("Displaying the original image:")
shed.display_data_image()
print("Eliciting user input for gradient mods:")
shed.mark_image_regions_for_gradient_mods()
print("Calculating the gradient image")
shed.compute_gradient_image()
print("Modifying the gradient image.")
shed.modify_gradients_with_marker_minima()
print("Computing Z level sets for the gradient image")
shed.compute_Z_level_sets_for_gradient_image()
print("Propagating influences:")
shed.propagate_influence_zones_from_bottom_to_top_of_Z_levels()
shed.display_watershed()
shed.display_watershed_in_color()
shed.extract_watershed_contours()
shed.display_watershed_contours_in_color()

