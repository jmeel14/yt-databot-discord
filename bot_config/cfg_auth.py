from os.path import dirname as file_loc
from . import _cfg_json

STR_FILE = str(file_loc(__file__))
STR_AUTH_FILE = STR_FILE + '.\\cfg_data\\authorization.json'

def get_data(data_ref, is_extended, **kwargs):
    auth_dict = _cfg_json.read_json(STR_AUTH_FILE)
    if is_extended:
        try:
            return auth_dict[kwargs["extended_prop"]][data_ref]
        except Exception as ExtendedDataException:
            raise ExtendedDataException
    else:
        try:
            return auth_dict[data_ref]
        except Exception as DataException:
            raise DataException