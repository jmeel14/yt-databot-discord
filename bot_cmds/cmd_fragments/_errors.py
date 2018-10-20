from os.path import dirname as file_loc
from json import loads as json_ls

from discord import Embed as disc_embed

STR_FILE_REF = str(file_loc(__file__))
STR_ERR_LOC = STR_FILE_REF + '/../cmd_data/cmd_errors.json'

def err_embed(title, desc, footer):
    embed_obj = disc_embed(
        title = title,
        description = desc,
        colour = 0xDD0000
    )
    embed_obj.set_footer(
        text = footer
    )
    return embed_obj

def gen_err(cmd, err_type, err_ref, **kwargs):
    errs_file = open(STR_ERR_LOC, 'r')
    errs_dict = json_ls(errs_file.read())
    errs_file.close()
    
    
    if (cmd in errs_dict and err_type in errs_dict[cmd] and err_ref in errs_dict[cmd][err_type]):
        err_obj = errs_dict[cmd][err_type][err_ref]
        embed_obj = err_embed(
            title = err_obj["title"],
            desc = err_obj["desc"],
            footer = err_obj["footer"]
        )
    elif "custom_err" in kwargs:
        embed_obj = err_embed(
            title = kwargs["custom_err"]["title"],
            desc = kwargs["custom_err"]["desc"],
            footer = kwargs["custom_err"]["footer"]
        )
    else:
        embed_obj = err_embed(
            title = "An unexpected error occurred.",
            desc = "There has been an unexpected error that the developer has overlooked.\nPlease let the developer know by `@MENTION_BOT suggestion h <a description of your situation>`.",
            footer = "Overlooked/unexpected malfunction error"
        )
    return embed_obj