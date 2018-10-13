from os.path import dirname as file_loc
from json import loads as json_l

STR_FILE = str(file_loc(__file__))
STR_AUTH_FILE = STR_FILE + '/../bot_config/cfg_data/authorization.json'
API_URL = "https://www.googleapis.com/youtube/v3/"

def req_build(api_req, reqs_auth):
    token_file = open(STR_AUTH_FILE)
    token = json_l(token_file.read())
    ret_str = API_URL + api_req
    if reqs_auth:
        return  ret_str + "&key=" + token["yt_key"]
    else:
        return ret_str
