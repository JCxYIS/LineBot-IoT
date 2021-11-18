import traceback

from linebot.models import MessageEvent, TextMessage, TextSendMessage

from linebot import LineBotApi
from linebot.webhook import WebhookHandler
from flask import Flask, request, Response

from settings import LINEBOT_CHANNEL_ACCESS_TOKEN, LINEBOT_CHANNEL_SECRET

# Line Bot APIs
# For More Information: https://github.com/line/line-bot-sdk-python
linebot_api = LineBotApi(LINEBOT_CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(LINEBOT_CHANNEL_SECRET)

# Flask Server
app = Flask(__name__, static_folder='static')


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

@webhook_handler.add(MessageEvent, message=TextMessage)
def echo(event):
    linebot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello, " + str(event.message.text))
    )
