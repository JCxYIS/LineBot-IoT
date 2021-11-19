import os
import tempfile
import time
import uuid


def abs_path(relative_path):
    """
    combine relative path to abs path
    """
    return os.path.join(os.path.dirname(__file__), relative_path)


def mkdirs(relative_dir_path):
    """
    mkdirs
    """
    if not os.path.exists(abs_path(relative_dir_path)):  # 準備好資料夾
        os.makedirs(relative_dir_path)


def create_random_fileName_in_temp_dir(ext):
    """
    在暫存資料夾產生一個隨機檔名
    ext: extension
    """
    return os.path.join(dir_temp, str(time.time()) + str(uuid.uuid4()) + "." + ext)


# def temp_path_to_server_path(absTempPath):
#     """
#     找出暫存檔案在伺服器裡面的位置 \\
#     目前不會判斷暫存檔案484真的在暫存資料夾
#     """
#     return (request.host_url + os.path.join('static', 'temp', os.path.basename(absTempPath))).replace('http://',
#                                                                                                       'https://')


############################################################################################

# 暫存檔案夾
dir_temp = abs_path('static/temp')  # temp directory
dir_resp = abs_path('responses')     # response directory

mkdirs(dir_temp)
