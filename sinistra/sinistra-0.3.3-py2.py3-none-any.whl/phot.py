from astropy.io import fits
import numpy as np
import os

from . import utilities

def aperture_grid(image, spacing, output=False, clobber=False):
	"""
	Makes a grid of apertures and writes to a qphot-compatible coords file.

	:param image: location of the image to be used.
	:type image: str
	:param spacing: x and y spacing between locations. For example, if one
	                aperture is located at x, the next is x + spacing. The
	                same thing holds for the y direction.
	:param spacing: float
	:param output: Either False, or the name of the coordinates file 
	                    that the output will be written to. If you don't want 
	                    to write to a file, pass in False.
	:type output: bool / str
	:param clobber: Whether or not to check for an already existing file of
	                this name. If it already exists, it will raise an error.
	:returns: List of tuples that contain the x,y coordinates of each
	          aperture.
	"""
	if output and not clobber:
		if utilities.check_if_file(output):
			raise IOError("The coords file {} already exists. "
				          " Set clobber = True if you're okay with "
				          "overwriting this.")
	# if everything is fine, it will continue on.

	# get the size of the image from the header
	header = fits.getheader(image)
	x_max = header["NAXIS1"]
	y_max = header["NAXIS2"]

	# then find all the places apertures can go. The first one is spaced half
	# a spacing from the edge, so that if aperture_size = spacing, then the 
	# aperture would go to the edge of the image.
	xs = np.arange(spacing / 2.0, x_max, spacing)
	ys = np.arange(spacing / 2.0, y_max, spacing)

 	# Then turn these into ordered pairs.
 	ordered_pairs = []
	for x in xs:
		for y in ys:
			ordered_pairs.append((x, y))

	# then if the user wants to, write to the file
	if output:
		with open(output, "w") as output_file:
			for pair in ordered_pairs:
				x, y = pair
				output_file.write("{} {}\n".format(x, y))

	# no matter what, return the ordered pairs
	return ordered_pairs


def fit_gaussian_negative(data, upper_cutoff, plot=False, savename=None,
	                      data_label="Counts"):
	"""
	Fits a Gaussain to all data underneath some cutoff.

	This is useful when doing things where the lower side of a Gaussian tells
	about the intrinsic scatter of something, whereas the upper end is 
	contaminated by real objects. An example is the flux within many 
	randomly placed apertures. The lower side will tell the sky error in the
	aperture flux.

	:param data: list of data to be fitted.
	:type data: list, np.array
	:param upper_cutoff: Data below this number will be used to fit the 
	                     Gaussian, while data above this will be rejected.
	:type upper_cutoff: float
	:param plot: Whether or not to create a plot showing the best fit to the
	             histogram of the data.
	:type plot: bool
	:param savename: If you are creating a plot, enter a file path here to save
	                 the figure. If this is left as none, then the plot will 
	                 not be saved. If you are running in an Jupyter notebook,
	                 the figure will show up even if it is not saved, so it's 
	                 not essential.
	:type savename: str
	:param data_label: Descriptor of the data that will be used on the x-axis
	                   of the data histogram. Defaults to "Flux" unless 
	                   otherwise specified.
	:type data_label: str
	:return: the mean and sigma of the best fit Gaussian.
	"""
	from scipy.optimize import curve_fit

	good_data = [item for item in data if item < upper_cutoff]

	# make the bins that will be used to fit things
	bins = np.linspace(min(data), upper_cutoff, 250)


	bin_values, bin_edges = np.histogram(good_data, bins=bins)

	# turn the edges into centers of the bins
	bin_centers = []
	for i in range(len(bin_edges) - 1):  # iterate through all left edges
		# then take the average of the left and right edges.
		center = np.mean([bin_edges[i], bin_edges[i+1]])
		bin_centers.append(center)

	# we can then fit the gaussian using Scipy.
	params, uncertainty = curve_fit(utilities.gaussian, xdata=bin_centers,
	                                ydata=bin_values)
	# we know what the params are, so find them.
	mean, sigma, amplitude = params
	# get rid of any sign on sigma, which sometimes happens
	sigma = abs(sigma)

	# now we need to plot the histogram if the user wants. 
	if plot:
		# import the things needed to plot
		import betterplotlib as bpl
		import matplotlib.pyplot as plt
		bpl.default_style()

		fig, ax = plt.subplots()
		# set the new bounds for the histogram. We want to reuse the old bounds
		# on the left side, plus make an equally spaced one on the upper side
		lower_lim = min(data)
		# the upper boundary goes the same distance as the lower boundary 
		# from the upper_cutoff, which will be the center of the plot
		upper_lim  = upper_cutoff + (upper_cutoff - min(data))

		# then turn this into bins.
		bins = np.linspace(lower_lim, upper_lim, 500)
        bpl.hist(data, bins=bins, label="Data")
        
        # Then get the overplotted gaussian
        xs = np.linspace(lower_lim, upper_lim, 5000)
        ys = utilities.gaussian(xs, mean, sigma, amplitude)
        plt.plot(xs, ys, c=bpl.almost_black, lw=3, label="Best fit")

        # Then format the plot nicelay
        bpl.legend(loc="upper right")
        bpl.set_limits(mean - 4 * sigma, mean + 4 * sigma)
        bpl.add_labels(data_label, "Number")

        # If the user wants to, save the figure.
        if savename is not None:
        	plt.savefig(savename, format=savename[-3:])

	# return only the params that matter, since the amplitude is determined
	# by our choice of binning.
	return mean, sigma

