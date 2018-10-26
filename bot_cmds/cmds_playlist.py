from re import search as re_s
from re import escape as re_e
from json import loads
from datetime import datetime
import traceback

from . import cmd_main

from .cmd_fragments._generate_API_request import req_build
from .cmd_fragments._channel_footer import generate_channel_footer
from .cmd_fragments._get_parameter_id import url_parse
from .cmd_fragments._errors import gen_err

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
                fetch_playlist_id = url_parse(cmd_args[1])
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
                                output_embed = gen_err("playlist", "error", "not_found")
                        except Exception as PlaylistResponseError:
                            output_embed = gen_err("playlist", "error", "unexpected")
                            print(PlaylistResponseError)
                            traceback.print_exc()
                    else:
                        output_embed = gen_err("playlist", "error", "not_found")
                else:
                    output_embed = gen_err("playlist", "error", "bad_request")
            else:
                """if cmd_args[1] == "videos":
                    req_build(
                        "playlists?part=snippet,"
                    )  TODO - Make this thing work
                """
                output_embed = gen_err(
                    None, None, None,
                    custom_err = {
                        "title": "Feature coming soon",
                        "desc": "Arguments for this command are currently not ready, and will be here soon. Please look forward to their arrival!",
                        "footer": "Coming soon..."
                    }
                )
        await init_msg.delete()
        return {
            "output_msg": await msg_obj.channel.send(kwargs["msg_cmd_compiled"], embed = output_embed),
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