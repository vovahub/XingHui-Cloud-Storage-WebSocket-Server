# 该项目的开源链接:https://github.com/vovahub/XingHui-Cloud-Storage-WebSocket-Server
"""
我很抱歉,作为一个自学python的孩子我的英文水平还做不到全部使用英文命名,这导致整个代码全是汉语,这或许很糟糕...:(
请原谅我的不负责
I am very sorry. As a child who is self-learning Python,
my English level is not yet enough to use English names for everything, 
which has resulted in the entire code being in Chinese. 
This may be very bad... :(
Please forgive my irresponsibility.
"""
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
import json
from datetime import datetime
import time
import os
import gc
import psutil
import random

GUI = True
服务器版本 = "0.1.7"
服务器版本更新内容 = [
    "0.0.1_作者大脑褶皱被抚平🧠✋突然想做个主要面向图形化编程的好用的云存储,并打算用那微薄的python知识随便写一个MVP"
    "~0.0.4_刚完成正常功能,完成基础WS服务器+存储逻辑",
    "0.0.5_增加并完善UAT系统",
    "0.0.6_UAT更加严格并修复dump数据为int类型导致的报错问题",
    "0.0.7_更改了'欢迎语'为文言文格式,更新了更加有趣的报错",
    "0.0.8_修复检验dump数据大小出现的数据大小单位混乱问题(论当时b/kb搞混了这块)",
    "0.0.9_改了一个文本和数据检查",
    "0.1.0_修改了用户查看账户状态时'您还可用(MB)'的浮点精度问题",
    "0.1.1_修复了逻辑漏洞(全新的UAT账户初次调用时,因对应的数据目录尚未创建,在计算存储占用时触发了“系统找不到指定路径”的WinError错误)",
    "0.1.2_做完了第一个BETA版本的RtCVS功能,但还有bug或许需要修一修",
    "0.1.3_修复了'路径遍历攻击'漏洞;我的天十分抱歉我的电脑基础知识不够,已经修复了(QMQ没人说过还有回退路径这个玩法啊...EEE)",
    "0.1.4_修改了UAT格式让其支持自定义权限系统并在代码中支持Ciallo～(∠・ω< )⌒☆",
    "0.1.5_稍微修改了CV部分",
    "0.1.6_开始学pyglet啦!所以随便写了一个GUI",
    "0.1.7_修复了下GUI的部分问题,顺便加了一个连续运行时间,这或许会让运营者更加自豪"
]
欢迎语 = '''~~~欢迎语👏and免责约言~~~
欢迎接入星辉服务器！储纳之用，分文不取。诸君数据，必守秘如瓶。然稳妥计，还望自备密文加密之法为善。
----免责约言----
虽竭力保连接与数据之安稳可访，然若逢突发或检修之时，或难连至本服务器。倘有损遗，恕难担责。必当竭力避此等事耳。
----作者(服务器代码制作和运营)----
作者名:ツ_5ZGA5ZG8fijCr+KWvcKvfil+
作者邮箱:vova1525@foxmail.com
属室邮箱:MFX_studio@126.com
属室QQ群:1073454623
（注：室名略宣耳。）
----感谢----
谨谢ChmlFrp襄助内网穿透之劳，
并感MFXstudio众员与F_code协力同心，
更谢诸君不行恶意攻袭之德，
诸般厚谊，皆铭于心
!----附言​----!
服务器运维实需成本，为爱发电固佳，若蒙捐助以破会员之制，则幸甚至哉！
支付宝/声讯：13275773306
（穷连冰糕亦难求，乐助五元足盛情！泣谢QwQ）
'''
print(r'''
 __  __   __   __   __   ______   __  __   __  __   __   __     __   ______    
/\_\_\_\ /\ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\ \/\ \ /\ \ /\ \  _ \ \ /\  ___\   
\/_/\_\/_\ \ \\ \ \-.  \\ \ \__ \\ \  __ \\ \ \_\ \\ \ \\ \ \/ ".\ \\ \___  \  
  /\_\/\_\\ \_\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\\ \_\\ \__/".~\_\\/\_____\ 
  \/_/\/_/ \/_/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/ \/_/ \/_/   \/_/ \/_____/
''')

