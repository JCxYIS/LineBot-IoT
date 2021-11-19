import os
import tempfile
import threading
import traceback

from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, AudioMessage

from linebot import LineBotApi
from linebot.webhook import WebhookHandler
from flask import Flask, request, Response

import fileutil
import mqtt_listener
import response
import settings
import user
from settings import LINEBOT_CHANNEL_ACCESS_TOKEN, LINEBOT_CHANNEL_SECRET

# Line Bot APIs
# For More Information: https://github.com/line/line-bot-sdk-python
linebot_api = LineBotApi(LINEBOT_CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(LINEBOT_CHANNEL_SECRET)

# mqtt listener
mqtt_listener.init()

# Flask Server
app = Flask(__name__, static_folder='static')
# app.run(threaded=True, host='0.0.0.0', port=settings.PORT)


# ###################################################################################

# root route
@app.route('/')
def root_route():
    return Response('Stay Cool')


# LINE POST router
@app.route('/callback', methods=['POST'])
def callback():
    # X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # print(body, signature)
        webhook_handler.handle(body, signature)
        return 'OK'
    except:
        # print(e)
        traceback.print_exc()
        app.logger.error(traceback.format_exc())
        return Response('Error!', 500)


# ###################################################################################

@webhook_handler.add(MessageEvent)
def on_message(event):
    """
    when our bot received message
    """

    # variables
    my_user = user.getuser(event.source.user_id)  # user model
    msg_message = ''                              # text of message
    msg_attachment_path = ''                      # local attachment path of that message

    # Determine type of msg
    attachment_ext = ''  # extension of a file
    if isinstance(event.message, TextMessage):
        msg_message = str(event.message.text)
        print('[MSG]', msg_message, flush=True)
    elif isinstance(event.message, ImageMessage):
        attachment_ext = 'jpg'
        print('[IMG_MSG]', flush=True)
    elif isinstance(event.message, VideoMessage):
        attachment_ext = 'mp4'
        print('[VID_MSG]', flush=True)
    elif isinstance(event.message, AudioMessage):
        attachment_ext = 'm4a'
        print('[VOC_MSG]', flush=True)

    # Download attachment if presented
    if attachment_ext:
        message_content = linebot_api.get_message_content(event.message.id)
        # Download to temp location
        with tempfile.NamedTemporaryFile(dir=fileutil.dir_temp, prefix=attachment_ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
            msg_attachment_path = tempfile_path + '.' + attachment_ext
            os.rename(tempfile_path, msg_attachment_path)

    # Special Commands
    if msg_message == 'reset':
        my_user.state = 0
        message = TextSendMessage(text='Your state has been reset.')
    elif msg_message == 'state':
        message = TextSendMessage(text='state=' + str(my_user.state) + ' \nUID：' + str(my_user.uid))
    else:
        # General Reply (responses)
        message = response.make_response(my_user, msg_message, msg_attachment_path, attachment_ext)

    # Send replies
    linebot_api.reply_message(event.reply_token, message)

    # Bind Rich Menu
    # attach_rich_menu_id = response.determine_attach_rich_menus(my_user)
    # if attach_rich_menu_id:
    #     linebot_api.link_rich_menu_to_user(event.source.user_id, attach_rich_menu_id)
    # else:
    #     linebot_api.unlink_rich_menu_from_user(event.source.user_id)