from . import cmd_main

from re import escape as re_e
from re import search as re_s

API_URL_DEFAULT = 'https://discordpy.readthedocs.io/en/rewrite/api.html'

API_REF = {
    "client": {
        "title": "Discord Client",
        "http_ref": "#client",
        "desc": "The discord client object."
    },
    "embed": {
        "title": "Discord Embed",
        "http_ref": "#embed",
        "desc": "The embed object, contained in messages."
    },
    "event": {
        "title": "Discord API Events",
        "http_ref": "#event-reference",
        "desc": "Events reference, which details how gateway events are handled."
    },
    "message": {
        "title": "Discord Message",
        "http_ref": "#message",
        "desc": "A message object, which is created whenever a message is sent or received by client."
    },
    "tchannel": {
        "title": "Discord Text Channel",
        "http_ref": "#textchannel",
        "desc": "A textchannel, which contains messages sent and received in public guilds."
    },
    "dmchannel": {
        "title": "Discord DM Channel",
        "http_ref": "#dmchannel",
        "desc": "A private message channel object, which contains messages only sent in private."
    },
    "user": {
        "title": "Discord User",
        "http_ref": "#user",
        "desc": "The user object that stores user information such as name, nick, discriminator, etc."
    }
}


async def cmd_func(cmd_name, cmd_str, msg_obj, **kwargs):
    if len(cmd_str.split(" ")) < 2:
        descript_str = "The following link will take you to the homepage of\nDiscord.py's rewrite branch documentation."
        output_embed = cmd_main.Embed(
            title = "Discord.py Rewrite Documentation Link",
            description = descript_str + "\n [Documents]({})".format(API_URL_DEFAULT)
        )
        cmd_output_msg = await msg_obj.channel.send(content = None, embed = output_embed)
        return { "output_admin": True, "output_msg": cmd_output_msg, "trigger_msg": msg_obj }
    else:
        if len(cmd_str.split(" ")) == 2:
            cmd_split = cmd_str.split(" ")
            cmd_arg = cmd_split[1].lower()
            try:
                if cmd_arg in API_REF:
                    link_ref = API_URL_DEFAULT + API_REF[cmd_arg]["http_ref"]
                    output_embed = cmd_main.Embed(
                        title = API_REF[cmd_arg]["title"],
                        description = API_REF[cmd_arg]["desc"] + "\n[Go to documentation]({0})".format(link_ref)
                    )
                    cmd_output_msg = await msg_obj.channel.send(content = None, embed = output_embed)
                    return { "output_admin": True, "output_msg": cmd_output_msg, "trigger_msg": msg_obj }
            except Exception as DocsException:
                output_embed = cmd_main.err_embed(
                    "Invalid command error",
                    "Could not find a documentation part with that name, maybe take a look yourself?\n[Go to documentation]({0})".format(API_URL_DEFAULT),
                    "Unknown API Reference"
                )
                cmd_output_msg = await msg_obj.channel.send(content = None, embed = output_embed)
                print(DocsException)
                return { "output_admin": True, "output_msg": cmd_output_msg, "trigger_msg": msg_obj }

cmd_docs = cmd_main.Command(
    "Developer Documentation",
    "docs doccos documentation",
    "Retrieves the URL for a specific part of the bot, with optional arguments to link to the respective Discord.py Rewrite Documentation segment.",
    cmd_func,
    True
)
