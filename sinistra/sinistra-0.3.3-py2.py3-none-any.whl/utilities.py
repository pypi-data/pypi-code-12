# note: modules are imported in each function to reduce overhead when using these utilities. This way, only the modules
# that are needed for the functions you use will be imported, rather than the modules needed for all utilities.
import numpy as np
import os

def reduced_chi_sq(model, data, errors):
    """ Does a reduced chi squared calculation

    .. math::
        \\chi^2 = \\sum_{k=1}^{n} \\left( \\frac{\\text{model}_k - \\text{data}_k}{\\text{error}_k} \\right) ^2

        \\chi^2_{\\text{red}} = \\frac{\\chi^2}{n}

    where :math:`n` is the number of data points.

    :param model: list of values that describe a possible fit to the data
    :param data: list of values that are the data do be fitted
    :param errors: list of errors on the data
    :return: value for the reduced chi squared value of the fit of the model to the data
    """
    if not len(model) == len(data) == len(errors):
        raise ValueError("The length of the model, data, and errors need to be the same.")
    chi_sq = 0
    for i in range(len(model)):
        chi_sq += ((model[i] - data[i])/errors[i])**2
    return chi_sq/(len(data))

def mag_to_flux(mag, zeropoint):
    """Convert a magnitude into a flux.

    We get the conversion by starting with the definition of the magnitude scale.

    .. math::
        m = -2.5 \\log_{10}(F) + C 

        2.5 \\log_{10}(F) = C - m

        F = 10^{\\frac{C-m}{2.5}}

    :param mag: magnitdue to be converted into a flux.
    :param zeropoint: zeropoint (in mags) of the magnitude system being used
    :return: flux that corresponds to the given magnitude
    """

    return 10**((zeropoint - mag)/2.5)


def flux_to_mag(flux, zeropoint):
    """Convert flux to magnitude with the given zeropoint.

    .. math::
        m = -2.5 \\log_{10} (F) + C

    :param flux: flux in whatever units. Choose your zeropoint correctly to make this work with the units flux is in.
    :param zeropoint: zeropoint of the system (in mags)
    :return: magnitude that corresponds to the given flux
    """

    import numpy as np
    try:
        return -2.5 * np.log10(flux) + zeropoint  # This is just the definition of magnitude
    except ValueError:  # the flux might be negative, and will mess things up
        return np.nan


def mag_errors_to_percent_flux_errors(mag_error):
    """Converts a magnitude error into a percent flux error.

    .. math::
        m = -2.5 \\log_{10} (F) + C

        dm = \\frac{-2.5}{\ln(10)} \\frac{dF}{F}

        \\frac{dF}{F} = \\frac{\\ln(10)}{2.5} dm 

    The minus sign just tells us that increasing flux gives decreasing magnitudes, so we can safely ignore it.

    :param mag_error: magnitude error
    :return: percentage flux error corresponding to this magnitude error.
    """

    return mag_error * (np.log(10) / 2.5)  # math.log takes natural log unless specified.

def percent_flux_errors_to_mag_errors(percent_flux_error):
    """Converts a percentage flux error into a magnitude error.

    .. math::
        m = -2.5 \\log_{10} (F) + C

        dm = \\frac{-2.5}{\ln(10)} \\frac{dF}{F}


    :param percent_flux_error: percentage flux error
    :return: magnitude error corresponding to the percentage flux error.
    """

    return (2.5 / np.log(10)) * percent_flux_error


def empty_data(datatype):
    """
    Makes an empty data of a given datatype. 

    This is useful for filling tables that have missing values.

    Here is what the various datatypes return:

    Float: np.nan

    Integer: -999999999999

    String: Empty string.

    :param datatype: data type, obtained by using `.dtype` on some numpy object.
    """

    if "f" == datatype.kind:
        return np.nan
    elif "i" == datatype.kind:
        return -999999999999
    elif "S" == datatype.kind:
        return ""

def check_if_file(possible_location):
    """
    Check if a file already exists at a given location.

    :param possible_location: File to check. Can be a path to a file, too.
    :type possible_location: str
    :return: bool representing whether or not a file already exists there.
    """

    # have to do separate cases for files in current directory and those 
    # elsewhere. Those with paths has os.sep in their location.
    if os.sep in possible_location:
        # get all but the last part, which is the directory
        directory = os.sep.join(possible_location.split(os.sep)[:-1]) 
        # then the filename is what's left
        filename = possible_location.split(os.sep)[-1]
    else:  # it's in the current directory
        directory = "."
        filename = possible_location

    # Then check if the given file exists
    if filename in os.listdir(directory):
        return True 
    else:
        return False

