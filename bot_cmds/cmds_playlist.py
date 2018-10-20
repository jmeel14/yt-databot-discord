from . import cmd_main

from ._cmd_generate_API_request import req_build
from ._cmd_channel_footer import generate_channel_footer
from ._cmd_get_parameter_id import grab_playlist_id

from re import search as re_s
from re import escape as re_e

from json import loads

from datetime import datetime

import traceback

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if len(cmd_str.split(" ")) > 1:
        init_embed = cmd_main.Embed(
            title = "Playlist Command Received",
            description = "Your command has been received by the bot. Please wait as your request gets processed."
        )
        init_msg = await msg_obj.channel.send(None, embed = init_embed)
        async with msg_obj.channel.typing():
            cmd_args = cmd_str.split(" ")
            if len(cmd_args) == 2:
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
                                
                                output_embed = await generate_channel_footer(
                                    output_embed,
                                    targ_result["channelId"],
                                    self_http = kwargs["self_http"],
                                    published_footer = { "published_at": targ_result["publishedAt"] }
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
            else:
                """if cmd_args[1] == "videos":
                    req_build(
                        "playlists?part=snippet,"
                    )  TODO - Make this thing work
                """
                output_embed = cmd_main.err_embed(
                    "Feature coming soon",
                    "Arguments for this command are currently not ready, and will be here soon. Please look forward to their arrival!",
                    "Coming soon..."
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