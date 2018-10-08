from . import cmd_main

from os.path import dirname as file_loc
from json import load as json_l
from json import dumps as json_d
from datetime import datetime

import re

STR_FILE = str(file_loc(__file__))
STR_SUGGESTS_FILE = STR_FILE + '/cmd_data/cmd_suggests.json'
SUGGESTS_DICT = json_l(open(STR_SUGGESTS_FILE, "r"))
SUGGESTION_CHANNELS = SUGGESTS_DICT["channels"]

class SuggestionEmbed:
    def __init__(self, self_lvl):
        self.level = self_lvl
    
    def build_suggestion_embed(self, levels_dict, **kwargs):
        embed_colour = None
        if self.level in levels_dict:
            embed_colour = levels_dict[self.level]["colour"]
        output_embed = cmd_main.Embed(
            title = kwargs["title"],
            description = kwargs["desc"],
            colour = embed_colour
        )
        output_embed.set_author(
            name = kwargs["author"]["name"],
            icon_url = kwargs["author"]["icon"]
        )
        output_embed.set_footer(
            text = kwargs["emb_footer"]["text"],
            icon_url = kwargs["emb_footer"]["icon"]
        )
        return output_embed

SUGGESTION_LEVELS = {
    "l": {
        "channel": SUGGESTION_CHANNELS["l"],
        "colour": 0x886600,
        "output_text": "Low",
        "embed": SuggestionEmbed('l')
    },
    "m": {
        "channel": SUGGESTION_CHANNELS["m"],
        "colour": 0xffee00,
        "output_text": "Medium",
        "embed": SuggestionEmbed('m')
    },
    "h": {
        "channel": SUGGESTION_CHANNELS["h"],
        "colour": 0xffaa00,
        "output_text": "High",
        "embed": SuggestionEmbed('h')
    }
}


