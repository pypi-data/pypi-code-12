#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# name:        pysaurio.py / __init__.py (Python 3.x).
# description: A tool for searching, extracting, debugging and displaying
#              information from multiple text files.
#              It also allows merge files, including only the necessary
#              lines.
# author:      Antonio Suárez Jiménez, pherkad13@gmail.com
# date:        08-05-2016
#
#-------------------------------------------------------------------------

'''A tool for searching, extracting, debugging and displaying 
information from multiple text files.

It also allows merge files, including only the necessary lines.
'''

__author__ = 'Antonio Suárez Jiménez, pherkad13@gmail.com'
__title__= 'pysaurio'
__date__ = '2016-05-08'
__version__ = '0.2.4'
__license__ = 'GNU GPLv3'

import os, configparser, collections, re

#-------------------------------------------------------------------------
#
# clase: Raptor()
#
#-------------------------------------------------------------------------

class Raptor(object):
    '''Raptor for extracting and displaying information from a set of files 
    of the same type; and creating a single file with all the selected
    information. 
    '''
    
    app_folder = os.getcwd() + '/'
    def __init__(self):
        '''Initialize a .rap template
        
        Attribute List:
        
        - description: short descripton of .rap template
        - extension: extension of the files to read
        - prefix: files must begin with this string
        - input_folder: folder of files to read
        - output_folder: output folder to save file with result
        - output_file: output filename
        - delimiter: delimiter character
        - quotechar: quote character
        - include_header: '0' or '1'
        - include_file: '0' or '1'
        - include_record_num: '0' or '1'
        - include_empty_record: '0' or '1'
        - search_multiple: '0' or '1'
        - alternate_header: alternative text of the report header
        - fields: dictionary with fieldnames and search (read template)                  
        - record: dictionary with fieldnames and values (read template)
        - rules: list of rules (read template)
        - list_files: list of filenames to read (auto)
        - record_counter: number of records (auto)        
        - errors: list of errors (auto)
        - number_errors: number of errors after you open or save a template
        
        >>> rap1 = Raptor()
                   
        '''     
        self.description = ''
        self.extension = 'txt'
        self.prefix = ''
        self.input_folder = Raptor.app_folder
        self.output_folder = Raptor.app_folder
        self.output_file = 'output.csv'
        self.delimiter = ','
        self.quotechar = '"'
        self.include_header = '1'
        self.include_file = '0'
        self.include_record_num = '0'
        self.include_empty_record = '0'
        self.search_multiple = '0'
        self.alternate_header = ''
        self.fields = collections.OrderedDict({})
        self.record = collections.OrderedDict({})
        self.rules = []
        self.list_files = []
        self.errors = []
        self.number_errors = 0
        self.record_counter = 0
            
    def Open(self, name):
        '''Open .rap template
        
        name -- .rap template name
        
        >>> rap1.Open('template.rap')
        '''
        self.errors = []        
        if os.path.exists(name):
            config_file = configparser.ConfigParser()
            config_file.read(name)
            if config_file.has_option('General','description'):
                self.description = config_file['General']['description']
            else:
                self.description = ''
            if config_file.has_option('General','extension'):
                self.extension = config_file['General']['extension']
            else:
                self.extension = "txt"
            if config_file.has_option('General','prefix'):
                self.prefix = config_file['General']['prefix']
            else:
                self.prefix = ''
            if config_file.has_option('General','input_folder') and \
                os.path.exists(config_file['General']['input_folder']):
                self.input_folder = config_file['General']['input_folder'] + '/'
            else:
                self.input_folder = Raptor.app_folder
                self.errors.append('No source folder. ')
            if config_file.has_option('General','output_folder') and \
                os.path.exists(config_file['General']['output_folder']):
                self.output_folder = config_file['General']['output_folder'] + '/'
            else:
                self.output_folder = Raptor.app_folder
                self.errors.append('No target folder. ')
            if config_file.has_option('General','output_file') and \
                config_file['General']['output_file'] != '':
                self.output_file = self.output_folder + config_file['General']['output_file']
            else:
                self.output_file = self.output_folder + "output.csv"                
            if config_file.has_option('General','delimiter') and \
                config_file['General']['delimiter'] != '':
                self.delimiter = config_file['General']['delimiter']
            else:
                self.delimiter = ','
            if config_file.has_option('General','quotechar') and \
                config_file['General']['quotechar'] != '':
                self.quotechar = config_file['General']['quotechar']
            else:
                self.quotechar = '"'
            if config_file.has_option('General','include_header') and \
                config_file['General']['include_header'] in ['0','1'] :
                self.include_header = config_file['General']['include_header']
            else:
                self.include_header = '1'
            if config_file.has_option('General','include_file') and \
                config_file['General']['include_file'] in ['0','1']:
                self.include_file = config_file['General']['include_file']
            else:
                self.include_file = '0'
            if config_file.has_option('General','include_record_num') and \
                config_file['General']['include_record_num'] in ['0','1']:
                self.include_record_num = config_file['General']['include_record_num']
            else:
                self.include_record_num = '0'
            if config_file.has_option('General','include_empty_record') and \
                config_file['General']['include_empty_record'] in ['0','1']:
                self.include_empty_record = config_file['General']['include_empty_record']
            else:
                self.include_empty_record = '0'
            if config_file.has_option('General','search_multiple') and \
                config_file['General']['search_multiple'] in ['0','1']:
                self.search_multiple = config_file['General']['search_multiple']
            else:
                self.search_multiple = '0'                
            if config_file.has_option('General','alternate_header'):
                self.alternate_header = config_file['General']['alternate_header']
            else:
                self.alternate_header = ''
            self.fields = collections.OrderedDict({})
            self.record = collections.OrderedDict({})
            if 'Fields' in config_file:
                if self.include_record_num == '1':
                    self.fields['r___n'] = ''
                    self.record['r___n'] = ''
                if self.include_file == '1':
                    self.fields['f___n'] = ''
                    self.record['f___n'] = ''
                for option, value in config_file['Fields'].items():
                    self.fields[option] = value
                    self.record[option] = ''
            
            self.rules = []
            if len(self.fields) > 0:            
                if 'Rules' in config_file:  
                    for option, value in config_file['Rules'].items():
                        if option.upper().startswith('RULE') and len(option) > 4 and \
                            option[4:].strip().isnumeric():
                                value = eval(value)
                                if type(value) is tuple and len(value) > 1:
                                    self.rules.append(value)
            else:
                self.errors.append('No field/s. ')

        self.list_files = []            
        if len(self.errors) == 0:
            list_file = os.listdir(self.input_folder)
            for actual_file in list_file:
                if actual_file[-3:].upper() == self.extension.upper():
                    if actual_file.startswith(self.prefix):
                        self.list_files.append(actual_file)
            
            if len(self.list_files) > 0:
                self.list_files.sort()
            else:
                self.errors.append('No file/s to search. ')
        self.number_errors = len(self.errors)

    def Save(self, name):
        '''It saves .rap template
        
        name -- .rap template name
        
        >>> rap1.Save('template.rap')
        '''
        self.errors = []        
        config_file = configparser.ConfigParser()       
        if os.path.exists(name) == False:
            if len(self.fields) > 0:
                config_file['General'] = {}
                config_file['Fields'] = {}
                config_file['Rules'] = {}
                general = config_file['General']
                fields = config_file['Fields']
                rules = config_file['Rules']
                general['description'] = self.description
                general['extension'] = self.extension
                general['prefix'] = self.prefix
                general['output_folder'] = self.output_folder
                general['input_folder'] = self.input_folder
                general['output_file'] = self.output_file           
                general['delimiter'] = self.delimiter
                general['quotechar'] = self.quotechar
                general['include_header'] = self.include_header
                general['include_file'] = self.include_file
                general['include_record_num'] = self.include_record_num
                general['include_empty_record'] = self.include_empty_record
                general['search_multiple'] = self.search_multiple
                general['alternate_header'] = self.alternate_header
                for option, value in self.fields.items():
                    fields[option] = value
                
                for position in range(len(self.rules)):
                    rules['rule' + str(position+1)] = str(self.rules[position])
                
                with open(name, 'w') as output_config:
                    config_file.write(output_config)
            else:
                self.errors.append('No field/s. ')
        else:
            self.errors.append('The .rap template exists. ')
        self.number_errors = len(self.errors)
    
    def BuildHeader(self):
        '''Build header
        
        Returns Python list of field names
        
        >>> rap1.BuildHeader()
        '''
        if self.number_errors == 0:
            if self.alternate_header == '':
                return(list(self.fields.keys()))
            else:
                return([self.alternate_header])            
        else:
            return([])

    def BuildRow(self, row):
        '''Buid row (record)
        
        row -- filename to search
        
        Returns value of empty line: True/False and
                dictionary with field names and data
        
        >>> rap1.BuildRow('filename')
        '''
        if self.number_errors == 0:
            for option in self.record.keys():
                self.record[option] = ''
                
            if self.include_record_num == '1':
                self.record_counter += 1
                self.record['r___n'] = str(self.record_counter)      
                        
            current_file = open(self.input_folder + row, 'rb')                  
            while True:
                current_line = current_file.readline()
                current_line = current_line.decode("utf-8", "ignore")
                if not current_line: break
                current_line = current_line.rstrip()
                len_cl = len(current_line)                              
                for option, value in self.fields.items():                    
                    if self.include_file == '1' and option == 'f___n':
                        self.record[option] = row
                    elif self.include_record_num == '1' and option == 'r___n':
                        pass             
                    else:                       
                        len_ss = len(value)         
                        pos_ini = current_line.find(value)
                        if pos_ini != -1:
                            if len_cl > pos_ini + len_ss:
                                new_value = current_line[pos_ini + len_ss:]
                                if self.record[option] == '':
                                    self.record[option] = new_value.strip()             
                            if self.search_multiple == '0':
                                break
            
            current_file.close()    
            if self.include_empty_record == '0':
                fields = len(self.record.keys())
                empty_fields = 0
                for option in self.record.keys():
                    if option == 'r___n' or option == 'f___n':
                        fields -=1
                    elif self.record[option] == '':
                        empty_fields +=1
                if fields == empty_fields:
                    if self.include_record_num == '1':
                        self.record_counter -= 1
                    return(False, {})
                    
            return(True, self.record)
        else:
            return(False, {})

    def ApplyRules(self, rec):
        '''Apply rules (changes data)
        
        rec -- Python dictionary with field names and data
        
        Returns Python dictionary with field names and data updated
        
        >>> rap1.ApplyRules(Dict)
        
        Functions available for rules:
        
        - rule1 = (fieldname, 'SUBSTR', postion_initial, lenght)
        - rule1 = (fieldname, 'REPLACE', 'search_string', 'replace_string')
        - rule1 = (fieldname, 'REPLACEALL', 'search_string', 'replace_string')
        - rule1 = (fieldname, 'UPPER')
        - rule1 = (fieldname, 'LOWER')
        - rule1 = (fieldname, 'REVERSE')
        - rule1 = (fieldname, 'REMOVE')
        - rule1 = (fieldname, 'FIELDISDATA')
        - rule1 = (fieldname, 'REMOVEFROM', 'string')
        - rule1 = (fieldname, 'REMOVETO', 'string')
        
        '''         
        if self.number_errors == 0:
            for rule in self.rules:                     
                if len(rule) > 1 and len(rule) < 5 and rule[0] in rec:
                    field = rule[0]
                    operation = rule[1]
                    value = rec[field]
                    if len(rule) > 2:
                        arg1 = rule[2]
                    if len(rule) > 3:
                        arg2 = rule[3]                                                          
                    if operation.upper() == 'SUBSTR' and \
                        len(rule) == 4 and type(arg1) is int and \
                        type(arg2) is int and\
                        len(value) >= arg1 + arg2 - 1:
                            rec[field] = value[arg1-1:arg2].strip()                         
                    elif operation.upper() == 'REPLACE' and \
                        len(rule) == 4 and type(arg1) is str and \
                        type(arg2) is str:
                            rec[field] = value.replace(arg1, arg2, 1)
                    elif operation.upper() == 'REPLACEALL' and \
                        len(rule) == 4 and type(arg1) is str and \
                        type(arg2) is str:
                            rec[field] = value.replace(arg1, arg2)
                    elif operation.upper() == 'UPPER':
                        rec[field] = value.upper()                      
                    elif operation.upper() == 'LOWER':
                        rec[field] = value.lower()
                    elif operation.upper() == 'REVERSE':
                        rec[field] = value[::-1]                    
                    elif operation.upper() == 'REMOVE':
                        rec[field] = ''                     
                    elif operation.upper() == 'FIELDISDATA':
                        rec[field] = field                      
                    elif operation.upper() == 'REMOVEFROM' and \
                        len(rule) == 3 and type(arg1) is str:
                            pos_ini = value.find(arg1)
                            if pos_ini != -1:
                                rec[field] = value[:pos_ini]
                    elif operation.upper() == 'REMOVETO' and \
                        len(rule) == 3 and type(arg1) is str:
                            pos_ini = value.find(arg1)
                            if pos_ini != -1:
                                rec[field] = value[pos_ini:]                                                                                                                                
        return(rec)

    def ShowError(self):
        '''Show errors
                
        Returns a string with the errors
        
        >>> rap1.ShowError()
        '''         
        if self.number_errors != 0:
            return('Errors: ' + ''.join(map(str, self.errors)))
        else:
            return('')

