class Topology():
    """Dichalcogenide topological properties.

    Instantiate with a :class:`.Dichalcogenide` instance, e.g.,

    .. code-block:: python

       topology = Topology(Dichalcogenide('mos2', 'default'))
       topology.Ω(0, 1, 1, 1)
    """

    def __init__(self, dichalcogenide):
        self._dichalcogenide = dichalcogenide

    def Ω(self, k, n, τ, σ):
        """Berry curvature.
        :param k: Momentum :math:`k`.
        :type k: float

        :param n: Band index :math:`n = ±1`.
        :type n: int

        :param τ: Valley index :math:`τ = ±1`.
        :type τ: int

        :param σ: Spin index :math:`σ = ±1`.
        :type σ: int

        :return: :math:`Ω^n_{τ σ} (k)`
        :rtype: float
        """
        d = self._dichalcogenide
        at, Δ, λ = d.at, d.Δ, d.λ
        x = Δ - λ * τ * σ
        y = (2 * at * k)**2 + x**2
        return -2 * (n * τ * at**2) * x * y**(-3/2)
