from . import cmd_main


from re import search as re_s
from re import escape as re_e

from os.path import dirname as file_loc
from json import loads

STR_FILE = str(file_loc(__file__))
STR_AUTH_FILE = STR_FILE + '/../bot_config/cfg_data/authorization.json'
API_URL = "https://www.googleapis.com/youtube/v3/"

def req_build(api_req, reqs_auth):
    token_file = open(STR_AUTH_FILE)
    token = loads(token_file.read())
    ret_str = API_URL + api_req
    if reqs_auth:
        return  ret_str + "&key=" + token["yt_key"]
    else:
        return ret_str

def grab_vid_id(vid_link):
    vid_return_id = None
    try:
        if "youtube.com" in vid_link or "youtu.be" in vid_link:
            vid_id_iterated = [re_res for re_res in re_s(
                re_e("youtube.com/watch?v=") + "([^&]*)&?|youtu.be\\/([^?]*)\??",
                vid_link
            ).groups() if re_res != None][0]
            return vid_id_iterated
    except Exception as URLParseError:
        print(URLParseError)
        return None

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if len(cmd_str.split(" ")) == 2:
        cmd_split = cmd_str.split(" ")
        fetch_vid_id = grab_vid_id(cmd_split[1])
        if fetch_vid_id:
            req_API = await kwargs["self_http"].get(
                req_build(
                    'videos?part=snippet,statistics&id={0}'.format(fetch_vid_id),
                    True
                )
            )
            if req_API.status == 200:
                targ_result = loads(await req_API.text())["items"][0]
                desc_str = targ_result["snippet"]["description"]
                if len(desc_str) > 560:
                    desc_str = desc_str[:560] + "..."
                output_embed = cmd_main.Embed(
                    title = targ_result["snippet"]["title"],
                    description = desc_str,
                    colour = 0xDD2222
                )
                output_embed.add_field(
                    name = "Views",
                    value = "{:,}".format(int(targ_result["statistics"]["viewCount"]))
                )
                output_embed.add_field(
                    name = "Likes",
                    value = "{:,}".format(int(targ_result["statistics"]["likeCount"])),
                    inline = False
                )
                output_embed.add_field(
                    name = "Dislikes",
                    value = "{:,}".format(int(targ_result["statistics"]["dislikeCount"])),
                    inline = True
                )
                output_embed.set_image(url=targ_result["snippet"]["thumbnails"]["high"]["url"])

                req_API_channel = await kwargs["self_http"].get(
                    req_build(
                        'channels?part=snippet&id={0}'.format(targ_result["snippet"]["channelId"]), True
                    )
                )
                channel_resp = loads(await req_API_channel.text())["items"][0]
                output_embed.set_footer(
                    text = targ_result["snippet"]["channelTitle"],
                    icon_url = channel_resp["snippet"]["thumbnails"]["default"]["url"]
                )
                await msg_obj.channel.send(None, embed = output_embed)
            else:
                output_embed = cmd_main.err_embed(
                    "Video Fetch Failure",
                    "Your request could not be accepted. Please try again later.",
                    "API Response - Page Not Found"
                )
        else:
            output_embed = cmd_main.err_embed(
                "Video Fetch Failure",
                "The URL that you provided could not be used to send a request. Please check to make sure the URL is correct and try again.",
                "Invalid Link Error"
            )
            return {
                "output_msg": await msg_obj.channel.send(None, embed = output_embed),
                "output_admin": False
            }
    else:
        cmd_split = cmd_str.split(" ")
        cmd_arg = cmd_split[2]
        print(cmd_arg)

cmd_video = cmd_main.Command(
    "Video",
    "video videosearch vidsearch vs",
    {
        "global": {
            "output_syntax": "{0} <OPTIONAL tags/fulldesc/restrictions> <video URL>",
            "output_description": "Retrieves information about a video, in respect to the given argument."
        },
        "tags": {
            "output_syntax": "{0} <video URL>",
            "output_description": "Retrieves the tags of a specified video URL."
        }
    },
    "Retrieves general information of a video",
    cmd_func,
    False
)