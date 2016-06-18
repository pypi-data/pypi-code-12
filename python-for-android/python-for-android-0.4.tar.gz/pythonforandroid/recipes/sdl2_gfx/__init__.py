
from pythonforandroid.toolchain import NDKRecipe
from os.path import exists

class LibSDL2GFX(NDKRecipe):
    version = '1.0.1'
    url = 'http://www.ferzkopp.net/Software/SDL2_gfx/SDL2_gfx-{version}.tar.gz'
    dir_name = 'SDL2_gfx'

recipe = LibSDL2GFX()
