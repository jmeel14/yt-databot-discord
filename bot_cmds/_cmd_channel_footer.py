from ._cmd_generate_API_request import req_build
from ._cmd_generate_API_request import json_l

from dateutil.parser import isoparse
async def generate_channel_footer(targ_embed, channel_ID, **kwargs):
    instance_embed = targ_embed
    req_API_channel = await kwargs["self_http"].get(
        req_build(
            'channels?part=snippet&id={0}'.format(channel_ID), True
        )
    )
    if req_API_channel.status == 200:
        channel_resp = json_l(await req_API_channel.text())["items"][0]
    
    if "published_footer" in kwargs:
        timestamp = isoparse(kwargs["published_footer"]["published_at"])
        footer_str = "".join([
            "{0} | ".format(channel_resp["snippet"]["title"]),
            "Published {0}".format(
                "".join([
                    str(timestamp.year), "/",
                    str(timestamp.month), "/",
                    str(timestamp.day), " at ",
                    str(timestamp.hour), ":",
                    str(timestamp.minute)
                ])
            )
        ])
    else:
        footer_str = "{0}".format(channel_resp["snippet"]["title"])

    try:
        instance_embed.set_footer(
            text = footer_str,
            icon_url = channel_resp["snippet"]["thumbnails"]["default"]["url"]
        )
    except:
        instance_embed.set_footer(
            text = footer_str,
            icon_url = "https://i.imgur.com/YxrOhoy.pngg"
        )
    return instance_embed