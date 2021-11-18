from linebot.models import *

from user import User

import os
import json
import pic_handle
import fileutil


def determine_response(myuser: User, message: str, attachmentPath: str, attachmentExt: str) -> SendMessage:
    """
    製作回覆
    myuser: my user
    meesage: message, may be ''
    attachmentPath: abs path, may be ''
    attachmentExt: extension of attachment (jpg, mp4, m4a), may be ''
    """

    # 起始
    if myuser.state == 0:
        myuser.state = 1
        return generate_response_from_directories('init')

    # 開始關注
    elif myuser.state == 1:
        if message == '開始製作長輩圖':
            myuser.state = 100
            return response_templates.img_cor_select_pic()
        else:
            return generate_response_from_directories('init')

    # 開始製作長輩圖
    elif myuser.state == 100:
        if message == 'goupload':
            myuser.state = 101
            return response_templates.flex_acoustic_message('開始上傳', '給我你要的圖片(也可以直接輸入網址)', 'a')
        elif message == 'retry':
            return response_templates.img_cor_select_pic()
            # TODO selected pic
        elif message.startswith('https') and 'jpg' in message:
            resurl = pic_handle.download_image(message)
            if resurl:
                myuser.state = 110
                myuser.edit_pic_filepath = resurl
                myuser.edit_pic_editions = []
                myuser.edit_pic_editingIndex = 0
            else:
                return response_templates.flex_acoustic_message('不對餒', '不是個有效的圖片網址 (jpg)', 'a')

            # return response_templates.flex_acoustic_message('很抱歉', '目前圖片範本暫不開放使用，需等待貧果審核通過', 'a')

    # 上傳圖片
    elif myuser.state == 101:
        if attachmentPath and attachmentExt == 'jpg':
            myuser.state = 110

            # user edit_pic狀態
            myuser.edit_pic_filepath = attachmentPath
            myuser.edit_pic_editions = []
            myuser.edit_pic_editingIndex = 0

            return response_templates.flex_acoustic_message(
                '好耶！上傳成功', '點擊下方選項按鈕，開始修圖吧', '好耶，接下來來修圖吧！', temp_path_to_server_path(attachmentPath))

    # 選擇功能
    elif myuser.state == 110:
        # input text
        if message == 'addText':
            myuser.state = 111
            return response_templates.flex_acoustic_message('輸入文字', '給我你要添加的文字', '新文字編輯')

        # TODO addFilter

        elif message == '動作 2':  # TODO => editlayer
            myuser.state = 121
            if len(myuser.edit_pic_editions) == 0:
                return TextSendMessage('目前沒有圖層，沒啥好改的...')
            else:
                replyStr = '你想更改以下哪一圖層呢？\n'
                for i in range(0, len(myuser.edit_pic_editions)):
                    replyStr += '第' + str(i) + '層：' + str(myuser.edit_pic_editions[i]) + '\n'
                replyStr = '\n輸入想編輯的層數。 (格式：數字)'

            return TextSendMessage(replyStr)

        elif message == 'finish':
            myuser.state = 0
            return response_templates.flex_acoustic_message('完成', '感謝使用長輩圖生成器！', '！')

            # 輸入文字
    elif myuser.state == 111:
        if message:
            myuser.state = 112

            # 加user edit_pic狀態
            newEdition = pic_handle.PicEdition_AddText(message, 50, 50, 100, 255, 255, 255, 255)
            myuser.edit_pic_editions.append(newEdition)
            myuser.edit_pic_editingIndex = len(myuser.edit_pic_editions) - 1

            return handle_Pic_and_reply(myuser)

    # 調整{文字}的rich menu
    elif myuser.state == 112:

        if message == 'done':
            myuser.state = 110
            return response_templates.flex_acoustic_message('繼續修改！', '滿意的話就按下finish吧！', 'd0')

        elif message == 'delete':
            myuser.edit_pic_editions.remove(myuser.edit_pic_editingIndex)
            myuser.state = 110
            return response_templates.flex_acoustic_message('不滿意退貨', '已刪除這個圖層...', 'd0')


        elif message == 'move':
            myuser.state = 113
            return response_templates.flex_acoustic_message('輸入你要移動的新座標',
                                                            '(現在：' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].posx) + ' ' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].posy) +
                                                            ') 格式：{x} {y} (各為0~100) (如：87 63)', '0')

        elif message == 'color':
            myuser.state = 114
            return response_templates.flex_acoustic_message('輸入你要更換的顏色',
                                                            '(現在：' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].colorr) + ' ' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].colorg) + ' ' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].colorb) + ' ' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].colora) +
                                                            ') 格式：{rgba color (各為0~255) (如：255 153 166 255)}', '0')

        elif message == 'size':
            myuser.state = 115
            return response_templates.flex_acoustic_message('輸入你要變更的大小',
                                                            '(現在：' +
                                                            str(myuser.edit_pic_editions[
                                                                    myuser.edit_pic_editingIndex].size) +
                                                            ') 格式：{數字}', '0')

            # 移動文字的方向與距離
    elif myuser.state == 113:
        numArr = message.split(' ')
        if len(numArr) != 2:
            return TextSendMessage('你必須輸入 2 個 0 ~ 100 的數字！');
        try:
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].posx = float(numArr[0]) % 150
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].posy = float(numArr[1]) % 150
            myuser.state = 112
            return handle_Pic_and_reply(myuser)
        except ValueError:
            return TextSendMessage('你必須輸入 2 個 0 ~ 100 的數字...');

    # 更換文字的顏色
    elif myuser.state == 114:
        colorArr = message.split(' ')
        if len(colorArr) != 3:
            return TextSendMessage('你必須輸入 3 個 0 ~ 255 的整數！');
        try:
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].colorr = abs(int(colorArr[0]) % 256)
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].colorg = abs(int(colorArr[1]) % 256)
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].colorb = abs(int(colorArr[2]) % 256)
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].colora = 255  # abs( int(colorArr[3]) % 256 )
            myuser.state = 112
            return handle_Pic_and_reply(myuser)
        except ValueError:
            return TextSendMessage('你必須輸入 3 個 0 ~ 255 的整數...');

    # 文字的大小
    elif myuser.state == 115:
        try:
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].size = abs(int(message) % 48764)
            myuser.state = 112
            return handle_Pic_and_reply(myuser)
        except ValueError:
            return TextSendMessage('你必須輸入 1 個 0 ~ 48763 的整數...');

    # 文字的敘述
    elif myuser.state == 116:
        if message:
            myuser.edit_pic_editions[myuser.edit_pic_editingIndex].text = message
            myuser.state = 112
            return handle_Pic_and_reply(myuser)
        else:
            return TextSendMessage('你必須輸入要更改的文字...');

    # 調整指定某一層
    elif myuser.state == 121:
        myuser.state = 110
        try:
            index = int(message)
            if index >= len(myuser.edit_pic_editions) or index < 0:
                return response_templates.flex_acoustic_message('太多了會壞掉', '你輸入的index怪怪的')

            if isinstance(myuser.edit_pic_editions[index], pic_handle.PicEdition_AddText):
                myuser.edit_pic_editingIndex = index
                myuser.state = 112
                return response_templates.flex_acoustic_message('繼續編輯吧', '繼續加油！')
            elif isinstance(myuser.edit_pic_editions[index], pic_handle.PicEdition_AddFilter):
                myuser.edit_pic_editions.remove(index)
                return TextSendMessage('先幫你刪掉這個濾鏡了，要的話再加')
            else:
                return response_templates.flex_acoustic_message('ㄅ欠', '目前無法變更此圖層...')

        except ValueError:
            return response_templates.flex_acoustic_message('？？？', '我要的是數字餒')

    # default fallback
    return generate_response_from_directories('default')


