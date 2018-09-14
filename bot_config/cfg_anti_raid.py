async def check_last_msgs(msg_obj, disc_client, length_back):
    msg_list_general = reversed(disc_client.messages)
    [print(str(msg.timestamp) + ' :: ' + msg.author.id + ' :: ' + msg.content) for msg in msg_list_general]
    msg_list_chnl_specific = []

    for msg in msg_list_general:
        if msg.channel.id == msg_obj.channel.id:
            msg_list_chnl_specific.append(msg)
    
    [print(msg.timestamp) for msg in msg_list_chnl_specific]