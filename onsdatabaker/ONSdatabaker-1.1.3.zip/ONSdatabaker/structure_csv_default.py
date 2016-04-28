"""
Template/Options file for altering the structure of the .csv flatfile output.

Terminology:

standard dimensions - the dimensions/columns that must be present in each and every file output by
databaker. You must always have an observations/values column as a standard dimension. It must ALWAYS 
be the first one.

topic dimensions - the dynamic dimensions (varying in number, minimum of one). These get added to the 
right hand side of your standard columns. 

"""

# = Standard Dimensions ========

# Start = list of headers for standard dimensions
start = "Observation,Data Marking,Geographic Area,Time"

# Dimension names (as strings!)
# This defines how you'll assign data to the standard columns within the recipes
# MUST have OBS. The others are optional.
dimension_names = ['OBS', 'DATAMARKER', 'GEOG', 'TIME']


# --- DONT CHANGE this code
# Create variables
for i, item in enumerate(reversed(dimension_names)):
    exec(item+"=-i")

__all__ = list(dimension_names) # don't expose unnecessary items when using `from foo import *`
# --- end of DONT CHANGE


# Columns to skip after each dimension/column is output. Order should match dimension_names.
# The number specifies columns to skip (so you can more easily matcha  required input structure)
SKIP_AFTER = {OBS: 0,            # 1  MANDATORY, must be here, must be called OBS
              DATAMARKER: 0,      
              GEOG: 0,            
              TIME: 0,           
              }        

# = Topic Dimensions ========

# Repeat - a comma delimited string of headers to be repeated for each topic dimension, use {num} to count
# i.e "Value {num},Blank {num},Name {num}" would extract topic dimensions as:
# Value 1, Blank 1, Name 1, Value 2, Blank 2, Name 2, etc
repeat = "dim_id_{num}"


# Where in the repeat do you want to output the dimension name and value?
# Example ([value,'', name]) would output three columns per topic dimensions, as above example
def get_topic_headers(name, value):  # DONT alter this
    return ([value])   # Change this line

# Where are the values? (should mirror the above (minus the 'name entries)
# So, ['value', '', ''] for our value-blank-name example
value_spread = ['value']

# do you want to output the 'name' value in the header of the 'value' columns?
topic_headers_as_dims = True



# ====================== S-P-E-C-I-A-L handling ==========================
# the following are laragely ONS specific but can be swtiched on and off for anyones use

# Standard Dimensions/columns that need to be outputted twice in a row (i.e item|label combos)
# if you use this you MUST account for the extra column with an extra heading in 'start'
SH_Repeat = []

# Do we want to create a TIMEUNIT dimension using a TIME dimension - very ONS specific
SH_Create_ONS_time = False

# Do you want to split the OBS, placing non float data into something specified in dimension_names
# If not, change it to '= False'
SH_Split_OBS = DATAMARKER