# -----------------------------------------------------------------------------------------------------------------

def handle_Pic_and_reply(myuser: User):
    """
    進行修圖，並把結果利用ImageSendMessage丟回使用者
    """
    path = pic_handle.pic_handle(myuser.edit_pic_filepath, myuser.edit_pic_editions)
    thumb = pic_handle.createThumb(path)
    return ImageSendMessage(fileutil.temp_path_to_server_path(path), fileutil.temp_path_to_server_path(thumb))


# -----------------------------------------------------------------------------------------------------------------


def determine_attach_rich_menus(myuser: User):
    """
    依照現在的 user state決定要附加甚麼rich menu \\
    如果沒有，回傳 空字串
    """

    if myuser.state == 110:
        return 'richmenu-87d4b4dbe02db04127c03ca06f5b9ba7'

    # 調整文字位置
    elif myuser.state == 112:
        return 'richmenu-063fc5e646c13b50d27811df86d7c647'

    else:
        return ''


# -----------------------------------------------------------------------------------------------------------------

def generate_response_from_directories(reqDirName) -> SendMessage:
    """
    從 Response 資料夾抓相應的 Response
    """
    json = get_reply_json_string_from_directories(reqDirName)
    if json:
        return parse_reply_json(json)
    else:
        return response_templates.flex_acoustic_message('我聽不懂耶', '看一下左下角有沒有三橫線按鈕(功能選單)？', '林北老灰啊聽毋啦')


def get_reply_json_string_from_directories(dirName) -> str:
    """
    從 Response 資料夾抓相應的 response.json 字串 \\
    沒有的話回傳None
    """

    dirName = os.path.join(dir_resp, dirName)

    # 回應資料夾存在！
    if os.path.exists(dirName):
        # print("Response Dir Name Exist! ", dirName)
        replyJsonPath = os.path.join(dirName, 'reply.json')

        # 回應資料夾裡面存在 reply.json
        if os.path.exists(replyJsonPath):
            f = open(replyJsonPath, "r").read()
            return f
        else:
            print("[WARNING] 回應資料夾裡面不存在 reply.json！ ", replyJsonPath)
            return ''
    else:
        return ''


def parse_reply_json(replyJson: str):
    """
    解析reply.json，回傳相應的物件
    """

    # Get json
    jsonObj = json.loads(replyJson)
    returnArray = []

    # parse json
    message_type = jsonObj['type']

    # 轉換
    if message_type == 'text':
        returnArray.append(TextSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'imagemap':
        returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'template':
        returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'image':
        returnArray.append(ImageSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'sticker':
        returnArray.append(StickerSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'audio':
        returnArray.append(AudioSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'location':
        returnArray.append(LocationSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'flex':
        returnArray.append(FlexSendMessage.new_from_json_dict(jsonObj))
    elif message_type == 'video':
        returnArray.append(VideoSendMessage.new_from_json_dict(jsonObj))
    else:
        raise BaseException("爛json格式:" + str(message_type))

        # 回傳
    return returnArray