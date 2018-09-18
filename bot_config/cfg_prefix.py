from re import search as re_s
from re import escape as re_e
from json import loads as json_ls
from os.path import dirname as file_loc

from ._cfg_json import read_json

STR_FILE = str(file_loc(__file__))
STR_PREF_FILE = STR_FILE + '/cfg_data/prefix.json'

def check_prefix(msg_obj, is_DM):
    """Reads config file to determine prefix, else faults to hardcoded prefix"""
    check_srv = None
    if not is_DM:
        check_srv = str(msg_obj.guild.id)

        pref_json_l = read_json(STR_PREF_FILE)

    try:
        try:
            return re_e(pref_json_l[check_srv])
        except:
            return re_e(pref_json_l["default"])
    except:
        return "\~j14 "