运行开始时间 = time.time()
父目录 = "D:/"
try:
    日志目录 = f"{父目录}XingHui_WS/log"
    os.makedirs(日志目录, exist_ok=True)
    数据目录 = f"{父目录}XingHui_WS/data"
    os.makedirs(数据目录, exist_ok=True)
    配置目录 = f"{父目录}XingHui_WS/config"
    os.makedirs(配置目录, exist_ok=True)
except Exception as e:
    print(f"初始化目录失败!{e}")

try:
    if not os.path.exists(f"{配置目录}/UAT.json"):
        with open(f"{配置目录}/UAT.json", "w", encoding="utf-8") as f:
            示例 = [
                {
                    "token": "GG", # 用户的token
                    "allowance": 1000, # 调用次数配额,到某一时刻将'total_uses'重新设置为设定的配额
                    "total_uses": 1000, # 可用次数,一段时间内可以调用的次数
                    "RtCVS_limit": 2, # 实时同步云变量限制大小(mb),预设是2MB
                    "storage_limit": 2048, # 存储限制大小(mb),预设是2gb
                    "project_name": "共用账户", # 用户申请凭证时写的使用项目名
                    "created_time": 1770626390.8700256, # 账户创建时间(供机器阅读的)
                    "H_created_time": "2010.10.01/16:39:50", # 账户创建时间(供人阅读的)
                    "project_application_reason": "c", # 申请的理由
                    "project_application_usage": "c", # 申请的用途,比如"用在网页中的云存储",一般靠这个修改'allowance'
                    "contact_email": "c", # 申请人的邮箱,方便以后的交流
                    "total_calls": 0, # 累计已经调用过多少次
                    "used_storage": 0, # 已用的空间,单位MB,这个仅方便查看一个项目的使用量
                    "permissions":{ # 权限
                        "read": True, # 读取数据
                        "write": True, # 写入数据
                        "delete": True, # 删除数据
                        "cv": True, # 使用云变量数据服务
                    }
                }
            ]
            f.write(json.dumps(示例, ensure_ascii=False, indent=2))
    if not os.path.exists(f"{配置目录}/timelast_updated.txt"):
        with open(f"{配置目录}/timelast_updated.txt", "w", encoding="utf-8") as f:
            f.write("")
except Exception as e:
    print(f"初始化文件失败!{e}")

日志数据 = []
日志允许占用内存大小MB = 2
class rizhi():
    def info(字符串): # 普通日志处理
        global 日志数据
        if len(str(json.dumps(日志数据,ensure_ascii=False)).encode('utf-8')) / 1024 / 1024 > 日志允许占用内存大小MB:
            日志数据 = []
        时间 = datetime.now().strftime("%Y.%m.%d/%H:%M:%S")
        日志 = f"{时间} -- INFO -- {字符串}"
        print(日志)
        时间_日志文件 = datetime.now().strftime("%Y%m%d")
        with open(f"{日志目录}/{时间_日志文件}日志_all.log", "a", encoding="utf-8") as f:
            f.write(f"{日志}\n")
        with open(f"{日志目录}/{时间_日志文件}日志_info.log", "a", encoding="utf-8") as f:
            f.write(f"{日志}\n")
        日志数据.append(日志)
        return 日志
    def warning(字符串): # 警告处理
        global 日志数据
        if len(str(json.dumps(日志数据,ensure_ascii=False)).encode('utf-8')) / 1024 / 1024 > 日志允许占用内存大小MB:
            日志数据 = []
        时间 = datetime.now().strftime("%Y.%m.%d/%H:%M:%S")
        日志 = f"{时间} -- WARNING -- {字符串}"
        print(日志)
        时间_日志文件 = datetime.now().strftime("%Y%m%d")
        with open(f"{日志目录}/{时间_日志文件}日志_all.log", "a", encoding="utf-8") as f:
            f.write(f"{日志}\n")
        with open(f"{日志目录}/{时间_日志文件}日志_warning.log", "a", encoding="utf-8") as f:
            f.write(f"{日志}\n")
        日志数据.append(日志)
        return 日志

