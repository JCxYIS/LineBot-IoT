"""
Settings
You can change these setting manually in code or by setting enviromental variable
"""
import os

# Is debug?
IS_DEBUG = False

# Note: When deployed to Heroku, the enviroment variable "PORT" will be used
PORT = os.environ.get("PORT", 3000)

# Line bot profile settings
LINEBOT_CHANNEL_ACCESS_TOKEN = os.environ.get("LINEBOT_CHANNEL_ACCESS_TOKEN")
LINEBOT_CHANNEL_SECRET = os.environ.get("LINEBOT_CHANNEL_SECRET")

scope = "6157d4893ea438209f27b415"
username = "6157df7c3ea438209f27b422"
password = "test"