def gaussian(x, mean, sigma, amplitude):
    """
    The Gaussian density at the given value.

    The Gaussian density is defined as 

    .. math::
        f(x) = A e ^ {- \\frac{(x - \\mu)^2}{2 \\sigma^2}}

    Note that if you want a normalized Gaussian (so that the total area 
    under the curve is 1), then use the `normed_gaussian()` function.

    :param x: location to get the Gaussian density at.
    :type x: float
    :param mean: Mean of the Gaussian.
    :type mean: float
    :param sigma: Standard deviation of the Gaussian. Should be positive
    :type sigma: float
    :param amplitude: Height of the highest point of the Gaussian.
    :return: Gaussain density of the given gaussian at the given x value. 

    """

    return amplitude * np.e ** (-1 * ((x - mean)**2 / (2 * sigma**2)))

def normed_gaussian(x, mean, sigma):
    """
    The Gaussian density at the given value.

    The Gaussian density is defined as 

    .. math::
        f(x) = \\frac{1}{\\sigma \\sqrt{2 \\pi}} e ^ {- \\frac{(x - \\mu)^2}{2 \\sigma^2}}

    Noe that if you want a Gaussian that is not normalized (ie where you 
    can set the amplitude), then use the `gaussian()` function.

    :param x: location to get the Gaussian density at.
    :type x: float
    :param mean: Mean of the Gaussian.
    :type mean: float
    :param sigma: Standard deviation of the Gaussian. Should be positive
    :type sigma: float
    :return: Gaussain density of the given gaussian at the given x value. 

    """

    # first see if amplitude is defined, and if not, normalize it.
    amplitude = 1.0 / (sigma * np.sqrt(2 * np.pi))
    return amplitude * np.e ** (-1 * ((x - mean)**2 / (2 * sigma**2)))

def flux_conv(flux_zeropont, counts_zeropoint):
    """
    Calculate the conversion factor from counts to flux.

    This is done by using the zeropoints of the magnitudes in flux and counts.
    The magnitude should be the same no matter how we calculate it, which is
    how we can derive this:

    .. math::
        \\text{mag}_\\text{flux} = \\text{mag}_\\text{counts}

        -2.5 \\log_{10}(F) + Z_F = -2.5 \\log_{10}(C) + Z_C

        \\text{where $F = $ Flux, $C = $ counts, and $Z_F$ and $Z_C$ represent the respective zeropoints when using flux or counts}

        -2.5(\\log_{10}(F) - \\log_{10}(C)) = Z_C - Z_F

        \\log_{10} \\left( \\frac{F}{C} \\right) = \\frac{Z_F - Z_C}{2.5}

        \\frac{F}{C} = 10^{\\frac{Z_F - Z_C}{2.5}}

        F = C * 10^{\\frac{Z_F - Z_C}{2.5}}

        F = C * \\text{Flux Conversion}

        \\text{where Flux Conversion $= 10^{\\frac{Z_F - Z_C}{2.5}}$}


    This flux conversion is what is calculated here.

    NOTE: Make sure the magnitudes really are the same (ie AB/Vega).

    :param flux_zeropoint: zero point for calculating magnitudes when using 
                           flux, such that mag = -2.5 log(flux) + 
                           `flux_zeropoint`. The actual value will depend
                           on what flux units you want. If you want
                           microJanskys, use 23.9, for example.
    :type flux_zeropoint: float
    :param counts_zeropoint: zero point for calculating magnitues when using 
                             counts, such that mag = -2.5 log(counts) +
                             `counts_zeropoint`. This is often found in the
                             header of the image in question.
    :type counts_zeropoing: float
    :returns: float containing the conversion from counts to flux, such that
              flux = counts * flux_conv. See above for derivation.

    """

    return 10 ** ((flux_zeropont - counts_zeropoint) / 2.5)

# Store the vega to AB conversions. They must all be of the form 
# m_AB = m_Vega + conversion
vega_to_ab_conversions = {"w1": 2.683,
                          "w2": 3.319,
                          "w3": 5.242,
                          "w4": 6.604}

def vega_to_ab(vega_mag, band):
    """
    Converts a Vega mag to AB.

    This basically contains a bunch of AB-Vega conversions, so I don't have
    to look them up every time I want to do anything.

    :param vega_mag: magnitude in the Vega system to be converted to AB.
    :type vega_mag: float
    :param band: Band the magnitude is in. Can be one of the following: "w1",
                 "w2", "w3", "w4".
    :type band: str
    :returns: float containing the ab magnitude
    """
    # use the dictionary I defined above.
    try: 
        return vega_mag + vega_to_ab_conversions[band]
    except KeyError:
        print("{} has not yet been implemented. Find the conversion "
              "and add it, please. ")

def ab_to_vega(ab_mag, band):
    """
    Converts a AB mag to Vega.

    This basically contains a bunch of AB-Vega conversions, so I don't have
    to look them up every time I want to do anything.

    :param ab_mag: magnitude in the AB system to be converted to Vega.
    :type ab_mag: float
    :param band: Band the magnitude is in. Can be one of the following: "w1",
                 "w2", "w3", "w4".
    :type band: str
    :returns: float containing the Vega magnitude
    """

    # use the dictionary I defined above.
    try: 
        return ab_mag - vega_to_ab_conversions[band]
    except KeyError:
        print("{} has not yet been implemented. Find the conversion "
              "and add it, please. ")

# Note: these all need to be tested.