def 检查并填充各UAT可用次数():
    try:
        with open(f"{配置目录}/timelast_updated.txt", "r", encoding="utf-8") as f:
            timelast_updated = f.read()
        if timelast_updated != datetime.now().strftime("%Y.%m.%d"):
            a = time.time()
            with open(f"{配置目录}/UAT.json", "r", encoding="utf-8") as f:
                UAT = json.loads(f.read())
                更新后UAT = []
                for 此刻UAT in UAT:
                    此刻UAT["total_uses"] = 此刻UAT["allowance"]
                    更新后UAT.append(此刻UAT)
            with open(f"{配置目录}/UAT.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(更新后UAT, indent=2, ensure_ascii=False))
            with open(f"{配置目录}/timelast_updated.txt", "w", encoding="utf-8") as f:
                f.write(datetime.now().strftime("%Y.%m.%d"))
            b = time.time()
            耗时 = round(b - a, 10)
            rizhi.info(f"[UAT填充]成功检测到日期变化并重新填充每个UAT账户的可用次数|耗时{耗时}秒")
    except Exception as e:
        rizhi.warning("[UAT填充]----严重错误!!!!未能检测日期变化给每个UAT账户填充可用次数!!!!----")

def 获取目录大小(路径):
    总字节 = 0
    try:
        for entry in os.scandir(路径):
            if entry.is_file():
                总字节 += entry.stat().st_size
            elif entry.is_dir():
                总字节 += 获取目录大小(entry.path)
        return 总字节
    except Exception as e:
        # # 在该环境下提示报错不是一个好方法,这会让我看到错误感到焦虑
        # rizhi.warning(f"[目录占用计算函数]发生了错误但为了保证运行正常忽略|ERROR:'{e}'")
        return 0

性能 = {
    "cpu":0,
    "ram":0,
    "disk":0,
    "disk_fs":0
}
def 实时更新性能数据():
    global 性能
    while True:
        性能_CPU占用 = psutil.cpu_percent(interval=1)
        性能_物理内存占用 = psutil.virtual_memory().percent
        性能_磁盘空间占用 = psutil.disk_usage(f"{父目录}").percent
        性能_磁盘可用空间 = psutil.disk_usage(f"{父目录}").free / 1024 / 1024 / 1024
        性能 = {
            "cpu":性能_CPU占用,
            "ram":性能_物理内存占用,
            "disk":性能_磁盘空间占用,
            "disk_fs":性能_磁盘可用空间
        }
    
def 过渡(目前值, 目标值, 过渡参数, adt):
    结果 = 目前值 + ( (目标值 - 目前值) / 过渡参数) * adt * 60
    return 结果

class Permission_error(Exception):
    pass
class Operation_exception(Exception):
    pass

Client = {
    "all":[],
    "type":{
        "RtCVS":{},
    },
}
RtCVS = {}
文件名黑名单 = ["/","\\",".","~"]
class MyServer(WebSocket):
    def handleConnected(self): # 连接时触发
        rizhi.info(f"[Connected]有新的客户端连接|客户端'{self.address}'")
        try:
            Client["all"].append(self)
        except Exception as e:
            rizhi.warning(f"在连接客户端添加列表时发生错误!{e}")
        self.sendMessage(欢迎语) # 连接的时候给新客户端发送一次数据

    def handleClose(self): # 关闭时触发
        rizhi.info(f"[Close]有客户端关闭连接|客户端'{self.address}'")
        try:
            Client["all"].remove(self)
        except Exception as e:
            rizhi.warning(f"在关闭客户端移除列表时发生错误!{e}")

    def handleMessage(self): # 收到数据时触发
        需要减少可用次数 = True
        日志显示内容限制长度 = 200
        if len(str(self.data)) > 日志显示内容限制长度:
            显示数据 = f"<内容字数大于{日志显示内容限制长度},不显示>"
        else:
            显示数据 = self.data
        rizhi.info(f"收到客户端({self.address})的指令|原始数据{显示数据}")
        接收数据 = self.data
        try:
            try:
                接收数据 = json.loads(接收数据)
                # 第一个方法
                try:
                    # 获取一下UAT数据
                    with open(f"{配置目录}/UAT.json", 'r', encoding='utf-8') as f:
                        UAT = json.loads(f.read())
                    接收数据_用户UAT = 接收数据["UAT"]
                    是否存在用户数据 = False
                    for i,现在UAT in enumerate(UAT):
                        if 现在UAT["token"] == 接收数据_用户UAT:
                            该用户的UAT = 现在UAT
                            用户UAT在列表中位置 = i
                            是否存在用户数据 = True
                            rizhi.info(f"[UAT]客户端({self.address})密钥确认|UAT位于{用户UAT在列表中位置};token'{该用户的UAT["token"]}';该密钥该日还允许'{int(该用户的UAT["total_uses"])-1}'次调用")
                            break
                    if not 是否存在用户数据: # 如果没有找到UAT
                        理由池 = [
                            f"客户端({self.address})的登录凭证不存在|难道没人说过调用功能需要UAT密钥吗|ω•)?",
                            f"客户端({self.address})的登录凭证不存在|如果不知道怎么登录注册UAT这边请(・ω・)ノQQ群:3977451197",
                            f"客户端({self.address})的登录凭证不存在|有点时候我很难对一个人的智商做评价(◕ᴗ◕✿)没说你",
                            f"客户端({self.address})的登录凭证不存在|尼食若至嘛(╯°益°)╯彡┻━┻",
                            f"客户端({self.address})的登录凭证不存在|那还说啥了兄弟¯\\_(ツ)_/¯",
                            f"客户端({self.address})的登录凭证不存在|你写的UAT密钥我遍历整个UAT存档了在哪里呢,哪呢哪呢(°Д°≡°Д°)?",
                            f"客户端({self.address})的登录凭证不存在|你这密钥是现编的吧..._(:3 」∠)_摆了摆了",
                        ]
                        理由 = random.choice(理由池)
                        self.sendMessage(json.dumps({"ERROR":理由}, indent=2, ensure_ascii=False))
                        是否存在用户数据 = False
                        raise ValueError(理由)
                    if not 现在UAT["total_uses"] > 0: # 如果UAT没有可用调用次数
                        理由池 = [
                            f"客户端({self.address})的UAT账户({现在UAT["token"]})|调用次数已尽|或许你需要等到凌晨omo?但对于正常用户你可以直接去肘击下管理的awa",
                            f"客户端({self.address})的UAT账户({现在UAT["token"]})|调用次数已尽|(；人；)`受不了...我写个服务器还需要为了招揽用户搞特别的报错,有这时间我应该去增加些bug的...?...我刚才说的啥o~o?",
                            f"客户端({self.address})的UAT账户({现在UAT["token"]})|调用次数已尽|你是用户还是开发者?如果你是用户就去肘击开发者让他找云服务商扩容下UAT账户的调用次数啊!",
                            f"客户端({self.address})的UAT账户({现在UAT["token"]})|调用次数已尽|写不动了,你知道你调用次数没了就好了",
                        ]
                        理由 = random.choice(理由池)
                        self.sendMessage(json.dumps({"ERROR":理由}, indent=2, ensure_ascii=False))
                        是否存在用户数据 = False
                        raise ValueError(理由)
                    if not 现在UAT["used_storage"] < 现在UAT["storage_limit"]: # 如果UAT的已用空间比允许空间大
                        理由 = f"客户端({self.address})的UAT账户({现在UAT["token"]})|存储空间达到限制,这还真没辙,你去找管理把你的数据文件删光光吧(╯°Д°)╯︵ /(.□ . )━☆ﾟ.*･｡ﾟ"
                        self.sendMessage(json.dumps({"ERROR":理由}, indent=2, ensure_ascii=False))
                        是否存在用户数据 = False
                        raise ValueError(理由)
                except Exception as e:
                    rizhi.warning(f"在处理客户端({self.address})身份时出现错误|{e}")

                if 是否存在用户数据:
                    接收数据_key = list(接收数据.keys())[0]
                    接收数据_value = 接收数据[接收数据_key]
                    # ---------声明客户端数据访问操作类型---------
                    if 接收数据_key == "type":
                        if 接收数据_value == "RtCVS":
                            if not 该用户的UAT["permissions"]["cv"]:
                                raise Permission_error(f"客户端({self.address}|{该用户的UAT["token"]})的操作在UAT信息中没有操作权限('cv')")
                            if 该用户的UAT["token"] not in Client["type"]["RtCVS"]:
                                Client["type"]["RtCVS"][该用户的UAT["token"]] = []
                            Client["type"]["RtCVS"][该用户的UAT["token"]].append(self)
                            rizhi.info(f"[TYPE]客户端'{self.address}'声明自己为'RtCVS'类型")
                    # ---------云存储部分_数据基础操作---------
                    if 接收数据_key in ["dump","write","w"]:  # 存储文件
                        if not 该用户的UAT["permissions"]["write"]:
                            raise Permission_error(f"客户端({self.address}|{该用户的UAT["token"]})的操作在UAT信息中没有操作权限('write')")
                        dump_文件名 = 接收数据_value[0]
                        for 字符 in dump_文件名: # 简单有效的防范路径漏洞
                            if 字符 in 文件名黑名单:
                                raise ValueError(f"客户端或许试图进行路径遍历(路径回退上一级漏洞)攻击(字符'{字符}'属于违规字符)")
                        dump_数据 = 接收数据_value[1]
                        if len(str(dump_数据).encode('utf-8')) < 该用户的UAT["storage_limit"]*1024*1024 - 该用户的UAT["used_storage"]*1024*1024:
                            os.makedirs(f"{数据目录}/{该用户的UAT["token"]}", exist_ok=True)
                            with open(f"{数据目录}/{该用户的UAT["token"]}/{dump_文件名}.txt", "w", encoding="utf-8") as f:
                                f.write(str(dump_数据))
                            if len(str(dump_数据)) > 日志显示内容限制长度:
                                显示数据 = f"<内容字数大于{日志显示内容限制长度},不显示>"
                            else:
                                显示数据 = dump_数据
                            rizhi.info(f"[DUMP]客户端({self.address}|{该用户的UAT["token"]})进行了创建or修改数据|数据名'{dump_文件名}';内容'{显示数据}'")
                        else:
                            理由池 = [
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:要保存的数据太大了啦啊喂!我吃不下啦!>n< 来人呀!(去联系管理员)",
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:这东西...我吃不消啊ono(去联系管理员)",
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:我吃撑了>M<AAAAAAAA!!!!!!(去联系管理员)",
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:(扔了一大坨饭饭到地上)CI!!!(炸毛)(去联系管理员)",
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:都吃撑了还让我吃啥啊!!!非礼啊!!!(去联系管理员)",
                                f"客户端({self.address})的UAT账户({现在UAT["token"]})|{该用户的UAT["token"]}目录宝:(ﾉ◕ヮ◕)ﾉ*不要再点我的啦坏坏~~~(?难道你是说你运气这么好第一次报错就遇到我?那恭喜了不止这一个)",
                            ]
                            理由 = random.choice(理由池)
                            self.sendMessage(json.dumps({"ERROR":理由}, indent=2, ensure_ascii=False))
                            rizhi.warning(f"[DUMP_ERROR]{理由}")
                    if 接收数据_key in ["load","read","r"]:  # 读取文件
                        if not 该用户的UAT["permissions"]["read"]:
                            raise Permission_error(f"客户端({self.address}|{该用户的UAT["token"]})的操作在UAT信息中没有操作权限('read')")
                        for 字符 in 接收数据_value: # 简单有效的防范路径漏洞
                            if 字符 in 文件名黑名单:
                                raise ValueError(f"客户端或许试图进行路径遍历(路径回退上一级漏洞)攻击(字符'{字符}'属于违规字符)")
                        with open(f"{数据目录}/{该用户的UAT["token"]}/{接收数据_value}.txt", "r", encoding="utf-8") as f:
                            读取数据 = f.read()
                        self.sendMessage(读取数据)
                        if len(str(读取数据)) > 日志显示内容限制长度:
                            显示数据 = f"<内容字数大于{日志显示内容限制长度},不显示>"
                        else:
                            显示数据 = 读取数据
                        rizhi.info(f"[LOAD]客户端({self.address}|{该用户的UAT["token"]})进行了查阅数据|数据名'{接收数据_value}';内容'{显示数据}'")
                    if 接收数据_key in ["remove","delete","del"]: # 删除文件
                        if not 该用户的UAT["permissions"]["delete"]:
                            raise Permission_error(f"客户端({self.address}|{该用户的UAT["token"]})的操作在UAT信息中没有操作权限('delete')")
                        os.remove(f"{数据目录}/{该用户的UAT["token"]}/{接收数据_value}.txt")
                        rizhi.info(f"[REMOVE]客户端({self.address}|{该用户的UAT["token"]})进行了删除数据|数据名'{接收数据_value}'")
                    # ---------实时同步云变量部分(RtCVS/CV)_数据操作---------
                    if 接收数据_key in ["CV_dump","CV_write","CV_w"]:
                        if not 该用户的UAT["permissions"]["cv"]:
                            raise Permission_error(f"客户端({self.address}|{该用户的UAT["token"]})的操作在UAT信息中没有操作权限('cv')")
                        需要减少可用次数 = False
                        if 该用户的UAT["token"] not in RtCVS:
                            RtCVS[该用户的UAT["token"]] = {}
                        rizhi.info(f"[CV_dump]客户端({self.address}|{该用户的UAT["token"]})上传了CV数据|变量'{接收数据_value[0]}'数据'{接收数据_value[1]}'")
                        if len(str(json.dumps(RtCVS[该用户的UAT["token"]], ensure_ascii=False)).encode('utf-8')) + len(str(接收数据_value[1]).encode('utf-8')) < 该用户的UAT["RtCVS_limit"]*1024*1024: # 检查是否符合大小
                            RtCVS[该用户的UAT["token"]][接收数据_value[0]] = 接收数据_value[1]
                            rizhi.info(f"[CV_dump]客户端({self.address}|{该用户的UAT["token"]})成功存储or修改数据|变量'{接收数据_value[0]}'数据'{接收数据_value[1]}'")
                            # 为所有同token的type类型为"RtCVS"的客户端播报
                            i = 0
                            for 目标 in Client["type"]["RtCVS"][该用户的UAT["token"]]:
                                i += 1
                                目标.sendMessage(json.dumps(RtCVS[该用户的UAT["token"]], ensure_ascii=False))
                            rizhi.info(f"[CV]为{i}个客户端广播了数据{json.dumps(RtCVS[该用户的UAT["token"]], ensure_ascii=False)}")
                        else:
                            rizhi.warning(f"[CV_dump]客户端({self.address}|{该用户的UAT["token"]})因整体数据大于'{该用户的UAT["RtCVS_limit"]}'导致数据被忽略|变量'{接收数据_value[0]}'数据'{接收数据_value[1]}'")
                    # ---------客户端查阅信息---------
                    if 接收数据_key == "i_server":  # 查看服务器性能占用
                        需要减少可用次数 = False
                        信息 = json.dumps(性能, ensure_ascii=False, indent=2)
                        self.sendMessage(信息)
                        rizhi.info(f"[i_server]客户端({self.address}|{该用户的UAT["token"]})进行了查看'server'状态信息\n'{信息}'")
                    if 接收数据_key == "i_me":  # 查看自己账号的一些信息
                        需要减少可用次数 = False
                        信息 = {
                            "每日配额(次数)":该用户的UAT["allowance"],
                            "今日剩余调用次数":该用户的UAT["total_uses"],
                            "累计已调用次数":该用户的UAT["total_calls"],
                            "数据量统计(MB)":该用户的UAT["used_storage"],
                            "数据量限额(MB)":该用户的UAT["storage_limit"],
                            "您还可用(MB)":round(该用户的UAT["storage_limit"] - 该用户的UAT["used_storage"], 3),
                            "留言":"数据限额之设，仅为防宵小蓄意塞盘。若君正经使用遇碍，但言无妨，立调配额、解限额，切莫忧心。凡正途所用，必畅行无阻！Ciallo～(∠・ω< )⌒☆"
                        }
                        信息 = json.dumps(信息, ensure_ascii=False, indent=2)
                        self.sendMessage(信息)
                        rizhi.info(f"[i_me]客户端({self.address}|{该用户的UAT["token"]})进行了查看'UAT账户'状态信息\n'{信息}'")
                    if 接收数据_key == "i_tos":  # 查看免责声明
                        self.sendMessage(欢迎语)
                        rizhi.info(f"[i_tos]客户端({self.address}|{该用户的UAT["token"]})进行了查看tos信息")
            except Exception as e:
                self.sendMessage(rizhi.warning(f"客户端({self.address})可能发送了无用或错误的信息导致处理失败|原始数据{self.data}|错误:{e}"))
                return # 直接返回终止在这里,不进行收尾工作,删掉这一行代表不管出现什么错误都会进行收尾工作,这可能产生不必要的报错日志
            #-----收尾工作,为该用户UAT信息做调整-----
            if 需要减少可用次数:
                该用户的UAT["total_uses"] -= 1
            该用户的UAT["total_calls"] += 1
            该用户的UAT["used_storage"] = round(获取目录大小(f'{数据目录}/{该用户的UAT["token"]}') / 1024 / 1024, 3)
            with open(f"{配置目录}/UAT.json", 'r', encoding='utf-8') as f:
                UAT = json.loads(f.read())
            UAT[用户UAT在列表中位置] = 该用户的UAT
            with open(f"{配置目录}/UAT.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(UAT, indent=2, ensure_ascii=False))
        except Exception as e:
            rizhi.warning(f"客户端({self.address})可能发送了无用或错误的信息导致处理失败,但是触发了最底层的except,这或许意味着有奇怪的错误导致了本身逻辑问题|原始数据{self.data}|错误:{e}")

def 进程_检查并填充各UAT可用次数():
    while True:
        检查并填充各UAT可用次数()
        time.sleep(5)
try:
    Thread(target=进程_检查并填充各UAT可用次数, daemon=True).start()
    rizhi.info("[--STAT--]_检查并填充各UAT可用次数函数")
except Exception as e:
    rizhi.warning(f"---检查并填充各UAT可用次数函数启动失败!{e}---")

server = SimpleWebSocketServer('', 55550, MyServer)
try:
    Thread(target=server.serveforever, daemon=True).start()
    rizhi.info(f"[--STAT--]_WS服务器函数({服务器版本})")
except Exception as e:
    rizhi.warning(f"---WS服务器启动失败!{e}---")

try:
    Thread(target=实时更新性能数据, daemon=True).start()
    rizhi.info(f"[--STAT--]_性能数据更新函数")
except Exception as e:
    rizhi.warning(f"---性能数据更新函数启动失败!{e}---")

if not GUI:
    while True:
        # 用来安心的东西awa,自己触发GC本质没啥用
        前_物理内存 = psutil.virtual_memory().percent
        gc.collect()
        time.sleep(5)
        后_物理内存 = psutil.virtual_memory().percent
        rizhi.info(f"[GC]触发GC完成|之前内存占用{前_物理内存}%;现内存占用{后_物理内存}%")
        time.sleep(900)
if GUI:
    # 下面的所有哦部分都是GUI部分,如果不想使用可以直接把该文档最开头的'GUI'写为'False'
    import pyglet
    window = pyglet.window.Window(1020, 720, "XingHui_WS信息面板", resizable=True)
    window.set_minimum_size(1020, 160) # 设置窗口最小宽高
    window.set_maximum_size(1020, 1080) # 设置窗口最大宽高
    batch = pyglet.graphics.Batch()
    # 创建日志布局
    日志文档 = pyglet.text.document.UnformattedDocument("")
    日志文档.set_style(0, 0, {'font_size': 9})
    日志布局 = pyglet.text.layout.ScrollableTextLayout(
        日志文档,
        width=window.width//2 - 6,  # 留点边距
        height=window.height - 6,
        x=3,
        y=3,
        batch=batch,
        multiline=True
    )
    日志布局.color = (0, 0, 0, 255)  # 黑色文字

    def 更新日志显示():
        最新日志 = 日志数据[-50:][::-1]  # 反转显示
        显示文本 = "\n".join([日志[:140] for 日志 in 最新日志])
        日志文档.text = 显示文本

    @window.event
    def on_draw():
        global 性能
        window.clear()
        更新日志显示()
        pyglet.shapes.Rectangle( # 背景_日志区域
            x=0,
            y=0,
            width=window.width//2,
            height=window.height,
            color=(255, 255, 255)
            ).draw()
        
        pyglet.shapes.Rectangle( # 背景_客户端区域
            x=window.width//2,
            y=0,
            width=window.width//2,
            height=window.height,
            color=(24, 65, 255)
            ).draw()
        pyglet.text.Label( # 显示客户端的标签
            f"客户端'ALL'({len(Client["all"])})",
            x=window.width//2,
            y=window.height - 15,
            color=(255, 255, 255)
            ).draw()
        i = 0
        for 客户端 in Client["all"]:
            pyglet.text.Label( # 显示客户端
                f"{客户端.address}",
                x=window.width//2,
                y=85 + 20 * i,
                color=(255, 255, 255)
                ).draw()
            i += 1
        # --------------------------------------------------
        pyglet.shapes.Rectangle( # 背景_性能区域
            x=window.width//2,
            y=0,
            width=window.width//2,
            height=80,
            color=(0, 0, 0)
            ).draw()
        # 内存占用显示
        pyglet.shapes.Rectangle( # 背景
            x=window.width//2 + 5,
            y=5,
            width=5 * 100,
            height=20,
            color=(255, 255, 255)
            ).draw()
        pyglet.shapes.Rectangle( # 条
            x=window.width//2 + 6,
            y=6,
            width=max(0, 5 * 过渡性能["ram"] - 2),
            height=20 - 2,
            color=(148, 119, 5)
            ).draw()
        pyglet.text.Label( # 文字
            f"内存:{性能['ram']}%",
            x=1 + window.width//2 + 5,
            y=1 + 5,
            color=(255, 255, 255)
            ).draw()

        # 存储占用显示
        pyglet.shapes.Rectangle( # 背景
            x=window.width//2 + 5,
            y=5 + 25,
            width=5 * 100,
            height=20,
            color=(255, 255, 255)
            ).draw()
        pyglet.shapes.Rectangle( # 条
            x=window.width//2 + 6,
            y=6 + 25,
            width=max(0, 5 * 过渡性能["disk"] - 2),
            height=20 - 2,
            color=(16, 40, 138)
            ).draw()
        pyglet.text.Label( # 文字
            f'存储:{性能["disk"]}%',
            x=1 + window.width//2 + 5,
            y=1 + 5 + 25,
            color=(255, 255, 255)
            ).draw()

        # CPU占用显示
        pyglet.shapes.Rectangle( # 背景
            x=window.width//2 + 5,
            y=5 + 50,
            width=5 * 100,
            height=20,
            color=(255, 255, 255)
            ).draw()
        pyglet.shapes.Rectangle( # 条
            x=window.width//2 + 6,
            y=6 + 50,
            width=max(0, 5 * 过渡性能["cpu"] - 2),
            height=20 - 2,
            color=(208, 32, 144)
            ).draw()
        pyglet.text.Label( # 文字
            f"CPU:{性能["cpu"]}%",
            x=1 + window.width//2 + 5,
            y=1 + 5 + 50,
            color=(255, 255, 255)
            ).draw()

        pyglet.text.Label( # 文字
            f"运行时间:{round((time.time()-运行开始时间)/60/60, 3)}小时",
            x=1 + window.width//2 + 5,
            y=1 + 5 + 50 + 25,
            color=(255, 255, 255)
            ).draw()

        batch.draw()
        pyglet.clock.tick()
    
    过渡性能 = {
        "cpu":0,
        "ram":0,
        "disk":0,
        "disk_fs":0
    }
    def 过渡性能数据(dt):
        global 性能,过渡性能数据
        for key in 性能:
            过渡性能[key] = 过渡(过渡性能[key], 性能[key], 15, dt)
    pyglet.clock.schedule_interval(过渡性能数据, 1/60.0)
    pyglet.app.run()

# QSBjaGlsZCB3aG8gZGlkbuKAmXQgZml0IGluIG9uY2UgdHJpZWQgdG8gcHJvdmUgdGhlaXIgd29ydGgsIGJ1dCBwZXJoYXBzIGl0IHdhcyBhbGwgaW4gdmFpbjooLi4=
