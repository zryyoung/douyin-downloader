#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import tqdm

import argparse
import io
import os
import sys
import json
import yaml
import time

from apiproxy.douyin.douyin import Douyin
from apiproxy.douyin.download import Download
from apiproxy.douyin import douyin_headers
from apiproxy.common import utils

#app_path = "/data/data/com.download.douyin/files/chaquopy/AssetFinder/app/"
configModel = {
    "link": [],
    "path": os.getcwd(),  # 当前 Python 文件所在目录#None,#os.path.join(app_path),
    "music": True,
    "cover": True,
    "avatar": True,
    "json": True,
    "folderstyle": True,
    "mode": ["post"],
    "number": {
        "post": 0,
        "like": 0,
        "allmix": 0,
        "mix": 0,
        "music": 0,
    },
    'database': True,
    "increase": {
        "post": False,
        "like": False,
        "allmix": False,
        "mix": False,
        "music": False,
    },
    "thread": 5,
    "cookie": None

}


def argument():
    parser = argparse.ArgumentParser(description='抖音批量下载工具 使用帮助')
    parser.add_argument("--cmd", "-C", help="使用命令行(True)或者配置文件(False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--link", "-l",
                        help="作品(视频或图集)、直播、合集、音乐集合、个人主页的分享链接或者电脑浏览器网址, 可以设置多个链接(删除文案, 保证只有URL, https://v.douyin.com/kcvMpuN/ 或者 https://www.douyin.com/开头的)",
                        type=str, required=False, default=[], action="append")
    parser.add_argument("--path", "-p", help="下载保存位置, 默认当前文件位置",
                        type=str, required=False, default=os.getcwd())
    parser.add_argument("--music", "-m", help="是否下载视频中的音乐(True/False), 默认为True",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--cover", "-c", help="是否下载视频的封面(True/False), 默认为True, 当下载视频时有效",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--avatar", "-a", help="是否下载作者的头像(True/False), 默认为True",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--json", "-j", help="是否保存获取到的数据(True/False), 默认为True",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--folderstyle", "-fs", help="文件保存风格, 默认为True",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--mode", "-M", help="link是个人主页时, 设置下载发布的作品(post)或喜欢的作品(like)或者用户所有合集(mix), 默认为post, 可以设置多种模式",
                        type=str, required=False, default=[], action="append")
    parser.add_argument("--postnumber", help="主页下作品下载个数设置, 默认为0 全部下载",
                        type=int, required=False, default=0)
    parser.add_argument("--likenumber", help="主页下喜欢下载个数设置, 默认为0 全部下载",
                        type=int, required=False, default=0)
    parser.add_argument("--allmixnumber", help="主页下合集下载个数设置, 默认为0 全部下载",
                        type=int, required=False, default=0)
    parser.add_argument("--mixnumber", help="单个合集下作品下载个数设置, 默认为0 全部下载",
                        type=int, required=False, default=0)
    parser.add_argument("--musicnumber", help="音乐(原声)下作品下载个数设置, 默认为0 全部下载",
                        type=int, required=False, default=0)
    parser.add_argument("--database", "-d", help="是否使用数据库, 默认为True 使用数据库; 如果不使用数据库, 增量更新不可用",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--postincrease", help="是否开启主页作品增量下载(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--likeincrease", help="是否开启主页喜欢增量下载(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--allmixincrease", help="是否开启主页合集增量下载(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--mixincrease", help="是否开启单个合集下作品增量下载(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--musicincrease", help="是否开启音乐(原声)下作品增量下载(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--thread", "-t",
                        help="设置线程数, 默认5个线程",
                        type=int, required=False, default=5)
    parser.add_argument("--cookie", help="设置cookie, 格式: \"name1=value1; name2=value2;\" 注意要加冒号",
                        type=str, required=False, default='')
    args = parser.parse_args()
    if args.thread <= 0:
        args.thread = 5

    return args


def yamlConfig():
    #curPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    curPath = os.path.dirname(os.path.abspath(__file__))
    yamlPath = os.path.join(curPath, "config.yml")
    f = open(yamlPath, 'r', encoding='utf-8')
    cfg = f.read()
    configDict = yaml.load(stream=cfg, Loader=yaml.FullLoader)

    try:
        if configDict["link"] != None:
            configModel["link"] = configDict["link"]
    except Exception as e:
        print("[  警告  ]:link未设置, 程序退出...\r\n")
    try:
        if configDict["path"] != None:
            configModel["path"] = configDict["path"]
    except Exception as e:
        print("[  警告  ]:path未设置, 使用当前路径...\r\n")
    try:
        if configDict["music"] != None:
            configModel["music"] = configDict["music"]
    except Exception as e:
        print("[  警告  ]:music未设置, 使用默认值True...\r\n")
    try:
        if configDict["cover"] != None:
            configModel["cover"] = configDict["cover"]
    except Exception as e:
        print("[  警告  ]:cover未设置, 使用默认值True...\r\n")
    try:
        if configDict["avatar"] != None:
            configModel["avatar"] = configDict["avatar"]
    except Exception as e:
        print("[  警告  ]:avatar未设置, 使用默认值True...\r\n")
    try:
        if configDict["json"] != None:
            configModel["json"] = configDict["json"]
    except Exception as e:
        print("[  警告  ]:json未设置, 使用默认值True...\r\n")
    try:
        if configDict["folderstyle"] != None:
            configModel["folderstyle"] = configDict["folderstyle"]
    except Exception as e:
        print("[  警告  ]:folderstyle未设置, 使用默认值True...\r\n")
    try:
        if configDict["mode"] != None:
            configModel["mode"] = configDict["mode"]
    except Exception as e:
        print("[  警告  ]:mode未设置, 使用默认值post...\r\n")
    try:
        if configDict["number"]["post"] != None:
            configModel["number"]["post"] = configDict["number"]["post"]
    except Exception as e:
        print("[  警告  ]:post number未设置, 使用默认值0...\r\n")
    try:
        if configDict["number"]["like"] != None:
            configModel["number"]["like"] = configDict["number"]["like"]
    except Exception as e:
        print("[  警告  ]:like number未设置, 使用默认值0...\r\n")
    try:
        if configDict["number"]["allmix"] != None:
            configModel["number"]["allmix"] = configDict["number"]["allmix"]
    except Exception as e:
        print("[  警告  ]:allmix number未设置, 使用默认值0...\r\n")
    try:
        if configDict["number"]["mix"] != None:
            configModel["number"]["mix"] = configDict["number"]["mix"]
    except Exception as e:
        print("[  警告  ]:mix number未设置, 使用默认值0...\r\n")
    try:
        if configDict["number"]["music"] != None:
            configModel["number"]["music"] = configDict["number"]["music"]
    except Exception as e:
        print("[  警告  ]:music number未设置, 使用默认值0...\r\n")
    try:
        if configDict["database"] != None:
            configModel["database"] = configDict["database"]
    except Exception as e:
        print("[  警告  ]:database未设置, 使用默认值False...\r\n")
    try:
        if configDict["increase"]["post"] != None:
            configModel["increase"]["post"] = configDict["increase"]["post"]
    except Exception as e:
        print("[  警告  ]:post 增量更新未设置, 使用默认值False...\r\n")
    try:
        if configDict["increase"]["like"] != None:
            configModel["increase"]["like"] = configDict["increase"]["like"]
    except Exception as e:
        print("[  警告  ]:like 增量更新未设置, 使用默认值False...\r\n")
    try:
        if configDict["increase"]["allmix"] != None:
            configModel["increase"]["allmix"] = configDict["increase"]["allmix"]
    except Exception as e:
        print("[  警告  ]:allmix 增量更新未设置, 使用默认值False...\r\n")
    try:
        if configDict["increase"]["mix"] != None:
            configModel["increase"]["mix"] = configDict["increase"]["mix"]
    except Exception as e:
        print("[  警告  ]:mix 增量更新未设置, 使用默认值False...\r\n")
    try:
        if configDict["increase"]["music"] != None:
            configModel["increase"]["music"] = configDict["increase"]["music"]
    except Exception as e:
        print("[  警告  ]:music 增量更新未设置, 使用默认值False...\r\n")
    try:
        if configDict["thread"] != None:
            configModel["thread"] = configDict["thread"]
    except Exception as e:
        print("[  警告  ]:thread未设置, 使用默认值5...\r\n")
    try:
        if configDict["cookies"] != None:
            cookiekey = configDict["cookies"].keys()
            cookieStr = ""
            for i in cookiekey:
                cookieStr = cookieStr + i + "=" + configDict["cookies"][i] + "; "
            configModel["cookie"] = cookieStr
    except Exception as e:
        pass
    try:
        if configDict["cookie"] != None:
            configModel["cookie"] = configDict["cookie"]
    except Exception as e:
        pass





# def main():
  
    # old_stdout = sys.stdout
    # sys.stdout = buffer = io.StringIO()

    # print("调用python DouYinCommand.py main")
    # # print("Test Python")
    
    # start = time.time()  # 开始时间

    # args = argument()

    # if args.cmd:
        # configModel["link"] = args.link
        # configModel["path"] = args.path
        # configModel["music"] = args.music
        # configModel["cover"] = args.cover
        # configModel["avatar"] = args.avatar
        # configModel["json"] = args.json
        # configModel["folderstyle"] = args.folderstyle
        # if args.mode == None or args.mode == []:
            # args.mode = []
            # args.mode.append("post")
        # configModel["mode"] = list(set(args.mode))
        # configModel["number"]["post"] = args.postnumber
        # configModel["number"]["like"] = args.likenumber
        # configModel["number"]["allmix"] = args.allmixnumber
        # configModel["number"]["mix"] = args.mixnumber
        # configModel["number"]["music"] = args.musicnumber
        # configModel["database"] = args.database
        # configModel["increase"]["post"] = args.postincrease
        # configModel["increase"]["like"] = args.likeincrease
        # configModel["increase"]["allmix"] = args.allmixincrease
        # configModel["increase"]["mix"] = args.mixincrease
        # configModel["increase"]["music"] = args.musicincrease
        # configModel["thread"] = args.thread
        # configModel["cookie"] = args.cookie
    # else:
        # yamlConfig()

    # if configModel["link"] == []:
        # return

    # if configModel["cookie"] is not None and configModel["cookie"] != "":
        # douyin_headers["Cookie"] = configModel["cookie"]

    # configModel["path"] = os.path.abspath(configModel["path"])
    # print("[  提示  ]:数据保存路径 " + configModel["path"])
    # if not os.path.exists(configModel["path"]):
        # os.mkdir(configModel["path"])

    # dy = Douyin(database=configModel["database"])
    # dl = Download(thread=configModel["thread"], music=configModel["music"], cover=configModel["cover"],
                  # avatar=configModel["avatar"], resjson=configModel["json"],
                  # folderstyle=configModel["folderstyle"])

    # for link in configModel["link"]:
        # print("--------------------------------------------------------------------------------")
        # print("[  提示  ]:正在请求的链接: " + link + "\r\n")
        # url = dy.getShareLink(link)
        # key_type, key = dy.getKey(url)
        # if key_type == "user":
            # print("[  提示  ]:正在请求用户主页下作品\r\n")
            # data = dy.getUserDetailInfo(sec_uid=key)
            # nickname = ""
            # if data is not None and data != {}:
                # nickname = utils.replaceStr(data['user']['nickname'])

            # userPath = os.path.join(configModel["path"], "user_" + nickname + "_" + key)
            # if not os.path.exists(userPath):
                # os.mkdir(userPath)

            # for mode in configModel["mode"]:
                # print("--------------------------------------------------------------------------------")
                # print("[  提示  ]:正在请求用户主页模式: " + mode + "\r\n")
                # if mode == 'post' or mode == 'like':
                    # datalist = dy.getUserInfo(key, mode, 35, configModel["number"][mode], configModel["increase"][mode])
                    # if datalist is not None and datalist != []:
                        # modePath = os.path.join(userPath, mode)
                        # if not os.path.exists(modePath):
                            # os.mkdir(modePath)
                        # dl.userDownload(awemeList=datalist, savePath=modePath)
                # elif mode == 'mix':
                    # mixIdNameDict = dy.getUserAllMixInfo(key, 35, configModel["number"]["allmix"])
                    # if mixIdNameDict is not None and mixIdNameDict != {}:
                        # for mix_id in mixIdNameDict:
                            # print(f'[  提示  ]:正在下载合集 [{mixIdNameDict[mix_id]}] 中的作品\r\n')
                            # mix_file_name = utils.replaceStr(mixIdNameDict[mix_id])
                            # datalist = dy.getMixInfo(mix_id, 35, 0, configModel["increase"]["allmix"], key)
                            # if datalist is not None and datalist != []:
                                # modePath = os.path.join(userPath, mode)
                                # if not os.path.exists(modePath):
                                    # os.mkdir(modePath)
                                # dl.userDownload(awemeList=datalist, savePath=os.path.join(modePath, mix_file_name))
                                # print(f'[  提示  ]:合集 [{mixIdNameDict[mix_id]}] 中的作品下载完成\r\n')
        # elif key_type == "mix":
            # print("[  提示  ]:正在请求单个合集下作品\r\n")
            # datalist = dy.getMixInfo(key, 35, configModel["number"]["mix"], configModel["increase"]["mix"], "")
            # if datalist is not None and datalist != []:
                # mixname = utils.replaceStr(datalist[0]["mix_info"]["mix_name"])
                # mixPath = os.path.join(configModel["path"], "mix_" + mixname + "_" + key)
                # if not os.path.exists(mixPath):
                    # os.mkdir(mixPath)
                # dl.userDownload(awemeList=datalist, savePath=mixPath)
        # elif key_type == "music":
            # print("[  提示  ]:正在请求音乐(原声)下作品\r\n")
            # datalist = dy.getMusicInfo(key, 35, configModel["number"]["music"], configModel["increase"]["music"])

            # if datalist is not None and datalist != []:
                # musicname = utils.replaceStr(datalist[0]["music"]["title"])
                # musicPath = os.path.join(configModel["path"], "music_" + musicname + "_" + key)
                # if not os.path.exists(musicPath):
                    # os.mkdir(musicPath)
                # dl.userDownload(awemeList=datalist, savePath=musicPath)
        # elif key_type == "aweme":
            # print("[  提示  ]:正在请求单个作品\r\n")
            # datanew, dataraw = dy.getAwemeInfo(key)
            # if datanew is not None and datanew != {}:
                # datalist = []
                # datalist.append(datanew)
                # awemePath = os.path.join(configModel["path"], "aweme")
                # if not os.path.exists(awemePath):
                    # os.mkdir(awemePath)
                # dl.userDownload(awemeList=datalist, savePath=awemePath)
        # elif key_type == "live":
            # print("[  提示  ]:正在进行直播解析\r\n")
            # live_json = dy.getLiveInfo(key)
            # if configModel["json"]:
                # livePath = os.path.join(configModel["path"], "live")
                # if not os.path.exists(livePath):
                    # os.mkdir(livePath)
                # live_file_name = utils.replaceStr(key + live_json["nickname"])
                # # 保存获取到json
                # print("[  提示  ]:正在保存获取到的信息到result.json\r\n")
                # with open(os.path.join(livePath, live_file_name + ".json"), "w", encoding='utf-8') as f:
                    # f.write(json.dumps(live_json, ensure_ascii=False, indent=2))
                    # f.close()

    # end = time.time()  # 结束时间
    # print('\n' + '[下载完成]:总耗时: %d分钟%d秒\n' % (int((end - start) / 60), ((end - start) % 60)))  # 输出下载用时时间
    # sys.stdout = old_stdout
    # return buffer.getvalue()


def log(msg):
    with open("/sdcard/Python_debug_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def log_print(msg):
    print(msg)
    log(msg)

def main():
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    log_print("调用python DouYinCommand.py main")

    start = time.time()

    args = argument()

    if args.cmd:
        log_print("命令行调用")
        configModel["link"] = args.link
        configModel["path"] = args.path
        configModel["music"] = args.music
        configModel["cover"] = args.cover
        configModel["avatar"] = args.avatar
        configModel["json"] = args.json
        configModel["folderstyle"] = args.folderstyle
        if args.mode == None or args.mode == []:
            args.mode = []
            args.mode.append("post")
        configModel["mode"] = list(set(args.mode))
        configModel["number"]["post"] = args.postnumber
        configModel["number"]["like"] = args.likenumber
        configModel["number"]["allmix"] = args.allmixnumber
        configModel["number"]["mix"] = args.mixnumber
        configModel["number"]["music"] = args.musicnumber
        configModel["database"] = args.database
        configModel["increase"]["post"] = args.postincrease
        configModel["increase"]["like"] = args.likeincrease
        configModel["increase"]["allmix"] = args.allmixincrease
        configModel["increase"]["mix"] = args.mixincrease
        configModel["increase"]["music"] = args.musicincrease
        configModel["thread"] = args.thread
        configModel["cookie"] = args.cookie
    else:
        log_print("配置文件调用")
        yamlConfig()

    if configModel["link"] == []:
        return

    if configModel["cookie"] is not None and configModel["cookie"] != "":
        douyin_headers["Cookie"] = configModel["cookie"]

    configModel["path"] = os.path.abspath(configModel["path"])
    log_print("[  提示  ]:数据保存路径 " + configModel["path"])
    if not os.path.exists(configModel["path"]):
        os.mkdir(configModel["path"])

    dy = Douyin(database=configModel["database"])
    dl = Download(thread=configModel["thread"], music=configModel["music"], cover=configModel["cover"],
                  avatar=configModel["avatar"], resjson=configModel["json"],
                  folderstyle=configModel["folderstyle"])

    for link in configModel["link"]:
        log_print("--------------------------------------------------------------------------------")
        log_print("[  提示  ]:正在请求的链接: " + link + "\r\n")
        url = dy.getShareLink(link)
        key_type, key = dy.getKey(url)
        if key_type == "user":
            log_print("[  提示  ]:正在请求用户主页下作品\r\n")
            data = dy.getUserDetailInfo(sec_uid=key)
            nickname = ""
            if data is not None and data != {}:
                nickname = utils.replaceStr(data['user']['nickname'])

            userPath = os.path.join(configModel["path"], "user_" + nickname + "_" + key)
            if not os.path.exists(userPath):
                os.mkdir(userPath)

            for mode in configModel["mode"]:
                log_print("--------------------------------------------------------------------------------")
                log_print("[  提示  ]:正在请求用户主页模式: " + mode + "\r\n")
                if mode == 'post' or mode == 'like':
                    datalist = dy.getUserInfo(key, mode, 35, configModel["number"][mode], configModel["increase"][mode])
                    if datalist is not None and datalist != []:
                        modePath = os.path.join(userPath, mode)
                        if not os.path.exists(modePath):
                            os.mkdir(modePath)
                        dl.userDownload(awemeList=datalist, savePath=modePath)
                elif mode == 'mix':
                    mixIdNameDict = dy.getUserAllMixInfo(key, 35, configModel["number"]["allmix"])
                    if mixIdNameDict is not None and mixIdNameDict != {}:
                        for mix_id in mixIdNameDict:
                            log_print(f'[  提示  ]:正在下载合集 [{mixIdNameDict[mix_id]}] 中的作品\r\n')
                            mix_file_name = utils.replaceStr(mixIdNameDict[mix_id])
                            datalist = dy.getMixInfo(mix_id, 35, 0, configModel["increase"]["allmix"], key)
                            if datalist is not None and datalist != []:
                                modePath = os.path.join(userPath, mode)
                                if not os.path.exists(modePath):
                                    os.mkdir(modePath)
                                dl.userDownload(awemeList=datalist, savePath=os.path.join(modePath, mix_file_name))
                                log_print(f'[  提示  ]:合集 [{mixIdNameDict[mix_id]}] 中的作品下载完成\r\n')
        elif key_type == "mix":
            log_print("[  提示  ]:正在请求单个合集下作品\r\n")
            datalist = dy.getMixInfo(key, 35, configModel["number"]["mix"], configModel["increase"]["mix"], "")
            if datalist is not None and datalist != []:
                mixname = utils.replaceStr(datalist[0]["mix_info"]["mix_name"])
                mixPath = os.path.join(configModel["path"], "mix_" + mixname + "_" + key)
                if not os.path.exists(mixPath):
                    os.mkdir(mixPath)
                dl.userDownload(awemeList=datalist, savePath=mixPath)
        elif key_type == "music":
            log_print("[  提示  ]:正在请求音乐(原声)下作品\r\n")
            datalist = dy.getMusicInfo(key, 35, configModel["number"]["music"], configModel["increase"]["music"])

            if datalist is not None and datalist != []:
                musicname = utils.replaceStr(datalist[0]["music"]["title"])
                musicPath = os.path.join(configModel["path"], "music_" + musicname + "_" + key)
                if not os.path.exists(musicPath):
                    os.mkdir(musicPath)
                dl.userDownload(awemeList=datalist, savePath=musicPath)
        elif key_type == "aweme":
            log_print("[  提示  ]:正在请求单个作品\r\n")
            datanew, dataraw = dy.getAwemeInfo(key)
            if datanew is not None and datanew != {}:
                datalist = []
                datalist.append(datanew)
                awemePath = os.path.join(configModel["path"], "aweme")
                if not os.path.exists(awemePath):
                    os.mkdir(awemePath)
                dl.userDownload(awemeList=datalist, savePath=awemePath)
        elif key_type == "live":
            log_print("[  提示  ]:正在进行直播解析\r\n")
            live_json = dy.getLiveInfo(key)
            if configModel["json"]:
                livePath = os.path.join(configModel["path"], "live")
                if not os.path.exists(livePath):
                    os.mkdir(livePath)
                live_file_name = utils.replaceStr(key + live_json["nickname"])
                log_print("[  提示  ]:正在保存获取到的信息到result.json\r\n")
                with open(os.path.join(livePath, live_file_name + ".json"), "w", encoding='utf-8') as f:
                    f.write(json.dumps(live_json, ensure_ascii=False, indent=2))
                    f.close()

    end = time.time()
    log_print('\n' + '[下载完成]:总耗时: %d分钟%d秒\n' % (int((end - start) / 60), ((end - start) % 60)))
    sys.stdout = old_stdout
    return buffer.getvalue()
    
    
if __name__ == "__main__":
    main()
