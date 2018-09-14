from discord import Embed
from re import search

cmd_list = {}

class Command:
    """
    A command class to simplify and modularize functionality.
    """

    def __init__(self, name, aliases, help_str, self_func, requires_admin):
        self.name = name
        self.aliases = aliases.split(" ")
        self.help = help_str
        self.self_func = self_func
        self.admin = requires_admin

        for alias in self.aliases:
            cmd_list[alias] = {
                "name": self.name,
                "help": self.help,
                "func": self.self_func,
                "admin": self.admin
            }

def err_embed(title, desc, footer):
    embed_obj = Embed(
        title = title,
        description = desc,
        colour = 0xDD0000
    )
    embed_obj.set_footer(
        text = footer
    )
    return embed_obj