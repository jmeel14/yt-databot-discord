from . import cmd_main


from re import search as re_s
from re import escape as re_e

from os.path import dirname as file_loc
from json import loads

from datetime import datetime

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

def grab_playlist_id(playlist_link):
    playlist_return_id = None
    try:
        if "youtube.com" in playlist_link:
            playlist_return_id = [re_res for re_res in re_s(
                re_e("youtube.com/playlist?list=") + "([^&]*)&?|" + re_e("youtube.com/watch?v=") + "[^&]*&?[^&]*?&list\=([^&]*)&?",
                playlist_link
            ).groups() if re_res][0]
            return playlist_return_id
    except Exception as URLParseError:
        print(URLParseError)
        return None

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if len(cmd_str.split(" ")) > 1:
        init_embed = cmd_main.Embed(
            title = "Playlist Command Received",
            description = "Your command has been received by the bot. Please wait as your request gets processed."
        )
        init_msg = await msg_obj.channel.send(None, embed = init_embed)
        cmd_args = cmd_str.split(" ")
        if len(cmd_str.split(" ")) == 2:
            fetch_playlist_id = grab_playlist_id(cmd_args[1])
            if fetch_playlist_id:
                req_API = await kwargs["self_http"].get(
                    req_build(
                        'playlists?part=snippet,contentDetails&id={0}'.format(fetch_playlist_id),
                        True
                    )
                )
                if req_API.status == 200:
                    try:
                        large_result = loads(await req_API.text())["items"]
                        if len(large_result) >= 1:
                            targ_result = large_result[0]["snippet"]
                            targ_result_content = large_result[0]["contentDetails"]
                            if len(targ_result["description"]) <= 2:
                                changed_desc = "_No description was provided for this playlist._"
                            elif len(targ_result["description"]) > 560:
                                changed_desc = targ_result["descripton"][:560] + "..."
                            else:
                                changed_desc = targ_result["description"]
                            output_embed = cmd_main.Embed(
                                title = targ_result["title"],
                                description = changed_desc,
                                colour = 0xDD2222
                            )
                            output_embed.add_field(
                                name = "View Playlist",
                                value = "[YouTube](https://youtube.com/playlist?list={0})".format(
                                    fetch_playlist_id
                                ),
                                inline = True
                            )
                            output_embed.add_field(
                                name = "Playlist length",
                                value = "{0} video(s)".format(targ_result_content["itemCount"])
                            )
                            output_embed.set_thumbnail(
                                url = targ_result["thumbnails"]["default"]["url"]
                            )
                            req_API_channel = await kwargs["self_http"].get(
                                req_build(
                                    'channels?part=snippet&id={0}'.format(targ_result["channelId"]), True
                                )
                            )
                            channel_resp = loads(await req_API_channel.text())["items"][0]
                            try:
                                output_embed.set_footer(
                                    text = "{0} | Published {1}".format(
                                        targ_result["channelTitle"],
                                        datetime.strptime(
                                            targ_result["publishedAt"][:-5],
                                            '%Y-%m-%dT%H:%M:%S'
                                        )
                                    ),
                                    icon_url = channel_resp["snippet"]["thumbnails"]["default"]["url"]
                                )
                            except:
                                output_embed.set_footer(
                                    text = "{0} | Published {1}".format(
                                        targ_result["channelTitle"],
                                        datetime.strptime(
                                            targ_result["publishedAt"][:-5],
                                            '%Y-%m-%dT%H:%M:%S'
                                        )
                                    ),
                                    icon_url = "https://i.imgur.com/YxrOhoy.png"
                                )
                        else:
                            output_embed = cmd_main.err_embed(
                                "Playlist Request Error",
                                "There were no results for your playlist request. Please try again later.",
                                "API Response - No Results"
                            )
                    except Exception as PlaylistResponseError:
                        output_embed = cmd_main.err_embed(
                            "Playlist Response Error",
                            "Unfortunately, the API returned a response that the bot was not ready for.\nPlease let the developer know of this issue using the `suggest` command.",
                            "API Response - Unexpected"
                        )
                        print(PlaylistResponseError)
                else:
                    output_embed = cmd_main.err_embed(
                        "Playlist Request Error",
                        "The playlist you requested could not be found. It may have been removed, changed location, or typed by you incorrectly.",
                        "API Response - Page Not Found"
                    )
            else:
                output_embed = cmd_main.err_embed(
                    "Playlist Request Parse Error",
                    "The playlist URL that you provided could not be used to send a request. Please check to make sure the URL is correct and try again.",
                    "Malformed playlist URL error"
                )
    await init_msg.delete()
    return {
        "output_msg": await msg_obj.channel.send(None, embed = output_embed),
        "output_admin": False
    }

cmd_playlist = cmd_main.Command(
    "Playlist",
    "playlist plist pl",
    {
        "global": {
            "output_syntax": "{0} `<playlist URL>`",
            "output_description": "Retrieves information about a playlist."
        }
    },
    "Retrieves general information of a YouTube playlist.",
    cmd_func,
    False
)