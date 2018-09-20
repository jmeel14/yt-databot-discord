from . import cmd_main

class SuggestionEmbed:
    def __init__(self, self_col):
        self.colour = self_col
    
    def build_suggestion_embed(self, **kwargs):
        output_embed = cmd_main.Embed(
            title = kwargs["title"],
            description = kwargs["desc"],
            colour = self.colour
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

SUGGESTION_CLASSES = {
    "low": SuggestionEmbed(0x888888),
    "med": SuggestionEmbed(0xccaa00),
    "high": SuggestionEmbed(0xff5500)
}

async def cmd_func(cmd_name, cmd_str, msg_obj, **kwargs):
    cmd_split = cmd_str.split(" ")
    try:
        if SUGGESTION_CLASSES[cmd_split[1]] and len(cmd_split) > 2:
            out_embed = SUGGESTION_CLASSES[cmd_split[1]].build_suggestion_embed(
                title = "Incoming suggestion",
                desc = " ".join(cmd_split[2:]),
                author = {
                    "name": "{0.author.name} - {0.author.id}".format(msg_obj),
                    "icon": msg_obj.author.avatar_url
                },
                emb_footer = {
                    "text": "{0.guild.name} - {0.guild.id}".format(msg_obj),
                    "icon": msg_obj.guild.icon_url
                }
            )
    except:
        out_embed = cmd_main.err_embed(
            title = "Suggestion Submit Error",
            desc = "Could not send that suggestion, as it did not fit the requirements!",
            footer = "Invalid Suggestion Value"
        )
        pass
    await msg_obj.channel.send(None, embed = out_embed)

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
    "If you have any ideas or changes you'd wish to see in the bot, please use this feature wisely and let the developer know. Thank you!",
    cmd_func,
    False
)
