#!/usr/bin/python3

def csv_as_dict(file, ref_header, delimiter=None):
    """
    http://stackoverflow.com/questions/14091387/creating-a-dictionary-from-a-csv-file
    :param file: Input csv file
    :param ref_header: Column name reference for each key
    :param delimiter: separator to read the csv

    :return: dict with csv content, first row with headers in lowercase
    """
    import csv
    import itertools

    # Function to make first row lower
    def lower_first(iterator):
        return itertools.chain([next(iterator).lower()], iterator)

    if not delimiter:
        delimiter = ';'

    reader = csv.DictReader(lower_first(open(file, encoding='utf-8')), delimiter=delimiter)

    result = {}
    for row in reader:
        key = row.pop(ref_header.lower())
        if key in result:
            # implement your duplicate row handling here
            pass
        result[key] = row
    return result


def save_csv_data(csv_rows=None, csv_filename='test.csv', csv_delimiter=','):
    """

    :param csv_rows: python list with rows
    :param csv_filename: output file
    :param csv_delimiter: output separator to use as delimiter
    :return: None
    """
    import csv
    import os
    if not csv_filename:
        return 'No csv_file selected'
    if not csv_rows:
        return 'There are no csv rows to write'
    print('saving to csv file:', csv_filename)
    csv_file_obj = open(csv_filename, 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file_obj, delimiter=csv_delimiter)
    for row in csv_rows:
        csv_writer.writerow(row)
    csv_file_obj.close()
    if csv_filename:
        if os.path.isfile(csv_filename):
            print('exported to:', csv_filename)


def get_csv_from_url(csv_url, csv_output='output.csv', delimiter=','):
    """

    :param csv_url: url to get the csv
    :param csv_output: path to output the csv
    :param delimiter: delimiter of the csv
    :return:
    """
    import csv
    from urllib import request
    import io
    import os
    url = csv_url
    try:
        response = request.urlopen(url)
    except:
        return None
    datareader = csv.reader(io.TextIOWrapper(response, encoding='utf-8'), delimiter=delimiter)  # Read csv from urlopen
    save_csv_data(datareader, csv_filename=csv_output, csv_delimiter=delimiter)
    if os.path.isfile:
        return "file saved to: ", csv_output