import csv


def get_check_list(fp_in_dict, fp_in_csv, fp_out):
    saved = dict()
    with open(fp_in_csv, 'r') as c:
        csvreader = csv.reader(c)
        for row in csvreader:
            saved[row[0]] = ''
    with open(fp_in_dict, 'r') as d:
        original = [line.strip() for line in d]
    with open(fp_out, 'w') as o:
        [o.write(line + '\n') for line in original if line not in saved]