async def cmd_func(cmd_name, cmd_str, msg_obj, **kwargs):
    cmd_args = cmd_str.split(" ")
    cmd_args[1] = cmd_args[1].lower()
    targ_chnl = kwargs["self_guild_meta"]["self_support_chnl"]
    try:
        if SUGGESTION_LEVELS[cmd_args[1]] and len(cmd_args) > 2:
            suggestion_str_re = re.compile(re.escape(cmd_args[0]) + "\s.\s(.*)", flags = re.DOTALL)
            suggestion_str = suggestion_str_re.search(cmd_str).groups()[0]

            received_str = "".join([
                "Your suggestion is received, and has been transferred for the bot developer to see.",
                "\nPlease wait to see if your suggestion gets accepted in the bot's support guild.",
                "\n\nYour patience is a very warm gesture, and greatly appreciated."
            ])
            received_embed = cmd_main.Embed(
                title = "Suggestion Command Received",
                description = "Your suggestion has been received, and transferred to the bot developer.",
                colour = 0x448844
            )
            received_embed.add_field(
                name = "Suggestion description",
                value = suggestion_str
            )
            received_embed.add_field(
                name = "Suggestion priority",
                value = SUGGESTION_LEVELS[cmd_args[1]]["output_text"]
            )
            received_msg = await msg_obj.channel.send(None, embed = received_embed)
            confirm_str = "".join([
                "Suggestion incoming from user \[{0.id}\] {0.name}.",
                "\nRespond with `Y` to accept suggestion with user's suggestion level,",
                "\nor enter appropriate suggestion level, using `l`, `m`, or `h`.\nRespond with `C <reason>` to cancel."
            ])

            time_now = datetime.now()
            time_str = "{0}:{1}:{2} on {3}/{4}/{5}".format(
                time_now.hour,
                time_now.minute,
                time_now.second,
                time_now.day,
                time_now.month,
                time_now.year
            )
            suggestion_id = "{0}{1}{2}{3}{4}{5}{6}".format(
                time_now.year,
                time_now.month,
                time_now.day,
                time_now.hour,
                time_now.minute,
                time_now.second,
                time_now.microsecond
            )

            confirm_embed = cmd_main.Embed(
                title = "Incoming suggestion",
                description = confirm_str.format(msg_obj.author),
                colour = 0xAAF9FF
            )
            confirm_embed.add_field(
                name = "Suggestion content",
                value = suggestion_str
            )
            confirm_embed.add_field(
                name = "User's Suggestion level",
                value = cmd_args[1]
            )
            confirm_msg = await targ_chnl.send(suggestion_id, embed = confirm_embed)
            
            def check_owner_responding(msg):
                return msg.author.id == kwargs["self_guild_meta"]["self_author"] and msg.channel.id == SUGGESTION_CHANNELS["raw"]
            
            owner_response = await kwargs["self_client"].wait_for('message', check = check_owner_responding)
            owner_args = owner_response.content.split(" ")
            owner_args[1] = owner_args[1].lower()

            suggestion_accept = False
            suggestion_priority = None
            if owner_args[0] == suggestion_id and owner_args[1] != "c":
                if (cmd_args[1] in SUGGESTION_LEVELS) and (owner_args[1] == 'y' or owner_args[1] == cmd_args[1]):
                    suggestion_accept = True
                    suggestion_priority = cmd_args[1]
                    out_str = "Your suggestion was accepted, and is now stored in the bot support guild!"
                    out_embed = SUGGESTION_LEVELS[cmd_args[1]]["embed"].build_suggestion_embed(
                        SUGGESTION_LEVELS,
                        title = "{0} | Received {1}".format(suggestion_id, time_str),
                        desc = suggestion_str,
                        author = { "name": msg_obj.author.name, "icon": msg_obj.author.avatar_url },
                        emb_footer = { "text": "{0} | {1}".format(msg_obj.guild.id, msg_obj.guild.name), "icon": msg_obj.guild.icon_url }
                    )
                elif owner_args[1] != cmd_args[1] and cmd_args[1] in SUGGESTION_LEVELS:
                    suggestion_accept = True
                    suggestion_priority = owner_args[1]
                    out_str = "Your suggestion was accepted, but at a different priority."
                    out_embed = SUGGESTION_LEVELS[owner_args[1]]["embed"].build_sugestion_embed(
                        SUGGESTION_LEVELS,
                        title = "{0} | Received {1}".format(suggestion_id, time_str),
                        desc = suggestion_str,
                        author = { "name": msg_obj.author.name, "icon": msg_obj.author.avatar_url },
                        emb_footer = { "text": "{0} | {1}".format(msg_obj.guild.id, msg_obj.guild.name), "icon": msg_obj.guild.icon_url }
                    )
            elif owner_args[0] == suggestion_id:
                re_reason_compile = re.compile("^\d*\s[cC]\s(.*)", re.DOTALL)
                owner_reason = re_reason_compile.search(owner_response.content).groups()[0]
                out_str = "Your suggestion was rejected... The owner responded with:"
                out_embed = cmd_main.err_embed(
                    title = "Suggestion Receival Failure",
                    desc = owner_reason,
                    footer = "Suggestion unwarranted/rejected by owner"
                )
            if suggestion_accept:
                await confirm_msg.delete()
                SUGGESTS_DICT["suggestions"][suggestion_id] = {
                    "author_id": msg_obj.author.id,
                    "msg_meta": {
                        "msg_id": msg_obj.id,
                        "msg_channel_id": msg_obj.channel.id,
                        "msg_guild_id": msg_obj.guild.id
                    },
                    "suggestion": {
                        "sugg_content": suggestion_str,
                        "sugg_priority": suggestion_priority
                    }
                }
                suggests_file = open(STR_SUGGESTS_FILE, 'w')
                suggests_file.write(json_d(SUGGESTS_DICT))
                suggests_file.close()
    except Exception as ParseSuggestionError:
        out_str = None
        out_embed = cmd_main.err_embed(
            title = "Suggestion Submit Error",
            desc = "Could not send that suggestion, as the syntax was incorrect.",
            footer = "Invalid Suggestion Value"
        )
        print("BAD SUGGESTION/FORMAT: {0}".format(ParseSuggestionError))
    return { "output_msg": await msg_obj.channel.send(out_str, embed = out_embed), "output_admin": False }

cmd_exec = cmd_main.Command(
    "Suggest a feature/change",
    "suggest suggestion sugg sgst",
    {
        "global": {
            "output_syntax": "{0} `<suggestion priority ('l'/'m'/'h')>` `<suggestion description>`",
            "output_description": "Sends a suggestion to the bot developer with the given priority level.\nThis feature logs your messages."
        },
        "l": {
            "output_syntax": "{0} `<suggestion description>`",
            "output_description": "Sends a suggestion of low priority. Use this one if the problem's just a typo, or something mostly irrelevant."
        },
        "m": {
            "output_syntax": "{0} `<suggestion description>`",
            "output_description": "Sends a suggestion of medium priority. Use this one if the bot's giving wrong information, or a little buggy."
        },
        "h": {
            "output_syntax": "{0} `<suggestion description>`",
            "output_description": "Sends a suggestion of high priority. Please reserve this only for issues that ruin the purpose of the bot."
        }
    },
    "Let the developer of the bot know of something you wish to see on it, or changed, or just removed. Your input is appreciated, thank you!\nPlease bear in mind your message will be stored.",
    cmd_func,
    False
)
