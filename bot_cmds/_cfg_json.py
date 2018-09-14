from json import loads as json_ls
from json import dumps as json_ds

def read_json(json_file):
    json_o = open(json_file, 'r')
    json_r = json_o.read()
    json_o.close()

    json_l = json_ls(json_r)
    return json_l

def write_json(json_file, json_content):
    op_file = open(json_file, 'w')
    op_file.write(json_ds(json_content))
    op_file.close()

    return True
