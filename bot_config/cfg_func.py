from re import search as re_s
from re import escape as re_esc
from re import M as re_m

def check_trigger(msg_obj, self_id, self_prefix):
    """Checks the message for a trigger, whether it's a mention or self ID."""

    mention_name_string = re_esc("<@") + self_id + re_esc(">") + "\s"
    mention_name_detect = re_s("^" + mention_name_string, msg_obj.content)

    prefix_string = self_prefix
    prefix_detect = re_s("^" + prefix_string, msg_obj.content)

    return {
        "check_name_mention": [mention_name_string, mention_name_detect],
        "check_prefix": [prefix_string, prefix_detect]
    }

def check_command(msg_obj, self_id, self_prefix):
    """Checks for a trigger, and then locates the command string."""

    check_obj = check_trigger(msg_obj, str(self_id), self_prefix)

    if check_obj["check_name_mention"][1]:
        cmd_string = re_s("^" + check_obj["check_name_mention"][0] + "(.*)", msg_obj.content, flags = re_m).groups()[0]
    elif check_obj["check_prefix"][1]:
        cmd_string = re_s("^" + check_obj["check_prefix"][0] + "(.*)", msg_obj.content, flags = re_m).groups()[0]
    else:
        cmd_string = False

    return cmd_string

async def check_cmd_list(cmd_name, cmd_array):
    for cmd in cmd_array:
        if cmd_name in cmd["aliases"]:
            return True
