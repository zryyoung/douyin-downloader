import io
import os
import DouYinCommand

def log(msg):
    with open("/sdcard/Python_main_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def main(args):  # args 是一个字符串
    log("agrs:"+args+"\n")
    # 分割参数字符串
    arg_list = args.split(",")
    
    log("Received args: {}".format(arg_list))  # 日志记录接收到的参数

    # 可以设置 sys.argv 为分割后的参数
    import sys
    sys.argv = ["DouYinCommand.py"] + arg_list

    print("sys.argv:", sys.argv)  # 可选调试打印
    log("sys.argv: {}".format(sys.argv))  # 可选调试打印

    DouYinCommand.main()  # 调用自己定义的逻辑
