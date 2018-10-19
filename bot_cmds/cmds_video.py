from . import cmd_main
from .cmds_playlist import grab_playlist_id as get_playlist

from ._cmd_generate_API_request import req_build
from ._cmd_channel_footer import generate_channel_footer
from ._cmd_get_video_id import grab_vid_id
from ._cmd_time_parse import convert_duration

from re import search as re_s
from re import escape as re_e
from dateutil.parser import parse

from json import loads

import traceback

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
                        output_embed = cmd_main.err_embed(
                            "Video Fetch Failure",
                            "An error occurred attempting to get your requested video. The video may have been deleted, or the video ID is wrong.",
                            "API Response - Unexpected"
                        )
                        print(ResponseParseError)
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
                    "Malformed video URL error"
                )
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
                        output_embed = cmd_main.err_embed(
                            "Video Tags Error",
                            "An error occurred attempting to get the tags of your requested video. The video may have been deleted, or the video ID is wrong.",
                            "Invalid video ID error"
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
                            output_embed = cmd_main.err_embed(
                                title = "Description Fetch Failure",
                                desc = "Unfortunately, the API did not provide any description for the given video. Please try again later.",
                                footer = "API Response - Unexpected"
                            )
                            traceback.print_exc()
                    else:
                        output_embed = cmd_main.err_embed(
                            title = "Video Description Error",
                            desc = "Unfortunately, the API did not return any results for your query.\nPlease check your URL or request, and try again.",
                            footer = "API Response - Page Not Found"
                        )
            elif cmd_args[1] == "playlist":
                fetch_playlist_id = get_playlist(cmd_args[2])
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
                output_embed = cmd_main.err_embed(
                    "Command Parse Error",
                    "There was an unexpected argument given to the command. Please check that you're not adding any unnecessary words to the end of your message.",
                    "Unexpected command argument error"
                )
        await init_msg.delete()
        return {
            "output_msg": await msg_obj.channel.send(None, embed = output_embed),
            "output_admin": False
        }

cmd_video = cmd_main.Command(
    "Video",
    "video vid v",
    {
        "global": {
            "output_syntax": "{0} `<OPTIONAL tags/description/playlist/restrictions>` `<video URL>`",
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