#-------------------------------------------------------------------------
#
# clase: Reptar()
#
#-------------------------------------------------------------------------

class Reptar(object):
    '''
    This class allows you to merge files, including only the necessary
    lines.
    '''
    app_folder = os.getcwd() + '/'
    def __init__(self):
        '''Initialize a .rep template
        
        Attribute List:
        
        - description: short descripton of .rap template
        - extension: extension of the files to read
        - prefix: files must begin with this string
        - input_folder: folder of files to read
        - output_folder: output folder to save file with result
        - output_file: output filename
        - delimiter: delimiter character
        - quotechar: quote character
        - include_header: '0' or '1'->header is the first line of the first file
        - include_file: '0' or '1'
        - include_record_num: '0' or '1'
        - header: text of the report header
        - alternate_header: alternative text of the report header
        - fields: dictionary with fieldnames and search (read template)                  
        - record: dictionary with fieldnames and values (read template)
        - lines: List of rules to include or exclude lines (read template)
        - rules: list of rules (read template)
        - list_files: list of filenames to read (auto)
        - record_counter: number of records (auto)        
        - errors: list of errors (auto)
        - number_errors: number of errors after you open or save a template
                    
        >>> rep1 = Reptar()
        
        '''     
        self.description = ''
        self.extension = 'txt'
        self.prefix = ''
        self.input_folder = Reptar.app_folder
        self.output_folder = Reptar.app_folder
        self.output_file = 'output.txt'
        self.delimiter = ''
        self.quotechar = '"'
        self.include_header = '1'
        self.include_file = '0'
        self.include_record_num = '0'
        self.include_empty_record = '0'
        self.header = ''
        self.alternate_header = ''
        self.lines = []
        self.rules = []
        self.list_files = []
        self.errors = []
        self.number_errors = 0
        self.record_counter = 0
            
    def Open(self, name):
        '''Open .rep template
        
        name -- .rep template name
        
        >>> rep1.Open('template.rep')
        '''
        self.errors = []        
        if os.path.exists(name):
            config_file = configparser.ConfigParser()
            config_file.read(name)
            if config_file.has_option('General','description'):
                self.description = config_file['General']['description']
            else:
                self.description = ''
            if config_file.has_option('General','extension'):
                self.extension = config_file['General']['extension']
            else:
                self.extension = "txt"
            if config_file.has_option('General','prefix'):
                self.prefix = config_file['General']['prefix']
            else:
                self.prefix = ''
            if config_file.has_option('General','input_folder') and \
                os.path.exists(config_file['General']['input_folder']):
                self.input_folder = config_file['General']['input_folder'] + '/'
            else:
                self.input_folder = Reptar.app_folder
                self.errors.append('No source folder. ')
            if config_file.has_option('General','output_folder') and \
                os.path.exists(config_file['General']['output_folder']):
                self.output_folder = config_file['General']['output_folder'] + '/'
            else:
                self.output_folder = Reptar.app_folder
                self.errors.append('No target folder. ')
            if config_file.has_option('General','output_file') and \
                config_file['General']['output_file'] != '':
                self.output_file = self.output_folder + config_file['General']['output_file']
            else:
                self.output_file = self.output_folder + "output.txt"                
            if config_file.has_option('General','delimiter') and \
                config_file['General']['delimiter'] != '':
                self.delimiter = config_file['General']['delimiter']
            else:
                self.delimiter = ''
            if config_file.has_option('General','quotechar') and \
                config_file['General']['quotechar'] != '':
                self.quotechar = config_file['General']['quotechar']
            else:
                self.quotechar = '"'                
            if config_file.has_option('General','include_header') and \
                config_file['General']['include_header'] in ['0','1'] :
                self.include_header = config_file['General']['include_header']
            else:
                self.include_header = '1'
            if config_file.has_option('General','include_file') and \
                config_file['General']['include_file'] in ['0','1']:
                self.include_file = config_file['General']['include_file']
            else:
                self.include_file = '0'
            if config_file.has_option('General','include_record_num') and \
                config_file['General']['include_record_num'] in ['0','1']:
                self.include_record_num = config_file['General']['include_record_num']
            else:
                self.include_record_num = '0'
            if config_file.has_option('General','include_empty_record') and \
                config_file['General']['include_empty_record'] in ['0','1']:
                self.include_empty_record = config_file['General']['include_empty_record']
            else:
                self.include_empty_record = '0'                
            if config_file.has_option('General','alternate_header'):
                self.alternate_header = config_file['General']['alternate_header']
            else:
                self.alternate_header = ''

            self.lines = []
            if 'Lines' in config_file:  
                for option, value in config_file['Lines'].items():
                    if option.upper().startswith('LINE') and len(option) > 4 and \
                        option[4:].strip().isnumeric():
                            value = eval(value)
                            if type(value) is tuple and len(value) > 0:
                                self.lines.append(value)

            self.rules = []
            if 'Rules' in config_file:  
                for option, value in config_file['Rules'].items():
                    if option.upper().startswith('RULE') and len(option) > 4 and \
                        option[4:].strip().isnumeric():
                            value = eval(value)
                            if type(value) is tuple and len(value) > 0:
                                self.rules.append(value)

        self.list_files = []            
        if len(self.errors) == 0:
            list_file = os.listdir(self.input_folder)
            for actual_file in list_file:
                if actual_file[-3:].upper() == self.extension.upper():
                    if actual_file.startswith(self.prefix):
                        self.list_files.append(actual_file)
            
            if len(self.list_files) > 0:
                self.list_files.sort()
            else:
                self.errors.append('No file/s to search. ')
        self.number_errors = len(self.errors)

    def Save(self, name):
        '''It saves .rep template
        
        name -- .rep template name
        
        >>> rep1.Save('template.rep')
        '''
        self.errors = []        
        config_file = configparser.ConfigParser()       
        if os.path.exists(name) == False:

            config_file['General'] = {}
            config_file['Lines'] = {}
            config_file['Rules'] = {}
            general = config_file['General']
            lines = config_file['Lines']
            rules = config_file['Rules']
            general['description'] = self.description
            general['extension'] = self.extension
            general['prefix'] = self.prefix
            general['output_folder'] = self.output_folder
            general['input_folder'] = self.input_folder
            general['output_file'] = self.output_file           
            general['delimiter'] = self.delimiter
            general['quotechar'] = self.quotechar
            general['include_header'] = self.include_header
            general['include_file'] = self.include_file
            general['include_record_num'] = self.include_record_num
            general['include_empty_record'] = self.include_empty_record
            general['alternate_header'] = self.alternate_header

            for position in range(len(self.lines)):
                lines['line' + str(position+1)] = str(self.lines[position])

            for position in range(len(self.rules)):
                rules['rule' + str(position+1)] = str(self.rules[position])
            
            with open(name, 'w') as output_config:
                config_file.write(output_config)

        else:
            self.errors.append('The .rep template exists. ')
        self.number_errors = len(self.errors)
    
    def BuildHeader(self, row):
        '''Build header
        
        Returns header
        
        >>> rep1.BuildHeader()
        '''
        if self.number_errors == 0:
            if self.alternate_header == '':
                current_file = open(self.input_folder + row, 'rb')
                current_line = current_file.readline()
                current_line = current_line.decode("utf-8", "ignore")
                if not current_line:
                    self.header = ''
                else:
                    self.header = current_line
                current_file.close()                
                if self.include_file == '1':
                    self.header = 'f___n' + self.delimiter + current_line               
                if self.include_record_num == '1':                    
                    self.header = 'r___n' + self.delimiter + self.header
                return(self.header.rstrip())
            else:
                return(self.alternate_header.rstrip())            
        else:
            return('')

    def BuildRow(self, current_line, row):
        '''Buid row (line)
        
        current_line -- line (string)
        row -- filename to search
        
        Returns value of empty line: True/False and
                dictionary with field names and data
        
        >>> rap1.BuildRow(current_line, filename)
        '''
        if self.number_errors == 0:
            current_line = current_line.rstrip()
            if self.include_empty_record == '0' and current_line == '':
                include = False
            else:
                if len(self.lines) != 0 and \
                (self.lines[0][0] == "INCLUDE" or \
                self.lines[0][0] == "INCLUDEND" or \
                self.lines[0][0] == "INCLUDRE"):
                    include = False
                else:
                    include = True                
                for line in self.lines:
                    if len(line) > 0 and len(line) < 4:
                        operation = line[0]                    
                        if len(line) > 1:
                            arg1 = line[1]
                        if len(line) > 2:
                            arg2 = line[2]
                        if operation.upper() == 'EXCLUDE' and \
                           len(line) == 2 and type(arg1) is str:
                               if arg1 in current_line:
                                   include = False
                        elif operation.upper() == 'EXCLUDEND' and \
                           len(line) == 2 and type(arg1) is str:
                               if current_line.endswith(arg1):
                                   include = False
                        elif operation.upper() == 'EXCLUDRE' and \
                           len(line) == 3 and type(arg1) is str and \
                           type(arg2) is str and arg2 in ['0','1']:
                               if arg2 == '0':
                                   patt = re.compile(arg1)
                               else:
                                   patt = re.compile(arg1, re.I)                                    
                               if patt.search(current_line)!=None:
                                   include = False
                        elif operation.upper() == 'INCLUDE' and \
                           len(line) == 2 and type(arg1) is str:
                               if arg1 in current_line:
                                   include = True
                        elif operation.upper() == 'INCLUDEND' and \
                           len(line) == 2 and type(arg1) is str:                               
                               if current_line.endswith(arg1):                                   
                                   include = True
                        elif operation.upper() == 'INCLUDRE' and \
                           len(line) == 3 and type(arg1) is str and \
                           type(arg2) is str and arg2 in ['0','1']:
                               if arg2 == '0':
                                   patt = re.compile(arg1)
                               else:
                                   patt = re.compile(arg1, re.I)
                               if patt.search(current_line):
                                   include = True                                    
                if include == True:
                    if self.include_file == '1':
                        current_line = row + self.delimiter + current_line                        
                    if self.include_record_num == '1':
                        self.record_counter +=1
                        current_line = str(self.record_counter) + self.delimiter \
                        + current_line                                            
        return(include, current_line)

    def ApplyRules(self, current_line):
        '''Apply rules (changes data)
        
        current_line -- string
        
        Returns string updated
        
        >>> rap1.ApplyRules(string)
        
        Functions available for rules:
        
        - rule1 = ('line', 'SUBSTR', postion_initial, lenght)
        - rule1 = ('line', 'REPLACE', 'search_string', 'replace_string')
        - rule1 = ('line', 'REPLACEALL', 'search_string', 'replace_string')
        - rule1 = ('line', 'UPPER')
        - rule1 = ('line', 'LOWER')
        - rule1 = ('line', 'REVERSE')
        - rule1 = ('line', 'REMOVEFROM', 'string')
        - rule1 = ('line', 'REMOVETO', 'string')
        - rule1 = ('line', 'REMOVECOL, column)
        
        '''         
        if self.number_errors == 0:
            for rule in self.rules:                     
                if len(rule) > 1 and len(rule) < 5 and rule[0].upper() == 'LINE':
                    operation = rule[1]
                    if len(rule) > 2:
                        arg1 = rule[2]
                    if len(rule) > 3:
                        arg2 = rule[3]                                                          
                    if operation.upper() == 'SUBSTR' and \
                        len(rule) == 4 and type(arg1) is int and \
                        type(arg2) is int and \
                        len(current_line) >= arg1 + arg2 - 1:
                            current_line = current_line[arg1-1:arg2].strip()                         
                    elif operation.upper() == 'REPLACE' and \
                        len(rule) == 4 and type(arg1) is str and \
                        type(arg2) is str:
                            current_line = current_line.replace(arg1, arg2, 1)
                    elif operation.upper() == 'REPLACEALL' and \
                        len(rule) == 4 and type(arg1) is str and \
                        type(arg2) is str:
                            current_line = current_line.replace(arg1, arg2)
                    elif operation.upper() == 'UPPER':
                        current_line = current_line.upper()                      
                    elif operation.upper() == 'LOWER':
                        current_line = current_line.lower()
                    elif operation.upper() == 'REVERSE':
                        current_line = current_line[::-1]
                    elif operation.upper() == 'REMOVEFROM' and \
                        len(rule) == 3 and type(arg1) is str:
                            pos_ini = current_line.find(arg1)
                            if pos_ini != -1:
                                current_line = current_line[:pos_ini]
                    elif operation.upper() == 'REMOVETO' and \
                        len(rule) == 3 and type(arg1) is str:
                            pos_ini = current_line.find(arg1)
                            if pos_ini != -1:
                                current_line = current_line[pos_ini:]
                    elif operation.upper() == 'REMOVECOL' and \
                        len(rule) == 3 and type(arg1) is int:
                            if self.delimiter in [',', '.', ':', ';', '|', '#']:
                                col   = int(arg1)
                                items = current_line.count(self.delimiter)
                                iter_matches = re.finditer('\\'+ self.delimiter, 
                                                           current_line)
                                elnum = 0
                                lim_lower = -1
                                lim_upper = -1
                                for located in iter_matches:
                                    elnum+=1
                                    if col == 1 and items >= 1:
                                        lim_lower = 0
                                        lim_upper = located.span()[1]
                                    elif col == items + 1 and elnum + 1 == col:
                                        lim_lower = located.span()[0]
                                        lim_upper = len(cadena)        
                                    elif col - elnum == 1:
                                        lim_lower = located.span()[1]
                                    elif col == elnum:
                                        lim_upper = located.span()[1]
                                    if lim_lower != -1 and lim_upper != -1:
                                        current_line = current_line[0:lim_lower] + \
                                        current_line[lim_upper:]
                                        break                                
        return(current_line.rstrip())

    def ShowError(self):
        '''Show errors
                
        Returns a string with the errors
        
        >>> rep1.ShowError()
        '''         
        if self.number_errors != 0:
            return('Errors: ' + ''.join(map(str, self.errors)))
        else:
            return('')

