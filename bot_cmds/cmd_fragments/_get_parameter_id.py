from re import escape as re_e, search as re_s

def url_parse(url):
    if "youtube.com" in url or "youtu.be" in url:
        re_param_grab = "\&?\??list\=" if "list" in url else "\?v\="
        re_arg_grab = "([^&>]*)&?\>?"
        try:
            return_arg = [re_res for re_res in re_s(
                re_param_grab + re_arg_grab, url
            ).groups() if re_res != None][0]
            return return_arg
        except:
            return None
    else:
        return None