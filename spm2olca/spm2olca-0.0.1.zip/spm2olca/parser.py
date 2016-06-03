import spm2olca.model as m


class Parser(object):
    def __init__(self):
        self.methods = []

        self._method = None
        self._section = None
        self._category = None
        self._damage = None
        self._nw_set = None

    def parse(self, file_path):
        with open(file_path, 'r', encoding='windows-1252') as f:
            for raw_line in f:
                line = raw_line.strip()
                self._next_line(line)

    def _next_line(self, line):

        if line == 'Method':
            # start of a new method
            self._method = m.Method()
            return

        if self._method is None:
            return

        if line == '':
            # empty lines are section separators
            if self._category is not None and self._section == 'Substances':
                self._category = None
            if self._nw_set is not None and self._section == 'Weighting':
                self._nw_set = None
            if self._damage is not None and self._section == 'Impact categories':
                    self._damage = None
            self._section = None
            return

        if line == 'End':
            self._end()

        if self._section is None:
            self._section = line
            return

        self._data_row(line)

    def _end(self):
        if self._method is not None:
            self.methods.append(self._method)
        self._method = None
        self._section = None

    def _data_row(self, line):
        if self._section == 'Name':
            self._method.name = line
            return

        if self._section == 'Comment':
            self._method.comment = line
            return

        if self._section == 'Weighting unit':
            self._method.weighting_unit = line
            return

        if self._section == 'Impact category':
            self._category = m.ImpactCategory(line)
            self._method.impact_categories.append(self._category)
            return

        if self._section == 'Substances' and self._category is not None:
            f = m.parse_impact_factor(line)
            self._category.factors.append(f)

        if self._section == 'Normalization-Weighting set':
            self._nw_set = m.NwSet(line)
            self._method.nw_sets.append(self._nw_set)

        if self._section == 'Normalization' and self._nw_set is not None:
            f = m.parse_category_factor(line)
            self._nw_set.normalisations.append(f)

        if self._section == 'Weighting' and self._nw_set is not None:
            f = m.parse_category_factor(line)
            self._nw_set.weightings.append(f)

        if self._section == 'Damage category':
            self._damage = m.DamageCategory(line)
            self._method.damage_categories.append(self._damage)

        if self._section == 'Impact categories' and self._damage is not None:
            f = m.parse_category_factor(line)
            self._damage.factors.append(f)
