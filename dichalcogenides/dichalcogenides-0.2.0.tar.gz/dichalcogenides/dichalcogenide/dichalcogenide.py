from dichalcogenides.model import Model

class Dichalcogenide(Model):
    """Model for a dichalcogenide.


    Inherits from :class:`model.Model`.
    """

    @property
    def at(self):
        """Product of the lattice constant and hopping energy.

        :return: :math:`at`
        :rtype: float
        """
        return self.material_parameter('at')

    @property
    def λ(self):
        """Half the valence band spin splitting.

        :return: :math:`λ`
        :rtype: float
        """
        return self.material_parameter('λ')

    @property
    def Δ(self):
        """Valance band conduction band energy splitting.

        :return: :math:`Δ`
        :rtype: float
        """
        return self.material_parameter('Δ')
