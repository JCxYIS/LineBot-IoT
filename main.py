from linebot import LineBotApi
from linebot.webhook import WebhookHandler
from flask import Flask, request, Response

from settings import LINEBOT_CHANNEL_ACCESS_TOKEN, LINEBOT_CHANNEL_SECRET



# Line Bot APIs
linebot_api = LineBotApi( LINEBOT_CHANNEL_ACCESS_TOKEN )
webhook_handler = WebhookHandler( LINEBOT_CHANNEL_SECRET )

# Flask Server
app = Flask(__name__, static_folder='static')