# def ap_phot(center_row_idx, center_col_idx, image_data, aperture_radius):
# 	"""
# 	This does aperture photometry without any background subtraction. 

# 	NOte: This is untested and needs to be re-written. Don't use this.
# 	"""
    
#     flux = 0
#     min_row = int(max(np.ceil(aperture_radius), np.floor(center_row_idx - aperture_radius)))
#     max_row = int(min(image_data.shape[0] - np.ceil(aperture_radius) - 1, np.ceil(center_row_idx + aperture_radius)))
#     # I subtracted one from the shape to get the index, which is not the same as the length.
#     min_col = int(max(np.ceil(aperture_radius), np.floor(center_col_idx - aperture_radius)))
#     max_col = int(min(image_data.shape[1] - np.ceil(aperture_radius) - 1, np.ceil(center_col_idx + aperture_radius)))
    
#     for row_idx in range(min_row, max_row + 1):  # plus one to include the max value
#         for col_idx in range(min_col, max_col + 1):
#             if np.sqrt((row_idx - center_row_idx)**2 + (col_idx - center_col_idx)**2) < aperture_radius:
#                 flux += image_data[row_idx][col_idx]
#     return flux

def sky_error(image, aperture_size, flux_conv, plot=True):
	"""
	Figures out the sky error with an aperture of a given size.

	This is done by placing apertures in a grid throughout the image, then
	doing aperture photometry within those apertures. Most of those will be on
	empty sky. By examining the spread of the fluxes of the apertures that
	were on empty sky, we can get an idea of the general sky scatter in an 
	aperture of that size.

	:param image: Image to do this process on. Pass in the path to the image,
	              or just the name of the image if it is in the current
	              directory.
	:type image: str
	:param aperture_size: The diameter of the aperture you want to use. NOTE
	                      THAT THIS IS DIAMETER, NOT RADIUS!
	:type aperture_size: float
	:param flux_conv: multiplicative factor to get from counts in the image
	                  to real fluxes in whatever units you want. Should be
	                  defined such that "flux" = "counts" * `flux_conv`. This
	                  can be determined from the zeropoint of the image.
	:type flux_conv: float
	:param plot: Whether or not to plot the Gaussian that results from this
	             process.
	:type plot: bool
	:return: flux error within that aperture size, in real flux units. Note 
	         you need to multiply by the aperture correction to get total 
	         errors!
	"""

	# first define the aperture grid
	aperture_grid(image, aperture_size, 
		          '{}_ap_grid.txt'.format(image.split(os.sep)[-1]))

	# then do photometry at those locations. 


	# THIS FUNCTION IS NOT DONE.



