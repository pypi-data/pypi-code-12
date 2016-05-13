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


def check_progress(saved, original, **kwargs):
    saved_index = kwargs.get('saved_index', 0)
    original_index = kwargs.get('original_index', 0)

    row = []
    with open(saved, 'r') as s:
        csvreader = csv.reader(s)
        for row in csvreader:
            pass
    progress = row[saved_index]


    with open(original, 'r') as i:
        csvreader = csv.reader(i)
        is_start = False
        for row in csvreader:
            if is_start:
                with open(original + '2', 'a') as o:
                    csvwriter = csv.writer(o)
                    csvwriter.writerow(row)
            else:
                if progress == row[original_index]:
                    is_start = True