from re import search as re_s

def convert_duration(time_str):
    resp_obj = { "H": None, "M": None, "S": None }
    re_match = re_s('^PT(\d*H)?(\d*M)?(\d*S)?', time_str)
    if re_match:
        re_str = re_match.groups()
        for grp in re_str:
            if grp and grp[-1] in resp_obj:
                if "H" in grp:
                    resp_obj[grp[-1]] = grp[:-1] + ":"
                else:
                    resp_obj[grp[-1]] = grp[:-1]
        ret_str = "{0}{1}:{2}".format(
            resp_obj["H"] or "",
            resp_obj["M"] or "00",
            resp_obj["S"] or "00"
        )
        return ret_str
    else:
        return None