# Imports
import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import xarray as xr

from calipso.data.coordinate import Coordinate


# Functions
def valid_range_finder(datasetvariable):
    '''
    Given a netcdf4 dataset variable, it will check the valid range
    instance and convert the lower and upper bounds to floats.
    
    Returns
    -------
    bounds : tuple
        Tuple of low and upper bound of valid range
        Example (0, 1.25)
    '''
    range_string = datasetvariable.valid_range
    try:
        low, high = map(float, range_string.split('...'))
    except:
        raise Exception('Valid Range is only a single value, please implement')
    
    return low, high


def select_data(filename, var_name='Extinction_Coefficient_532'):
    """
    Function that is given an hdf file path and variable of interest.
    Defaults to Extinction data
    """
    dataset = nc.Dataset(filename)
    variable = dataset[var_name]
    variable.set_auto_maskandscale(False)
    variable_data = ma.masked_outside(variable, *valid_range_finder(variable))
    
    return variable_data


def make_altitudes():
    '''
    Convenience function for making the array of altitudes for Calypso data.
    Makes them in Km.
    
    CALIOP is a three channel lidar, with detectors that collect 532 nm parallel,
    532 nm perpendicular, and 1064 nm light that is backscattered from molecules and particulates
    in the atmosphere [38]. CALIOP Level 2 (L2) products include Profile product, Layer product,
    and Vertical Feature Mask (VFM) product. Profile products mainly provide 532 and 1064 nm column AOD,
    the vertical distribution of the extinction coefficient, the backscatter coefficient, and the depolarization ratio.
    CALIOP provides a high horizontally resolution of 333 m (vertically resolution of 30 m) for altitudes of 0–8.2 km,
    1.0 km (60 m) for altitudes of 8.2–20.2 km, and 1.67 km (180 m) for altitudes
    of 20.2–30.1 km (https://www-calipso.larc.nasa.gov/products/, last access: 31 June 2021) [38].
    A more detailed description of the CALIPSO satellite and its parameters are also available on the
    NASA website (https://www-calipso.larc.nasa.gov/documents/, last access: 31 June 2021).
    Here, Level 2 (L2) products of CALIOP’s version 3 during the daytime were
    used from 2007 to 2015 in the present study.
    '''
    alt = 0
    alts = [alt]
    step = 0
    
    while len(alts) < 399:
        if 0 <= alt < 8.2:
            step = 0.06
        elif 8.2 <= alt < 20.2:
            step = 0.06
        else:
            step = 0.18
        
        alt += step
        alts.append(alt)
    
    # The altitudes in the extinction array is expecting the highest first so I flip my array
    return np.flip(np.array(alts))


def create_extinction_tensor(filename):
    '''
    Makes a tensor of extinction coefficients given a data file via path of filename.
    The tensor is an xarray of dimension latitude x altitude.
    
    Returns
    -------
    xarray : dims [ 'lat', 'alt' ]
    '''
    
    extinction_data = select_data(filename)
    latitude = select_data(filename, 'Latitude')[:, 0]
    longitude = select_data(filename, 'Longitude')[:, 0]
    altitudes = make_altitudes() # Makes the altitudes I think the documentation is telling me it makes
    
    data_tensor = xr.DataArray(extinction_data, dims=['lat', 'alt'], coords=[latitude, altitudes])
    
    # Packs the lat and lon data in attrs so it can be retrieved later for complete plotting of coordinates
    data_tensor.lat.attrs['lat'] = latitude
    data_tensor.lat.attrs['lon'] = longitude
    return data_tensor


def filter_tensor(data_tensor, latitudes=(-90, 90), longitudes=False, altitudes=(0, 12), sortby='lat'):
    '''
    Takes in an xarray tensor along with the sections of latitude, and altitude
    that should be kept. Altitudes are in Km.
    
    Returns the transpose of the original tensor since the next step is probably plotting
    figured it would save a little bit of typing.
    
    This started out way more complicated than it needed to be
    and really isn't necessary as the line to do the same thing looks like:
    qm = extinction_data.sortby('lat').loc[-10:55, extinction_data.alt <= 12].transpose().plot(ax=ax, cmap=plt.cm.plasma, add_colorbar=False)
    which isn't horrible. I decided to keep it though so the actions being done are explicit
    rather than implicit.
    '''

    a, b = min(altitudes), max(altitudes) # The altitudes can be given in any order
    sorted_alts = data_tensor.sortby(sortby).alt
    altitudes_mask = [ a <= alt and alt <= b for alt in sorted_alts] # Boolean mask of where the altitude should be kept
    
    return data_tensor.sortby(sortby).loc[slice(*latitudes), altitudes_mask].transpose()



# Not actually useful for anything, just while I was learning about the data

def print_variables(filename):
    '''
    Used to print the variables of a dataset so I can spell them
    easier. Not very useful
    '''
    dataset = make_dataset(filename)
    for i in dataset.variables.values():
        print(i.name)


def make_dataset(filename):
    '''
    Shorthand for makeing a file given by filename which should
    be a full path into a netcdf4 dataset object
    '''
    return nc.Dataset(filename)
