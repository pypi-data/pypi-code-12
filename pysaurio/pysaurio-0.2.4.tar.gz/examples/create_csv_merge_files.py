#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# name:        merge_files.py (Python 3.x)
# description: Create a file with data from multiple text files  
# author:      Antonio Suárez Jiménez, pherkad13@gmail.com
# date:        08-05-2016
#
#--------------------------------------------------------------------

__author__ = 'Antonio Suárez Jiménez, pherkad13@gmail.com'
__title__= 'merge_files_csv'
__date__ = '2016-05-08'
__version__ = '0.2.4'
__license__ = 'GNU GPLv3'

from pysaurio import Reptar
        
def main():
    
    # Creates and saves a new .rep template (If the template exists it is not saved)
                    
    rep1 = Reptar()       
    rep1.description = 'Get list of users GNU/Linux, except Marta'
    rep1.extension = 'txt'
    rep1.prefix = 'PCS'
    rep1.input_folder = 'txt'
    rep1.output_folder = 'txt'
    rep1.output_file = 'merge_files.csv'
    rep1.delimiter = ','
    rep1.include_header = '1'
    rep1.include_file = '1'
    rep1.include_record_num = '1'
    rep1.alternate_header = ''
    rep1.lines.append(('INCLUDE', 'GNU/Linux'))
    rep1.lines.append(('INCLUDRE', '^Co205', '1'))  
    rep1.lines.append(('EXCLUDE', 'Marta'))
    rep1.lines.append(('EXCLUDRE', 'MADRID', '0'))
    rep1.lines.append(('INCLUDEND', '8'))
    rep1.rules.append(('line', 'UPPER'))
    rep1.rules.append(('line', 'REPLACE', '140', '136'))
    rep1.Save("merge_files.rep")
    del rep1

    # Opens .rep template and creates file from the data read from multiple text files
    
    rep2 = Reptar()
    rep2.Open('merge_files.rep')
    if rep2.number_errors == 0:         
        file_csv = open(rep2.output_file, 'w')
        if rep2.include_header == '1':
            header = rep2.BuildHeader(rep2.list_files[0])
            print(header)
            file_csv.write(header + "\n")
                                    
        for row in rep2.list_files:
            current_file = open(rep2.input_folder + row, 'rb')
            while True:
                new_record = current_file.readline()
                new_record = new_record.decode("utf-8", "ignore")
                if not new_record: break
                valid_record, new_record = rep2.BuildRow(new_record, row)
                if valid_record:
                    new_record = rep2.ApplyRules(new_record)
                    print(new_record)
                    file_csv.write(new_record + "\n")
            current_file.close()
        file_csv.close()            
    else:
        print(rep2.ShowError())
    del rep2
    return 0

if __name__ == '__main__':
    main()
