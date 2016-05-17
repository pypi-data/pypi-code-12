import scipy.constants

from . import UpperValenceBand

class Optical():
    """Dichalcogenide properties related to optical transitions.

    Instantiate with a :class:`.Dichalcogenide` instance, e.g.,

    .. code-block:: python

       optical = Optical(Dichalcogenide('mos2', 'default'))
    """

    def __init__(self, dichalcogenide):
        self._dichalcogenide = dichalcogenide
        self._energy = UpperValenceBand(self._dichalcogenide)

    def p_circular(self, e, τ, ϵ):
        """Matrix element for optical transitions (circular polarization):
        :math:`\\left|P^{+-}_α \\left(E, \\mathbf{ϵ_±} \\right)\\right|^2`.

        Transitions are from the upper valance band to the lower conduction band.
        Given in units of :math:`\\text{GeV}^2`.

        :param e: Energy :math:`E`.
        :type e: float

        :param τ: Valley index :math:`τ = ±1`.
        :type τ: int

        :param ϵ: Polarization index :math:`ϵ = ±1`.
        :type ϵ: int
        """
        constant = scipy.constants.value

        at = self._dichalcogenide.at
        m0 = constant('electron mass energy equivalent in MeV')
        ℏ = constant('Planck constant over 2 pi in eV s')
        c = constant('speed of light in vacuum')
        Å = scipy.constants.angstrom

        sin = self._energy.trig('sin^2 θ/2')
        cos = self._energy.trig('cos^2 θ/2')
        x = 2 * (10**3 * at * Å * m0 / (c * ℏ))**2

        if ϵ * τ == 1:
            return x * sin(e)**2
        elif ϵ * τ == -1:
            return x * cos(e)**2
        else:
            raise RuntimeError(
                'Valley and polarization indexes must have values 1 or -1')
