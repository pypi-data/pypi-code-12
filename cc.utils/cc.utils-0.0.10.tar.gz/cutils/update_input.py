
def update_input(fp, target_line):
    with open(fp, 'r') as i:
        lines = [line.strip() for line in i]
    line_index = lines.index(target_line)
    with open(fp + '_', 'a') as o:
        [o.write(line + '\n') for line in lines[(line_index + 1):]]


# update_input('/Users/cchen224/Downloads/user_ids_1', '401106225')