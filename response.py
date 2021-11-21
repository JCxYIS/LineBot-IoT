import random

from linebot.models import *

import mqtt_listener
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
        user.state = 1
        return generate_response_from_directory('welcome')

    # Basic state
    elif user.state == 1:
        # if message == 'temperature':
        #   return generate_response_from_directory('temperature', mqtt_listener.temperature, mqtt_listener.last_updated)
        # elif message == 'guess':
        #   user.state = 100
        #   return generate_response_from_directory('guess')
        return generate_response_from_directory(message)  # should remove this

    # Guess number
    # elif user.state == 100:
    #     user.state = 1
    #     if message == '48763':
    #         return generate_response_from_directory('guess_correct')
    #     else:
    #         return generate_response_from_directory('guess_wrong')

    # ---
    # default fallback
    return generate_response_from_directory('default')


# -----------------------------------------------------------------------------------------------------------------


def determine_attach_rich_menus(user: User):
    """
    依照現在的 user state決定要附加甚麼rich menu \\
    如果沒有，回傳 空字串
    """

    # if user.state == 1:
    #     return 'richmenu-XXXXXXXXXXXXXXXXXXXXXX'

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
        replies = json_to_line_message_object(json_str, *arguments)

    # Not found
    if len(replies) == 0:
        replies.append(TextSendMessage("I don't know what you mean..."))

    return replies


def json_to_line_message_object(reply_json: str, *args) -> [SendMessage]:
    """
    Parse reply.json, and return the corresponding line message model
    """

    # Get json
    json_obj = json.loads(reply_json)
    return_array = []

    # parse json
    # json_obj = {key: value.format(*args) for key, value in json_obj.items()}  #TODO: general func to parse texts

    # Convert
    message_object = None
    message_type = json_obj['type']
    if message_type == 'text':
        json_obj['text'] = json_obj['text'].format(*args)
        message_object = TextSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'imagemap':
        message_object = ImagemapSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'template':
        message_object = TemplateSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'image':
        message_object = ImageSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'sticker':
        message_object = StickerSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'audio':
        message_object = AudioSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'location':
        message_object = LocationSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'flex':
        message_object = FlexSendMessage.new_from_json_dict(json_obj)
    elif message_type == 'video':
        message_object = VideoSendMessage.new_from_json_dict(json_obj)
    else:
        raise Exception("BAD reply json type:" + str(message_type))

    return_array.append(message_object)

    # return
    return return_array
