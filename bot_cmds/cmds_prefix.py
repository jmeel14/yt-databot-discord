from . import _cfg_json
from . import cmd_main
from os.path import dirname as file_loc

from re import search as re_s
from re import escape as re_e

STR_FILE = str(file_loc(__file__))
STR_PREF_FILE = STR_FILE + '/../bot_config/cfg_data/prefix.json'


async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    if cmd_trigger != cmd_str:
        try:
            esc_str = re_s(re_e(cmd_str.split(" ")[0]) + "\s(.*)", cmd_str)
        except:
            resp_embed = cmd_main.err_embed(
                "Command Error",
                "An error occurred attempting to parse the new prefix. Please make sure there are no strange characters in your message.",
                "Prefix processing error"
            )
            await msg_obj.channel.send(
                content = None,
                embed = resp_embed
            )
            raise
        prefix_str = esc_str.groups()[0]

        pref_srv = str(msg_obj.guild.id)

        pref_json = _cfg_json.read_json(STR_PREF_FILE)
        pref_json[pref_srv] = prefix_str

        _cfg_json.write_json(STR_PREF_FILE, pref_json)

        out_str = "The bot's prefix in this channel has been successfully set to '" + prefix_str + "'.\n"
        embed_obj = cmd_main.Embed(
            title = "Command sucessful",
            description =   out_str,
            colour = 0x00DD00
        )
        await msg_obj.channel.send(
            content = None,
            embed = embed_obj
        )

    else:
        curr_pref_json = _cfg_json.read_json(STR_PREF_FILE)
        try:
            curr_pref = curr_pref_json[str(msg_obj.guild.id)]
        except:
            curr_pref = curr_pref_json["default"]
        out_str = "The bot's prefix in this channel is set to '" + curr_pref + "'."
        embed_obj = cmd_main.Embed(
            title = "Command Result",
            description =   out_str,
            colour = 0x00DDDD
        )
        await msg_obj.channel.send(
            content = None,
            embed = embed_obj
        )

cmd_video = cmd_main.Command(
    "Prefix",
    "cp change_prefix changeprefix prefix setprefix set_prefix sp",
    {
        "global": {
            "output_syntax": "{0} <any new prefix>",
            "output_description": "Changes the guild's bot prefix to a different one."
        }
    },
    "Modifies the prefix of the current server",
    cmd_func,
    False
)
