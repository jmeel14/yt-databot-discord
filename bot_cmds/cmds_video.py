from . import cmd_main


from re import search as re_s
from re import escape as re_e

from os.path import dirname as file_loc
from json import loads

STR_FILE = str(file_loc(__file__))
STR_AUTH_FILE = STR_FILE + '\\..\\bot_config\\cfg_data\\authorization.json'
API_URL = "https://www.googleapis.com/youtube/v3"

def req_build(api_req):
    token_file = open(STR_AUTH_FILE)
    token = loads(token_file.read())
    return API_URL + api_req + "&key=" + token["yt_key"]

def grab_vid_id(vid_link):
    vid_return_id = None
    try:
        if "youtube.com" in vid_link or "youtu.be" in vid_link:
            vid_id_group = re_s(
                re_e("youtube.com/watch?v=") + "(.*)\\?|youtu.be\\/(.*)\\?",
                vid_link
            )
            print(vid_id_group)
    except Exception as URLParseError:
        print(URLParseError)
        return None

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if len(cmd_str.split(" ")) == 2:
        cmd_split = cmd_str.split(" ")
        grab_vid_id(cmd_split[1])

cmd_video = cmd_main.Command(
    "Video",
    "video videosearch vidsearch vs",
    "Retrieves general information of a video",
    cmd_func,
    False
)