import os as os
import tinytools as tt
import inspect as inspect

def _runit():
    # Go into each directory and look for interesting things per pseudo-code:
    #
    # if ".TIL found":
    #     "return all .TILs and stop"
    # elif ".TIF found" :
    #     "return all .TIFs and stop"
    # elif ".shp or .json found" :
    #     "return all .shp and .json then stop"
    #
    # then use "filename_map.PVL" to add quick access entries
    # on the OrderedBunch

    pkg_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    pkg_dirs = tt.files.search(pkg_dir, '*', ret_files=False, ret_dirs=True)

    # Setup the data structure to be populated
    pkg_samples = tt.bunch.OrderedBunch()

    # Return files from each of the sample directories
    for d in pkg_dirs:
        # Set sample folder info bunch structure to populated
        name = os.path.basename(d)
        pkg_samples[name] = tt.bunch.OrderedBunch()

        # Set package name
        if os.path.isdir(d):
            pkg_samples[name]['path'] = d

        # Check for notes
        tmpnote = tt.files.search(d, 'notes.txt', case_sensitive=False)
        if tmpnote:
            with open(tmpnote[0],'r') as f:
                pkg_samples[name]['notes'] = f.read()

        # Look for TIL files
        tmptil = tt.files.search(d, '*.TIL', case_sensitive=False, depth=3)
        # Look for TIF files
        tmptif = tt.files.search(d, ['*.TIF', '*.TIFF'],
                                 case_sensitive=False, depth=3)
        # Look for vector files
        tmpvec = tt.files.search(d, ['*.SHP', '*.json', '*.geojson'],
                                 case_sensitive=False, depth=3)

        if tmptil:
            pkg_samples[name]['files'] = tmptil
            # pkg_samples[name] = _build_dgimg(pkg_samples[name])
        elif tmptif:
            pkg_samples[name]['files'] = tmptif
            # pkg_samples[name] = _build_dgimg(pkg_samples[name])
        elif tmpvec:
            pkg_samples[name]['files'] = tmpvec
            # pkg_samples[name] = _build_vec(pkg_samples[name])

        try:
            name_map = tt.pvl.read_from_pvl(os.path.join(d,'filename_map.PVL'))
        except:
            name_map = {}

        for k,v in name_map.iteritems():
            v = tt.files.search(d,'*'+v,depth=3)
            if v[0] in pkg_samples[name]['files']:
                pkg_samples[name][k] = v[0]

    return pkg_samples
