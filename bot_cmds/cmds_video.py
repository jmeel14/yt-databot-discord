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
    try:
        re_str = re_s(re_e("?v=") + "(.*)", vid_link).groups()[0]
        return [True, re_str]
    except:
        return [False, None]

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if cmd_str.split(" ")[0] == "video":
        cmd_split = cmd_str.split(" ")
        if re_s(re_e("?v=") + "(.*)", cmd_str):
            if grab_vid_id(cmd_split[1])[0]:
                re_str = grab_vid_id(cmd_split[1])[1]
            else:
                await msg_obj.channel.send("No video URL was provided, cancelling command.")
                return

            wait_msg = await msg_obj.channel.send("Please wait while the request is generated and sent...")
            await msg_obj.channel.trigger_typing()
            
            api_req = "/videos?part=snippet" + "&id=" + re_str
            req_str = req_build(api_req)
            req = await kwargs["self_http"].get(req_str)
            resp = await req.text()

            resp_json = loads(resp)

            if resp_json["pageInfo"]["totalResults"] != 0:
                vid_obj = resp_json["items"][0]["snippet"]

                output_embed = cmd_main.Embed(
                    title = vid_obj["title"],
                    description = vid_obj["description"][:280] + "..."
                )
                output_embed.set_thumbnail(
                    url = vid_obj["thumbnails"]["default"]["url"]
                )

                api_req = "/channels?part=snippet&id=" + vid_obj["channelId"]
                req_str = req_build(api_req)
                req = await kwargs["self_http"].get(req_str)
                resp = await req.text()
                resp_json = loads(resp)
                if resp_json["pageInfo"]["totalResults"] != 0:
                    channel_obj = resp_json["items"][0]["snippet"]

                    output_embed.set_footer(
                        text = channel_obj["title"],
                        icon_url = channel_obj["thumbnails"]["default"]["url"]
                    )

                if len(cmd_split) > 2:
                    if cmd_split[2] == "tags":
                        try:
                            tags_list = ""
                            for tag in vid_obj["tags"]:
                                tags_list = tags_list + tag + " | "
                        except:
                            tags_list = "No tags could be found on the requested video."

                        output_embed.add_field(
                            name = "Tags",
                            value = tags_list[:800]
                        )
                        await wait_msg.delete()
                        await msg_obj.channel.send(
                            content = None,
                            embed = output_embed
                        )
                else:
                    await wait_msg.delete()
                    await msg_obj.channel.send(
                        content = None,
                        embed = output_embed
                    )

            else:
                print("ERROR occurring in URL: " + req_str)
                await msg_obj.channel.send(
                    content = None,
                    embed = cmd_main.err_embed(
                        "Command Error",
                        "An error occurred attempting to parse your URL.",
                        "Invalid URL error"
                    )
                )


cmd_video = cmd_main.Command(
    "Video",
    "video videosearch vidsearch vs",
    "Retrieves general information of a video",
    cmd_func,
    False
)