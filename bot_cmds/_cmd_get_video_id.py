from re import escape as re_e, search as re_s
def grab_vid_id(vid_link):
    try:
        if "youtube.com" in vid_link or "youtu.be" in vid_link:
            vid_return_id = [re_res for re_res in re_s(
                re_e("youtube.com/watch?v=") + "([^&]*)&?|youtu.be\\/([^?]*)\??",
                vid_link
            ).groups() if re_res != None][0]
            return vid_return_id
        else:
            return None
    except Exception as URLParseError:
        print(URLParseError)
        return None
