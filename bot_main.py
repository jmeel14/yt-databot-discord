import discord

import bot_cmds
import bot_config

import re
import random
import aiohttp
import asyncio
import os

import logging
logging.basicConfig(level=logging.INFO)
import traceback

CMD_LIST = bot_cmds.cmd_main.cmd_list


async def generic_err(prefix, discord_client, msg_obj, cmd_name):
    if len(prefix) > 3:
        err_str = "There was no command found with the name '" + cmd_name + "', or the response was too big!"
        err_embed = discord.Embed(
            title = "Command error",
            description = err_str,
            colour = 0xDD0000
        )
        err_embed.set_footer(text = "Unknown command error")

        await msg_obj.channel.send(
            content = None,
            embed = err_embed
        )

class Bot(discord.Client):
    def __init__(self, ownerID, guildID, bot_token):
        super(Bot, self).__init__()
        self.owner_guild_id = guildID
        self.owner_id = ownerID
        self.client = self

        self.run(bot_token)

    async def on_ready(self):
        self.http_session = aiohttp.ClientSession()
        print(
            "\nSTART-UP: Bot started with ID {0.id} and name {0.name}".format(self.user)
        )
    async def on_guild_join(self, gld):
        join_str_array = [
            "JOIN: Bot joined ",
            "guild with ID {0.id} ", "and name {0.name}, ",
            "with {0.members}, ", "of which {0.human_members} are human."
        ]
        mbr_count = [len(gld.members), len([mbr for mbr in gld.members if mbr.bot])]
        mbr_humans = [str(mbr_count[0] / (mbr_count[0] - mbr_count[1])) + "%"]
        format_str = "".join(join_str_array).format({
            "id": gld.id, "name": gld.name,
            "members": mbr_count[0], "human_members": mbr_humans[1]
        })
        print(format_str)
    
    async def on_message(self, msg_obj):
        if not msg_obj.author.bot or msg_obj.author.id == self.owner_id:
            is_DM = isinstance(msg_obj.channel, discord.abc.PrivateChannel)
            if is_DM:
                print_str = {
                    "announce": "INCOMING MESSAGE | [{0.author.id}] {0.author.name} : {0.content}"
                }
                print(print_str["announce"].format(msg_obj))
            sv_prefix = bot_config.cfg_prefix.check_prefix(msg_obj, is_DM)
            msg_cmd = bot_config.cfg_func.check_command(msg_obj, self.user.id, sv_prefix)
            if msg_cmd:
                cmd_name = msg_cmd.split(" ")[0]
                try:
                    if CMD_LIST[cmd_name]['admin'] and msg_obj.author.id != 103832588556193792:
                        await generic_err(sv_prefix, self, msg_obj, cmd_name)
                        return
                    else:
                        resp_msg = await CMD_LIST[cmd_name]['func'](
                            cmd_name, msg_cmd, msg_obj,
                            self_client = self.client,
                            self_http = self.http_session
                        )
                        try:
                            if resp_msg["output_admin"]:
                                await asyncio.sleep(30)
                                await resp_msg["output_msg"].delete()
                                try:
                                    await resp_msg["trigger_msg"].delete()
                                except:
                                    pass
                        except:
                            pass
                except:
                    if msg_obj.channel.id not in [110373943822540800, 468690756899438603, 110374153562886144]:
                        await generic_err(sv_prefix, self, msg_obj, cmd_name)
                    
                    if not isinstance(msg_obj.channel, discord.abc.GuildChannel):
                        print_str = [
                            "ERROR | In [{0.guild.id}] {0.guild.name}, by user [{0.author.id}] {0.author.name}",
                            "{0.author.name}: {1}"
                        ]
                    else:
                        print_str = [
                            "ERROR | In DM from [{0.author.id}] {0.author.name}",
                            "{0.author.name}: {1}"
                        ]
                    print(print_str[0].format(msg_obj))
                    print(print_str[1].format(msg_obj, msg_cmd))
                    traceback.print_exc()

            if msg_obj.author.id == self.owner_id:
                if msg_obj.content == "bot.shutdown":
                    await self.client.logout()
                    await self.http_session.close()
                elif msg_obj.content == "bot.restart":
                    os.system('./bot_start.sh')
                    await self.client.logout()

DISC_YT_BOT = Bot(
    bot_config.cfg_auth.get_data("bot_author", True, extended_prop="bot_meta"),
    bot_config.cfg_auth.get_data("bot_guild", True, extended_prop="bot_meta"),
    bot_config.cfg_auth.get_data('bot_key', True, extended_prop="bot_meta")
)

