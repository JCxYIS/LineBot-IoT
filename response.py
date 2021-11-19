import random

from linebot.models import *

from user import User

import os
import json
import fileutil


def make_response(user: User, message: str, attachment_path: str, attachment_ext: str) -> [SendMessage]:
    """
    Make Response
    user: user model of that user
    message: text message, may be empty
    attachment_path: abs path of attachment, may be empty
    attachment_ext: extension of attachment (possible values: jpg, mp4, m4a, (empty))
    """

    # Init
    if user.state == 0:
        user.state = 100
        return generate_response_from_directory('welcome')

    # Basic state
    elif user.state == 100:
        # TODO
        return generate_response_from_directory('test', random.randint(0, 100))

    # 開始製作長輩圖
    elif user.state == 200:
        # TODO
        return generate_response_from_directory('init')

    # ---
    # default fallback
    return generate_response_from_directory('default')


# -----------------------------------------------------------------------------------------------------------------


def determine_attach_rich_menus(user: User):
    """
    依照現在的 user state決定要附加甚麼rich menu \\
    如果沒有，回傳 空字串
    """

    if user.state >= 200:
        return 'richmenu-87d4b4dbe02db04127c03ca06f5b9ba7'
    elif user.state >= 100:
        return 'richmenu-063fc5e646c13b50d27811df86d7c647'
    else:
        return ''


# -----------------------------------------------------------------------------------------------------------------

def generate_response_from_directory(response_name, *arguments) -> [SendMessage]:
    """
    Generate response from the folder "responses/{response_name}.json"
    If not found, reply with "I don't know"-like message
    """
    # the dir we wanna find
    replies = []
    path = os.path.join(fileutil.dir_resp, response_name+'.json')
    if os.path.exists(path):
        json_str = open(path, "r").read()
        replies = json_to_line_message_object(json_str)

    # Not found
    if len(replies) == 0:
        replies.append(TextSendMessage("I don't know what you mean..."))

    # Fill in parameters
    for r in replies:
        r.text = r.text.format(*arguments)

    return replies


def json_to_line_message_object(reply_json: str) -> [SendMessage]:
    """
    Parse reply.json, and return the corresponding line message model
    """

    # Get json
    jsonObj = json.loads(reply_json)
    return_array = []

    # parse json
    message_type = jsonObj['type']

    # Convert
    if message_type == 'text':
        return_array.append(TextSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'imagemap':
        return_array.append(ImagemapSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'template':
        return_array.append(TemplateSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'image':
        return_array.append(ImageSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'sticker':
        return_array.append(StickerSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'audio':
        return_array.append(AudioSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'location':
        return_array.append(LocationSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'flex':
        return_array.append(FlexSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'video':
        return_array.append(VideoSendMessage.new_from_json_dict(jsonObj))
    else:
        raise Exception("BAD reply json type:" + str(message_type))

    # return
    return return_array
