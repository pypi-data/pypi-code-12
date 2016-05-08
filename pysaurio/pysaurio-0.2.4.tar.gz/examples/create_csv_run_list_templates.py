#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# name:        create_csv_run_list_templates.py (Python 3.x)
# description: Run a list of .rap templates
# author:      Antonio Suárez Jiménez, pherkad13@gmail.com
# date:        08-05-2016
#
#--------------------------------------------------------------------

__author__ = 'Antonio Suárez Jiménez, pherkad13@gmail.com'
__title__= 'create_csv_run_list_templates'
__date__ = '2016-05-08'
__version__ = '0.2.4'
__license__ = 'GNU GPLv3'

from pysaurio import Raptor
import csv
        
def main():
    
    # Declares Python list with .rap templates
                    
    rap_templates = ['users.rap',
                     'users_columns.rap',
                     'users_and_filename.rap']
                     
    objects = [Raptor() for index in range(len(rap_templates))]

    # Uses one by one all the objects
    
    for number_object in range(len(objects)):
        current_rap = rap_templates[number_object]
        current_object = objects[number_object]
        print('Template:', current_rap)

        # Opens .rap template for current object and creates .csv file
            
        current_object.Open(current_rap)        
        if current_object.number_errors == 0:           
            file_csv = open(current_object.output_file, 'w', newline='')
            csv_output = csv.writer(file_csv, 
                                    delimiter=current_object.delimiter,
                                    quotechar=current_object.quotechar, 
                                    quoting=csv.QUOTE_MINIMAL)
            if current_object.include_header == '1':
                fields_list = current_object.BuildHeader()
                print(fields_list)
                csv_output.writerow(fields_list)
                                
            for row in current_object.list_files:
                valid_record, new_record = current_object.BuildRow(row)
                new_record = current_object.ApplyRules(new_record)
                if valid_record:                    
                    new_record = list(new_record.values())
                    print(new_record)
                    csv_output.writerow(new_record)         
            file_csv.close()            
        else:
            print(current_object.ShowError())
        del current_object
    return 0

if __name__ == '__main__':
    main()

