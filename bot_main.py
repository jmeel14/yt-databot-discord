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

CLIENT_LOGGER = logging.getLogger('discord')

async def generic_err(prefix, discord_client, msg_obj, cmd_name):
    if len(prefix) > 3:
        err_str = "".join([
            "There was an issue processing your requested command '", cmd_name,"'.",
            "\n", "This should not have happened, so please let the developer know using ",
            "`{0} suggest h <description of the problem>`.".format(prefix)
        ])
        err_embed = discord.Embed(
            title = "Invalid Command Error",
            description = err_str,
            colour = 0xDD0000
        )
        err_embed.set_footer(text = "Unknown command error")

        await msg_obj.channel.send(
            content = None,
            embed = err_embed
        )

class Bot(discord.Client):
    def __init__(self, ownerID, guildMeta, bot_token):
        super(Bot, self).__init__()
        self.owner_guild_id = guildMeta["self_guild"]
        self.support_channel_id = guildMeta["self_support"]
        self.owner_id = ownerID
        self.client = self

        self.run(bot_token)

    async def on_ready(self):
        try:
            await self.user.edit(avatar = open('./avatar.png', 'rb').read())
            CLIENT_LOGGER.log(20, "Avatar successfully updated to meet latest version on disk.")
        except:
            pass
        try:
            await self.change_presence(
                activity = discord.Activity(name = " for @mention help", type = discord.ActivityType.watching)
            )
            CLIENT_LOGGER.log(20, "Successfully set activity status to 'Watching for @mention help'.")
        except Exception as StatusError:
            print(StatusError)
        self.http_session = aiohttp.ClientSession()
        CLIENT_LOGGER.log(20, "START-UP: Bot started with ID {0.id} and name {0.name}".format(self.user))
    
    async def on_guild_join(self, gld):
        join_str = "JOIN: Bot joined guild with ID {0} and name {1}\nMembers: {2} Humans:{3}"
        join_str = join_str.format(
            gld.id, gld.name, len(gld.members),
            len([mbr for mbr in gld.members if mbr.bot]) / len(gld.members)
        )
        print(join_str)
    async def on_guild_remove(self, gld):
        print("Left/removed from guild {0}".format(gld.name))
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
                    if cmd_name in CMD_LIST:
                        if CMD_LIST[cmd_name]['admin'] and msg_obj.author.id != self.owner_id:
                            await generic_err(sv_prefix, self, msg_obj, cmd_name)
                            return
                        else:
                            resp_msg = await CMD_LIST[cmd_name]['func'](
                                cmd_name, msg_cmd, msg_obj,
                                msg_guild_prefix = sv_prefix,
                                self_client = self.client,
                                self_http = self.http_session,
                                self_guild_meta = {
                                    "self_guild": self.get_guild(self.owner_guild_id),
                                    "self_support_chnl": self.get_channel(self.support_channel_id),
                                    "self_author": self.owner_id
                                }
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
                    
                    if not isinstance(msg_obj.channel, discord.abc.PrivateChannel):
                        print_str = [
                            "ERROR | In guild [{0.guild.id}] {0.guild.name}, by user [{0.author.id}] {0.author.name}",
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
    bot_config.cfg_auth.get_data("bot_guild_meta", True, extended_prop="bot_meta"),
    bot_config.cfg_auth.get_data('bot_key', True, extended_prop="bot_meta")
)

