"""
This module contains the darcula pygments theme.
"""
from .crepuscule import CrepusculeStyle


class MidnaDarkStyle(CrepusculeStyle):
    """
    A variant of the crepuscule scheme, made to look good when using
    the midna dark kde theme.
    """
    background_color = '#31343f'
    highlight_color = '#384058'
