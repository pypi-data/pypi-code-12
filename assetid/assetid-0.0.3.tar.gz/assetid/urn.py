# Package level logger
import random
import string
import itertools

import logging
logger = logging.getLogger("assetid")
logger.addHandler(logging.NullHandler())


class IoosUrn(object):
    """ https://geo-ide.noaa.gov/wiki/index.php?title=IOOS_Conventions_for_Observing_Asset_Identifiers """

    def __init__(self, *args, **kwargs):

        self.asset_type   = None
        self.authority    = None
        self.label        = None
        self.component    = None
        self.discriminant = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def from_string(urn_string):
        complete = urn_string.split('#')
        extras = ''
        if len(complete) > 1:
            extras = '#{0}'.format(complete[1])
        parts = complete[0].split(':')

        if len(parts) < 5:
            return IoosUrn()

        urn            = IoosUrn()
        urn.asset_type = parts[2]
        urn.authority  = parts[3]
        urn.label      = parts[4]
        if len(parts) > 5:
            if urn.asset_type == 'station':
                urn.discriminant = parts[5]
            elif len(parts) > 6:
                # Also a discriminant specified, so this has to be the component
                urn.component = parts[5] + extras
            else:
                logger.debug("Assuming that {0} is the 'component' piece of the URN (not the 'discriminant')".format(parts[5] + extras))
                urn.component = parts[5] + extras
        if len(parts) > 6:
            urn.discriminant = parts[6]
        if len(parts) > 7:
            pass
            logger.warning("The URN is too long stripping off '{}'".format(':'.join(parts[7:])))
        return urn

    @staticmethod
    def from_dict(authority, label, data_dict):

        def clean_value(v):
            return v.replace('(', '').replace(')', '').strip().replace(' ', '_')

        extras = []
        intervals = []  # Because it can be part of cell_methods and its own dict key

        if 'cell_methods' in data_dict and data_dict['cell_methods']:
            cm = data_dict['cell_methods']
            keys = []
            values = []
            sofar = ''
            for i, c in enumerate(cm):
                if c == ":":
                    if len(keys) == len(values):
                        keys.append(clean_value(sofar))
                    else:
                        for j in reversed(range(0, i)):
                            if cm[j] == " ":
                                key = clean_value(cm[j+1:i])
                                values.append(clean_value(sofar.replace(key, '')))
                                keys.append(key)
                                break
                    sofar = ''
                else:
                    sofar += c
            # The last value needs appending
            values.append(clean_value(sofar))

            pairs = zip(keys, values)

            mems = []
            cell_intervals = []
            pairs = sorted(pairs)
            for group, members in itertools.groupby(pairs, lambda x: x[0]):
                if group == 'interval':
                    cell_intervals = [m[1] for m in members]
                elif group in ['time', 'area']:  # Ignore 'comments'. May need to add more things here...
                    member_strings = []
                    for m in members:
                        member_strings.append('{}:{}'.format(group, m[1]))
                    mems.append(','.join(member_strings))
            if mems:
                extras.append('cell_methods={}'.format(','.join(mems)))
            if cell_intervals:
                intervals += cell_intervals

        if 'bounds' in data_dict and data_dict['bounds']:
            extras.append('bounds={0}'.format(data_dict['bounds']))

        if 'vertical_datum' in data_dict and data_dict['vertical_datum']:
            extras.append('vertical_datum={0}'.format(data_dict['vertical_datum']))

        if 'interval' in data_dict and data_dict['interval']:
            if isinstance(data_dict['interval'], (list, tuple,)):
                intervals += data_dict['interval']
            elif isinstance(data_dict['interval'], str):
                intervals += [data_dict['interval']]

        logger.info(data_dict)

        if 'standard_name' in data_dict and data_dict['standard_name']:
            variable_name = data_dict['standard_name']
        elif 'name' in data_dict and data_dict['name']:
            variable_name = data_dict['name']
        else:
            variable_name = ''.join(random.choice(string.ascii_uppercase) for _ in range(8)).lower()
            logger.warning("Had to randomly generate a variable name: {0}".format(variable_name))

        if 'discriminant' in data_dict and data_dict['discriminant']:
            variable_name = '{}:{}'.format(variable_name, data_dict['discriminant'])

        if intervals:
            intervals = list(set(intervals))  # Unique them
            extras.append('interval={}'.format(','.join(intervals)))

        if extras:
            variable_name = '{0}#{1}'.format(variable_name, ';'.join(extras))

        urn = IoosUrn(asset_type='sensor',
                      authority=authority,
                      label=label,
                      component=variable_name,
                      discriminant=None)

        return urn

    @property
    def urn(self):
        if self.valid() is False:
            return None
        z = 'urn:ioos:{0}:{1}:{2}'.format(self.asset_type, self.authority, self.label)
        if self.component is not None:
            z += ':{}'.format(self.component)
        if self.discriminant is not None:
            z += ':{}'.format(self.discriminant)
        return z.lower()

    def attributes(self, combine_interval=True):
        """
        By default, this will put the `interval` as part of the `cell_methods`
        attribute (NetCDF CF style). To return `interval` as its own key, use
        the `combine_interval=False` parameter.
        """
        if self.valid() is False:
            return dict()

        if self.asset_type != 'sensor':
            logger.error("This function only works on 'sensor' URNs.")
            return dict()

        if '#' in self.component:
            standard_name, extras = self.component.split('#')
        else:
            standard_name = self.component
            extras = ''

        d = dict(standard_name=standard_name)

        if self.discriminant is not None:
            d['discriminant'] = self.discriminant

        intervals = []
        cell_methods = []
        if extras:
            for section in extras.split(';'):
                key, values = section.split('=')
                if key == 'interval':
                    # special case, intervals should be appended to the cell_methods
                    for v in values.split(','):
                        intervals.append(v)
                else:
                    if key == 'cell_methods':
                        value = [ x.replace('_', ' ').replace(':', ': ') for x in values.split(',') ]
                        cell_methods = value
                    else:
                        value = ' '.join([x.replace('_', ' ').replace(':', ': ') for x in values.split(',')])
                        d[key] = value

        if combine_interval is True:
            if cell_methods and intervals:
                if len(cell_methods) == len(intervals):
                    d['cell_methods'] = ' '.join([ '{} (interval: {})'.format(x[0], x[1].upper()) for x in zip(cell_methods, intervals) ])
                else:
                    d['cell_methods'] = ' '.join(cell_methods)
                    for i in intervals:
                        d['cell_methods'] += ' (interval: {})'.format(i.upper())
            elif cell_methods:
                d['cell_methods'] = ' '.join(cell_methods)
                for i in intervals:
                    d['cell_methods'] += ' (interval: {})'.format(i.upper())
            elif intervals:
                raise ValueError("An interval without a cell_method is not allowed!  Not possible!")
        else:
            d['cell_methods'] = ' '.join(cell_methods)
            d['interval'] = ','.join(intervals).upper()

        if 'vertical_datum' in d:
            d['vertical_datum'] = d['vertical_datum'].upper()

        return d

    def valid(self):
        ASSET_TYPES = ['station', 'network', 'sensor', 'survey']

        try:
            assert self.authority is not None
        except AssertionError:
            logger.error('An "authority" is required')
            return False

        try:
            assert self.label is not None
        except AssertionError:
            logger.error('A "label" is required')
            return False

        try:
            assert self.asset_type in ASSET_TYPES
        except AssertionError:
            logger.error('asset_type {0} is unknown.  Must be one of: {1}'.format(self.asset_type, ', '.join(ASSET_TYPES)))
            return False

        if self.asset_type == 'station':
            try:
                assert self.component is None
            except AssertionError:
                logger.error('An asset_type of "station" may not have a "component".')
                return False

        return True

    def __str__(self):
        return self.urn

    def __repr__(self):
        return self.__str__
