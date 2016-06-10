#!/usr/bin/env python
import random
import argparse
import inflect
import json

class rollme:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Generate a random number from some parameters')
        parser.add_argument('-a', action="store", dest="action", default='standard', help="Type of Dice Action, defaults to 'standard'")
        parser.add_argument('-t', action="store", dest="type", default='standard', help="Type of Dice, defaults to 'standard'")
        parser.add_argument('-x', action="store", dest="highrange", type=int, required=False, help="High Range")
        parser.add_argument('-y', action="store", dest="lowrange", type=int, required=False, help="Low Range")
        parser.add_argument('-c', action="store", dest="custom_config", required=False, help="Custom configuration file path")
        parser.add_argument('-z', action="store_true", dest="override_defaults", default=False, required=False, help="Override dice types with custom types")
        parser.add_argument('-g', action="store", dest="groups", required=False, help="Groups of Dice, example: 6,4,8")
        parser.add_argument('-l', action="store", dest="labels", default='', required=False, help="Label your Groups of Dice, example: Six,Four,Eight")
        parser.add_argument('-o', action="store", dest="output", default='print', required=False, help="What kind of output do you want?")

        args = parser.parse_args()

        self.dice_action = args.action
        self.dice_type = args.type
        self.low_range = args.highrange
        self.high_range = args.lowrange
        self.custom_config = args.custom_config
        self.override_defaults = args.override_defaults
        self.dice_groups = args.groups
        self.dice_labels = args.labels
        self.output = args.output

        self.dice_group_type = None
        self.dice_label_type = None
        self.default_dice_types = {
            '4': { 'low': 1, 'high': 4 },
            '6': { 'low': 1, 'high': 6 },
            '8': { 'low': 1, 'high': 8 },
            '10': { 'low': 1, 'high': 10 },
            '12': { 'low': 1, 'high': 12 },
            '20': { 'low': 1, 'high': 20 },
            'custom': { 'low': self.low_range, 'high': self.high_range }
        }

        if self.dice_groups:
            dash = self.dice_groups.find('-')
            if dash > -1:
                self.dice_groups = self.dice_groups.split('-')
                self.dice_group_type = 'block'
            else:
                self.dice_groups = self.dice_groups.split(',')
                self.dice_group_type = 'list'

        if self.dice_labels:
            dash = self.dice_labels.find('-')
            comma = self.dice_labels.find(',')
            if dash > -1:
                self.dice_labels = self.dice_labels.split('-')
                self.dice_label_type = 'block'
            elif comma > -1:
                self.dice_labels = self.dice_labels.split(',')
                self.dice_label_type = 'list'
            else:
                if self.dice_labels == 'blank':
                    self.dice_label_type = 'blank'
                else:
                    self.dice_labels = None
                    self.dice_label_type = 'default'

        if self.dice_type == 'standard' and (self.low_range and self.high_range):
            self.dice_type = 'custom'

        if self.custom_config:
            try:
                with open(self.custom_config, 'r') as config_file:
                    self.custom_config = config_file.read()
                    self.custom_config = json.loads(self.custom_config)

                    for custom_dice in self.custom_config['dice_types']:
                        this_name = custom_dice['name']
                        if this_name in self.default_dice_types:
                            if self.override_defaults:
                                self.default_dice_types[this_name]['low'] = custom_dice['low']
                                self.default_dice_types[this_name]['high'] = custom_dice['high']
            except:
                self.custom_config = None
                pass

    def makeObject(self, data, is_error):
        break_on_comma = data.split(',')
        counter = 0
        for entry in break_on_comma:
            parts = entry.split(':')

            try:
                value = int(parts[2])
                roll = parts[2]
                error = None
            except:
                roll = None
                error = parts[2]

            new_data = {
                'label': parts[0],
                'type': parts[1],
                'roll': roll,
                'error': error
            }
            break_on_comma[counter] = new_data
            counter += 1

        return break_on_comma

    def makeJson(self, data):
        return json.dumps(data, indent=4)

    def makeOutput(self, value, is_error=False):
        if self.output == 'print':
            print(value)
        elif self.output == 'json':
            print(self.makeJson(self.makeObject(value, is_error)))
        elif self.output == 'object':
            return self.makeObject(value, is_error)
        else:
            return value

    def rollTheDice(self, low_range, high_range):
        if low_range and high_range:
            if low_range < high_range:
                return random.randint(int(low_range),int(high_range))
            else:
                return 'Low range must be lower than high range'
        else:
            return 'No range specified'

    def diceType(self, dice_type='standard', low_range=None, high_range=None):
        if dice_type:
            if dice_type == 'standard':
                dice_type = '6'
            for dice, range_info in self.default_dice_types.iteritems():
                if dice_type == dice:
                    if dice_type == 'custom':
                        if low_range and high_range:
                            return self.rollTheDice(range_info['low'], range_info['high'])
                        else:
                            return 'Both ranges (high & low) were not specified'
                    else:
                        return self.rollTheDice(range_info['low'], range_info['high'])
                else:
                    if self.custom_config:
                        if 'dice_types' in self.custom_config:
                            for custom_dice in self.custom_config['dice_types']:
                                if 'name' in custom_dice:
                                    custom_name = custom_dice['name']
                                    if custom_name == dice_type:
                                        if 'low' in custom_dice and 'high' in custom_dice:
                                            low = custom_dice['low']
                                            high = custom_dice['high']
                                            if low and low > 0 and high and high > 0:
                                                return self.rollTheDice(low, high)
                                            else:
                                                return 'Missing a low or high for custom dice: ' + custom_name
                                        else:
                                            return 'No low and high for custom dice: ' + custom_name

            return 'Dice type specified is not available'
        else:
            return 'No dice type specified'

    def main(self):
        if self.dice_action == 'standard':
            roll_value = self.diceType(self.dice_type, self.low_range, self.high_range)
            if roll_value:
                return self.makeOutput(roll_value)
        elif self.dice_action == 'group':
            if self.dice_groups:
                p = inflect.engine()
                roll_value = ''
                counter = 0
                if self.dice_group_type == 'list':
                    for entry in self.dice_groups:
                        entry_string = p.number_to_words(entry)
                        self.dice_groups[counter] = self.diceType(entry, self.low_range, self.high_range)
                        label = entry_string.capitalize()
                        if self.dice_labels:
                            if 0 <= counter and counter < len(self.dice_labels):
                                label = self.dice_labels[counter]
                        if counter > 0:
                            roll_value += ','

                        if self.dice_label_type == 'blank':
                            roll_value += "{}"
                        else:
                            roll_value += label + ':' + entry + ':{}'

                        counter += 1

                    roll_value = roll_value.format(*self.dice_groups)
                    return self.makeOutput(roll_value)
                elif self.dice_group_type == 'block':
                    dice_type = self.dice_groups[1]
                    range_high = (int(self.dice_groups[0])+1)
                    self.dice_groups = []
                    for entry in range(1, range_high):
                        entry_string = p.number_to_words(entry)
                        self.dice_groups.insert(counter, self.diceType(dice_type, self.low_range, self.high_range))
                        label = entry_string.capitalize()
                        if self.dice_labels:
                            if 0 <= counter and counter < len(self.dice_labels):
                                label = self.dice_labels[counter]
                        if counter > 0:
                            roll_value += ','

                        if self.dice_label_type == 'blank':
                            roll_value += "{}"
                        else:
                            roll_value += label + ':' + self.dice_type + ':{}'
                        counter += 1

                    roll_value = roll_value.format(*self.dice_groups)
                    return self.makeOutput(roll_value)
            else:
                return 'No dice'

if __name__ == '__main__':
    myapp = rollme()
    myapp.main()
