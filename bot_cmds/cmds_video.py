from re import search as re_s
from re import escape as re_e
from dateutil.parser import parse
from json import loads
import traceback

from . import cmd_main

from .cmd_fragments._generate_API_request import req_build
from .cmd_fragments._channel_footer import generate_channel_footer
from .cmd_fragments._get_parameter_id import grab_vid_id, grab_playlist_id
from .cmd_fragments._time_parse import convert_duration
from .cmd_fragments._errors import gen_err

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    init_embed = cmd_main.Embed(
        title = "Video Command Received",
        description = "Your command has been received by the bot. Please wait as your request gets processed."
    )
    init_msg = await msg_obj.channel.send(None, embed = init_embed)
    async with msg_obj.channel.typing():
        if len(cmd_str.split(" ")) == 2:
            cmd_split = cmd_str.split(" ")
            fetch_vid_id = grab_vid_id(cmd_split[1])
            if fetch_vid_id:
                req_API = await kwargs["self_http"].get(
                    req_build(
                        'videos?part=snippet,statistics,contentDetails&id={0}'.format(fetch_vid_id),
                        True
                    )
                )
                if req_API.status == 200:
                    try:
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
                            value = "{:,}".format(int(targ_result["statistics"]["viewCount"])),
                            inline = True
                        )

                        vid_duration = convert_duration(targ_result["contentDetails"]["duration"])
                        if vid_duration:
                            output_embed.add_field(
                                name = "Length",
                                value = vid_duration
                            )

                        output_embed.add_field(
                            name = "Likes",
                            value = "{:,}".format(int(targ_result["statistics"]["likeCount"])),
                            inline = True
                        )
                        output_embed.add_field(
                            name = "Dislikes",
                            value = "{:,}".format(int(targ_result["statistics"]["dislikeCount"])),
                            inline = True
                        )
                        output_embed.set_image(url=targ_result["snippet"]["thumbnails"]["high"]["url"])

                        output_embed = await generate_channel_footer(
                            output_embed, targ_result["snippet"]["channelId"],
                            self_http = kwargs["self_http"],
                            published_footer = { "published_at": targ_result["snippet"]["publishedAt"] }
                        )
                    except Exception as ResponseParseError:
                        output_embed = gen_err("video", "error", "unexpected")
                        print(ResponseParseError)
                        traceback.print_exc()
                else:
                    output_embed = gen_err("video", "error", "")
            else:
                output_embed = gen_err("video", "error", "bad_request")
        elif len(cmd_str.split(" ")) > 2:
            cmd_args = cmd_str.split(" ")
            if cmd_args[1] == "tags":
                fetch_vid_id = grab_vid_id(cmd_args[2])
                if fetch_vid_id:
                    req_API = await kwargs["self_http"].get(
                        req_build(
                            'videos?part=snippet&id={0}'.format(fetch_vid_id),
                            True
                        )
                    )
                    try:
                        targ_result = loads(await req_API.text())["items"][0]["snippet"]
                        try:
                            output_embed = cmd_main.Embed(
                                title = targ_result["title"],
                                description = "**The video you requested had the following tags:**\n{0}".format(
                                    "\n".join(targ_result["tags"][:20])
                                ),
                                colour = 0xDD2222
                            )
                        except:
                            output_embed = cmd_main.Embed(
                                title = targ_result["title"],
                                description = "Unfortunately, the video that you requested did not have any tags.",
                                colour = 0xffee00
                            )
                        output_embed.set_thumbnail(url = targ_result["thumbnails"]["default"]["url"])

                        output_embed = await generate_channel_footer(
                            output_embed,
                            targ_result["channelId"],
                            self_http = kwargs["self_http"],
                            published_footer = { "published_at": targ_result["publishedAt"] }
                        )
                    except Exception as TagsFetchError:
                        print(fetch_vid_id)
                        output_embed = gen_err(None, None, None, custom_err = 
                            {
                                "title": "Tag Fetch Failure",
                                "desc": "There was a problem getting the tags of your requested video.\nPlease check to make sure the URL is correct, and try again.",
                                "footer": "Invalid video ID error"
                            }
                        )
                        traceback.print_exc()
            elif cmd_args[1] == "description":
                fetch_vid_id = grab_vid_id(cmd_args[2])
                if fetch_vid_id:
                    req_API = await kwargs["self_http"].get(
                        req_build(
                            'videos?part=snippet&id={0}'.format(fetch_vid_id),
                            True
                        )
                    )
                    if req_API.status == 200:
                        try:
                            targ_result = loads(await req_API.text())["items"][0]["snippet"]
                            if len(targ_result["description"]) > 2048:
                                out_str = " ".join([
                                    targ_result["description"][:2047][:-100], "...\n",
                                    "[Read the full description on the video page.](https://youtu.be/{0})".format(fetch_vid_id)
                                ])
                            else:
                                out_str = targ_result["description"]
                            output_embed = cmd_main.Embed(
                                title = targ_result["title"],
                                description = out_str,
                                colour = 0xDD2222
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
                        except Exception as OutputFormatError:
                            output_embed = gen_err("video", "error", "unexpected")
                            traceback.print_exc()
                    else:
                        output_embed = gen_err("video", "error", "not_found")
            elif cmd_args[1] == "playlist":
                fetch_playlist_id = grab_playlist_id(cmd_args[2])
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
                                targ_result_contents = large_result[0]["contentDetails"]
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
                                    value = "{0} video(s)".format(targ_result_contents["itemCount"])
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
                output_embed = gen_err("video", "error", "bad_arg")
    await init_msg.delete()
    return {
        "output_msg": await msg_obj.channel.send(kwargs["msg_cmd_compiled"], embed = output_embed),
        "output_admin": False
    }

cmd_video = cmd_main.Command(
    "Video",
    "video vid v",
    {
        "global": {
            "output_syntax": "{0} `<OPTIONAL tags/description/playlist>` `<video URL>`",
            "output_description": "Retrieves information about a video, in respect to the given argument."
        },
        "tags": {
            "output_syntax": "{0} `<video URL>`",
            "output_description": "Retrieves the tags of a specified video URL."
        },
        "description": {
            "output_syntax": "{0} `video URL>`",
            "output_description": "Retrieves up to "
        },
        "playlist": {
            "output_syntax": "{0} `<video URL containing playlist ID>`",
            "output_description": "Retrieves information about a video's playlist."
        }
    },
    "Retrieves general information of a YouTube video.",
    cmd_func,
    False
)