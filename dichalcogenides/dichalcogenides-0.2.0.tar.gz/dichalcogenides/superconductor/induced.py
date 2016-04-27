from dichalcogenides.dichalcogenide import UpperValenceBand

from . import Superconductor

class Induced(Superconductor):
    """Induced superconductor.

    Inherits from :class:`.Superconductor`.
    """

    def __init__(self, model):
        super().__init__(model)
        self._energy = UpperValenceBand(self.model)

    @property
    def Δc(self):
        """Conduction band coupling constant.

        :return: :math:`Δ_c`
        :rtype: float
        """
        return self.model.system_parameter('Δc')

    @property
    def Δv(self):
        """Valance band coupling constant.

        :return: :math:`Δ_v`
        :rtype: float
        """
        return self.model.system_parameter('Δv')

    @property
    def Δk(self):
        """The superconducting parameter :math:`Δ_\\mathbf{k}`
        as a function of the energy :math:`E`.

        :return: :math:`Δ(E)`
        :rtype: func
        """
        Δc, Δv = self.Δc, self.Δv
        cos = self._energy.trig('cos θ')
        return lambda e: (1 / 2) * ((Δc + Δv) + (Δc - Δv) * cos(e))
