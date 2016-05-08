#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# name:        create_csv_from_columns.py (Python 3.x)
# description: Creates .csv file with data from multiple text files
#              with data in columns  
# author:      Antonio Suárez Jiménez, pherkad13@gmail.com
# date:        08-05-2016
#
#--------------------------------------------------------------------

__author__ = 'Antonio Suárez Jiménez, pherkad13@gmail.com'
__title__= 'create_csv_from_columns'
__date__ = '2016-05-08'
__version__ = '0.2.4'
__license__ = 'GNU GPLv3'

from pysaurio import Raptor
import csv
        
def main():
    
    # Creates and saves a new .rap template (If the template exists it is not saved)
                    
    rap1 = Raptor()       
    rap1.description = 'Get list of users with data in columns'
    rap1.extension = 'log'
    rap1.prefix = 'PC'
    rap1.input_folder = 'txt'
    rap1.output_folder = 'txt'
    rap1.output_file = 'users_from_columns.csv'
    rap1.delimiter = ','
    rap1.quotechar = '"'
    rap1.include_header = '1'
    rap1.include_file = '0'
    rap1.include_record_num = '1'
    rap1.search_multiple = '1'
    rap1.fields['user'] = 'User='
    rap1.fields['name'] = 'Name='
    rap1.fields['os'] = 'OS='
    rap1.fields['ip'] = 'IP='
    rap1.rules.append(('user', 'UPPER'))
    rap1.rules.append(('user', 'SUBSTR', 1, 6))
    rap1.rules.append(('os', 'REMOVEFROM', ' '))
    rap1.Save("users_columns.rap")
    del rap1

    # Opens .rap template and creates .csv file from the data read from multiple text files
    
    rap2 = Raptor()
    rap2.Open('users_columns.rap')
    if rap2.number_errors == 0:         
        file_csv = open(rap2.output_file, 'w', newline='')
        csv_output = csv.writer(file_csv, 
                                delimiter=rap2.delimiter,
                                quotechar=rap2.quotechar, 
                                quoting=csv.QUOTE_MINIMAL)
        if rap2.include_header == '1':
            fields_list = rap2.BuildHeader()
            print(fields_list)
            csv_output.writerow(fields_list)
                            
        for row in rap2.list_files:
            valid_record, new_record = rap2.BuildRow(row)
            new_record = rap2.ApplyRules(new_record)            
            new_record = list(new_record.values())
            if valid_record:
                print(new_record)
                csv_output.writerow(new_record)         
        file_csv.close()            
    else:
        print(rap2.ShowError())
    del rap2
    return 0

if __name__ == '__main__':
    main()

