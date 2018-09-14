from . import cmd_main
async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    output_embed = False
    self_destruct = False
    if cmd_str == cmd_trigger:
        output_embed = cmd_main.Embed(
            title = "Youtube Data Bot Commands List",
            description = """This bot performs tasks related to grabbing information from YouTube, including uploaders, videos, channels, playlists, etc.
\nThis bot is not the property of Alphabet Inc., and all data you see provided by this bot is available publically on YouTube.""",
            colour = 0x5588DD
        )
        
        curr_dict_list = {}
        for cmd in cmd_main.cmd_list:
            curr_item = cmd_main.cmd_list[cmd]
            if not curr_item['admin'] or msg_obj.author.id == 103832588556193792:
                new_dict_item = {
                    "name": curr_item["name"],
                    "alias": cmd,
                    "help": curr_item["help"]
                }

                if new_dict_item["name"] in curr_dict_list:
                    old_alias = curr_dict_list[new_dict_item["name"]]["alias"]
                    curr_dict_list[new_dict_item["name"]]["alias"] = old_alias + ", " + cmd
                else:
                    curr_dict_list[new_dict_item["name"]] = new_dict_item
                if curr_item["admin"]:
                    self_destruct = True
        for prop in curr_dict_list:
            output_embed.add_field(
                name = "Command",
                value = curr_dict_list[prop]["name"],
                inline = True
            )
            output_embed.add_field(
                name = "Alternative triggers",
                value = curr_dict_list[prop]["alias"],
                inline = True
            )
            output_embed.add_field(
                name = "Description",
                value = str(curr_dict_list[prop]["help"]) + "\n\n",
                inline = False
            )
    else:
        try:
            cmd_main.cmd_list[cmd_str.split(' ')[1]]
            print("Command '" + cmd_str.split(' ')[1] + "' found in cmd_list")
        except:
            cmd_out_str = "Unfortunately, there was no known command with the name `" + cmd_str.split(' ')[1] + "`.\nSorry about that!"
            output_embed = cmd_main.err_embed("Invalid Help Command", cmd_out_str, "Unknown command reference")
    
    if output_embed:
        help_msg = await msg_obj.channel.send(
            content = None,
            embed = output_embed
        )
        
    if self_destruct:
        return {
            "output_admin": True,
            "output_msg": help_msg,
            "trigger_msg": msg_obj
        }

cmd_help = cmd_main.Command(
    "Commands Help",
    "help ?",
    "This command outputs the parameters for all other commands.",
    cmd_func,
    False
)