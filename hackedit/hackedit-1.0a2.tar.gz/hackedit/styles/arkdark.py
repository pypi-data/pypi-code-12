"""
This module contains the darcula pygments theme.
"""
from .crepuscule import CrepusculeStyle


class ArkDarkStyle(CrepusculeStyle):
    """
    A variant of the crepuscule scheme, made to look good when using
    the ark-dark gtk theme.
    """
    background_color = '#404552'
    highlight_color = '#303542'
