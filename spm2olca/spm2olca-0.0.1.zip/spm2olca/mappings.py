import csv
import logging as log
from .util import flow_uuid, as_path
from .data import data_dir


def compartment(label: str) -> str:
    if label is None:
        return 'unspecified'
    t = label.strip().lower()
    if t in ('', '(unspecified)'):
        return 'unspecified'
    if t == 'air':
        return 'Emissions to air'
    if t == 'water':
        return 'Emissions to water'
    if t == 'soil':
        return 'Emissions to soil'
    if t == 'raw':
        return 'Resources'
    return label.strip()


class UnitEntry(object):
    def __init__(self, csv_row):
        self.unit_name = csv_row[0]
        self.unit_id = csv_row[1]
        self.property_name = csv_row[2]
        self.property_id = csv_row[3]


class UnitMap(object):
    def __init__(self, file_path):
        self.mappings = {}
        with open(file_path, 'r', encoding='utf-8', newline='\n') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # skip first line
            for line in reader:
                entry = UnitEntry(line)
                self.mappings[entry.unit_name] = entry

    @staticmethod
    def create():
        """ Creates the unit map with default data. """
        path = data_dir + '/units.csv'
        return UnitMap(path)

    def get(self, unit_name: str) -> UnitEntry:
        if unit_name in self.mappings:
            return self.mappings[unit_name]
        return None


class FlowEntry(object):
    def __init__(self, csv_row):
        self.sp_name = csv_row[0]
        self.sp_category = csv_row[1]
        self.sp_sub_category = 'unspecified' if csv_row[2] == '' else csv_row[2]
        self.sp_unit = csv_row[3]
        self.olca_flow_id = csv_row[4]
        self.olca_flow_name = csv_row[5]
        self.olca_property_id = csv_row[6]
        self.olca_property_name = csv_row[7]
        self.olca_unit_id = csv_row[8]
        self.olca_unit_name = csv_row[9]
        self.factor = float(csv_row[10])

    @property
    def flow_uid(self) -> str:
        """ Returns the SimaPro flow UUID generated from the SimaPro flow
            attributes
        """
        return flow_uuid(self.sp_category, self.sp_sub_category, self.sp_name,
                         self.sp_unit)


class FlowMap(object):
    def __init__(self, file_path):
        self.mappings = {}
        with open(file_path, 'r', encoding='utf-8', newline='\n') as f:
            reader = csv.reader(f, delimiter=';')

            for line in reader:

                if len(line) < 11:
                    log.error('invalid line in ' + file_path + ':' + str(line))
                    continue

                entry = FlowEntry(line)
                uid = entry.flow_uid
                if uid in self.mappings:
                    log.warning('Duplicate in flow mappings: ' + file_path)
                    log.warning('  ' + as_path(entry.sp_category,
                                               entry.sp_sub_category,
                                               entry.sp_name,
                                               entry.sp_unit))
                self.mappings[uid] = entry

    @staticmethod
    def create():
        """ Creates the flow map with default data. """
        path = data_dir + '/flows.csv'
        return FlowMap(path)

    def get(self, flow_uid: str) -> FlowEntry:
        if flow_uid in self.mappings:
            return self.mappings[flow_uid]
        return None
