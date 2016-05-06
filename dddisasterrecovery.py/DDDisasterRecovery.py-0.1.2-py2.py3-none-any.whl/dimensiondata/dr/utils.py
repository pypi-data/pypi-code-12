import click
import csv


def handle_click_http_exception(e):
    click.secho("{0}".format(e), fg='red', bold=True)
    exit(1)


def get_vm_mapping_from_file(filename):
    dc_dict = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_dc = row['Source_MCP']
            source_vm = row['Source_VM_Name']
            target_dc = row['Target_MCP']
            target_vm = row['Target_VM_Name']
            if source_dc not in dc_dict:
                dc_dict[source_dc] = {}
            if target_dc not in dc_dict:
                dc_dict[target_dc] = {}
            dc_dict[source_dc][source_vm] = {'vm': target_vm,
                                             'dc': target_dc}
            dc_dict[target_dc][target_vm] = {'vm': source_vm,
                                             'dc': source_dc}

    return dc_dict
