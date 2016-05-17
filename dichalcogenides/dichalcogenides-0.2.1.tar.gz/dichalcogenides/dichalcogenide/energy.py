import numpy

class Energy():
    """Dichalcogenide properties related to the energy.

    Instantiate with a :class:`.Dichalcogenide` instance, e.g.,

    .. code-block:: python

       energy = Energy(Dichalcogenide('mos2', 'default'))
       energy.e(0, 1, 1, 1)
    """

    def __init__(self, dichalcogenide):
        self._dichalcogenide = dichalcogenide

    def e(self, k, n, τ, σ):
        """Band energy.

        :param k: Momentum :math:`k`.
        :type k: float

        :param n: Band index :math:`n = ±1`.
        :type n: int

        :param τ: Valley index :math:`τ = ±1`.
        :type τ: int

        :param σ: Spin index :math:`σ = ±1`.
        :type σ: int

        :return: :math:`E^n_{τ σ} (k)`
        :rtype: float
        """
        d = self._dichalcogenide
        at, Δ, λ = d.at, d.Δ, d.λ
        sqrt = numpy.sqrt
        α = τ * σ
        return 0.5 * (λ * α + n * sqrt((2 * at * k)**2 + (Δ - λ * α)**2))

    # TODO: Raise error when e is out of range given n.
    # pylint: disable=unused-argument
    def k(self, e, n, τ, σ):
        """Inverse energy-momentum relation.

        :param e: Energy :math:`E`.
        :type e: float

        :param n: Band index :math:`n = ±1`.
        :type n: int

        :param τ: Valley index :math:`τ = ±1`.
        :type τ: int

        :param σ: Spin index :math:`σ = ±1`.
        :type σ: int

        :return: :math:`k(E)`
        :rtype: float
        """
        d = self._dichalcogenide
        at, Δ, λ = d.at, d.Δ, d.λ
        sqrt = numpy.sqrt

        x = 2 * e * Δ**-1
        y = (λ * Δ**-1) * (1 - x)

        return (at**-1) * (Δ / 2) * sqrt(x**2 + 2 * τ * σ * y - 1)

class UpperValenceBand():
    """Dichalcogenide properties related to the upper valence band energy.

    For this class, the energy is assumed to be in the upper valence band:
    :math:`n = -1` and :math:`τ = σ`.

    Instantiate with a :class:`.Dichalcogenide` instance, e.g.,

    .. code-block:: python

       uvb = UpperValenceBand(Dichalcogenide('mos2', 'default'))
       uvb.ρ(0)
    """

    def __init__(self, dichalcogenide):
        self._dichalcogenide = dichalcogenide

    @property
    def Δμ(self):
        """Chemical potential offset.

        The distance of the chemical potential
        from the top of the upper valence band.

        :return: :math:`Δμ`
        :rtype: float
        :default: :math:`-λ`
        """
        if not hasattr(self, '_Δμ'): self.Δμ = -self._dichalcogenide.λ
        return self._Δμ

    @Δμ.setter
    def Δμ(self, value):
        self._Δμ = value

    @property
    def μ(self):
        """Chemical potential.

        Determined by the chemical potential offset.

        :return: :math:`μ = λ - Δ / 2 + Δμ`
        :rtype: float
        """
        d = self._dichalcogenide
        Δ, λ, Δμ = d.Δ, d.λ, self.Δμ
        return λ - Δ / 2 + Δμ

    @property
    def ξ_bounds(self):
        """Allowed range for the variable :math:`ξ = E - μ`.

        :return: :math:`(\\left|Δμ\\right| - 2 λ, \\left|Δμ\\right|)`
        :rtype: tuple
        """
        λ, Δμ = self._dichalcogenide.λ, self.Δμ
        return (abs(Δμ) - 2 * λ, abs(Δμ))

    def ρ(self, e):
        """Density of states.

        :param e: Energy :math:`E`.
        :type e: float

        :return: :math:`ρ(E) = \\left|k'(E) k(E)\\right|`
        :rtype: float
        """
        d = self._dichalcogenide
        at, λ = d.at, d.λ
        return abs(2 * e - λ) * (2 * at**2)**(-1)

    def trig(self, name):
        """Trigonometric functions of the energy.

        * ``sin θ``       - :math:`\\sin θ(E)`
        * ``cos θ``       - :math:`\\cos θ(E)`
        * ``sin^2 θ/2``   - :math:`\\sin^2 \\frac{θ(E)}{2}`
        * ``cos^2 θ/2``   - :math:`\\cos^2 \\frac{θ(E)}{2}`

        :param name: One of the above function names.
        :type name: str

        :return: Corresponding function of the energy :math:`E`.
        :rtype: function
        """
        fn = {}
        λ, Δ = self._dichalcogenide.λ, self._dichalcogenide.Δ
        sqrt = numpy.sqrt
        x = lambda e: (2 * e - λ)**(-1)

        fn['sin θ'] = lambda e: sqrt((2 * e - Δ) * (2 * e + Δ - 2 * λ)) * x(e)
        fn['cos θ'] = lambda e: (Δ - λ) * x(e)
        fn['sin^2 θ/2'] = lambda e: (e - Δ / 2) * x(e)
        fn['cos^2 θ/2'] = lambda e: (e + Δ / 2 - λ) * x(e)

        return fn[name]
