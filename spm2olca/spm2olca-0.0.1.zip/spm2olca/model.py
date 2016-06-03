from .util import make_uuid, flow_uuid
from .mappings import compartment


class ImpactCategory(object):
    def __init__(self, line: str):
        parts = [p.strip() for p in line.split(';')]
        self.name = parts[0]
        self.ref_unit = parts[1]
        self.factors = []

    @property
    def uid(self):
        return make_uuid('ImpactCategory', self.name)


class ImpactFactor(object):
    def __init__(self):
        self.category = ''
        self.sub_category = ''
        self.name = ''
        self.cas = ''
        self.value = 0
        self.unit = ''

    @property
    def flow_uid(self):
        return flow_uuid(self.category, self.sub_category, self.name, self.unit)

    @property
    def flow_category_uid(self):
        return make_uuid('Category', self.category)

    @property
    def flow_sub_category_uid(self):
        return make_uuid('Category', self.category, self.sub_category)


class Method(object):
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.weighting_unit = ''
        self.impact_categories = []
        self.damage_categories = []
        self.nw_sets = []

    @property
    def uid(self):
        return make_uuid('ImpactMethod', self.name)

    def get_damage_factor(self, impact_category: ImpactCategory) \
            -> (str, float):
        """ Returns the name of the damage category and damage factor for the
            given LCA category
        """
        for category in self.damage_categories:
            for factor in category.factors:
                if factor.impact_category == impact_category.name:
                    return category.name, factor.factor
        return None


class DamageCategory(object):
    def __init__(self, line: str):
        parts = [p.strip() for p in line.split(';')]
        self.name = parts[0]
        self.ref_unit = parts[1]
        self.factors = []


class NwSet(object):
    def __init__(self, name: str):
        self.name = name
        self.normalisations = []
        self.weightings = []

    @property
    def uid(self):
        return make_uuid('NwSet', self.name)

    def get_weighting_factor(self, damage_category: str) -> float:
        for f in self.weightings:
            if f.impact_category == damage_category:
                return f.factor
        return None

    def get_normalisation_factor(self, damage_category: str) -> float:
        for f in self.normalisations:
            if f.impact_category == damage_category:
                return f.factor
        return None


class CategoryFactor(object):
    def __init__(self):
        self.impact_category = ''
        self.factor = 0.0


def parse_impact_factor(line: str) -> ImpactFactor:
    f = ImpactFactor()
    parts = [p.strip() for p in line.split(';')]
    f.category = compartment(parts[0])
    f.sub_category = compartment(parts[1])
    f.name = parts[2]
    f.cas = parts[3]
    f.value = float(parts[4].replace(',', '.'))
    f.unit = parts[5]
    return f


def parse_category_factor(line: str) -> CategoryFactor:
    f = CategoryFactor()
    parts = [p.strip() for p in line.split(';')]
    f.impact_category = parts[0]
    f.factor = float(parts[1])
    return f
