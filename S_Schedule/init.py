'''init.py:

'''
import sqlite3
import datetime
import os
import subprocess as sb
import json

CONSOLE = 0

def get_sql():
    '''获取数据库相关变量元组:
    - <Connection> 主数据库连接
    - <Cursor> 数据库操作光标
    '''
    table = sqlite3.connect("./res/data/maintable.db", check_same_thread=False)
    cur = table.cursor()

    return (table, cur)

def get_path():
    '''以较安全的方式获取当前绝对路径
    '''
    path = os.path.abspath(__file__)
    filePath = os.path.dirname(path)

    return filePath

def get_date():
    '''获取日期相关变量元组:
    - <datetime.date> 当前日期及星期
    - <list> 中文星期
    - <dic> 用于转换中文星期与iso数字的字典
    '''
    DATE_NOW = datetime.date.today()
    ##DATE_NOW = datetime.date(2023,3,6)
    WKDAY_NOW = DATE_NOW.weekday()

    weekcn = ['一', '二', '三', '四', '五', '六', '日']
    weeken = {'周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5, '周六': 6, '周日': 7}

    return (DATE_NOW, WKDAY_NOW, weekcn, weeken)


def get_json():
    global CONSOLE
    '''获取运行参数相关变量列表:
    - <bool> TASK_PROTECT: 进程保护
    - <int> REFRESH_RATE: 刷新周期
    - <bool> STARTUP: 开机自启状态
    - <bool> SHJ: 红杰模式启动状态
    - <int> SATURDAY_REFERENCE: 周六校准参数
    - <int> WEDNESDAY_REFERENCE: 周三校准参数
    - <bool> HOMO: 杜比顶级音效
    - <int> CHOSEN_COUNTDOWN: 选中倒数日序号
    - <int> SEPARATOR: 中午位于第几节
    '''
    filePath = get_path()
    with open(filePath+"/res/data/param.json",'r+',encoding='utf-8') as jsFile:
        param = json.load(jsFile)
        TASK_PROTECT = param["TASK_PROTECT"]
        REFRESH_RATE = param["REFRESH_RATE"]
        STARTUP = param["STARTUP"]
        SHJ = param["SHJ"]
        SATURDAY_REFERENCE = param["SATURDAY_REFERENCE"]
        WEDNESDAY_REFERENCE = param["WEDNESDAY_REFERENCE"]
        HOMO = param["HOMO"]
        CHOSEN_COUNTDOWN = param["CHOSEN_COUNTDOWN"]
        SEPARATOR = param["SEPARATOR"]
        TOMORROW = param["TOMORROW"]
        CONSOLE = param["CONSOLE"]
        IGNORE_PID = param["IGNORE_PID"]
    paramList = (param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR, TOMORROW, CONSOLE, IGNORE_PID)
    
    return paramList


def std_out(text:str, level=1, setting=0):
    print(text)


def check_pid():
    with open("./res/data/pid.txm",'r',encoding="utf-8") as pidfile:
        LAST_PID = pidfile.readline()
        RESULT = sb.getoutput(f'tasklist /fi "PID eq {LAST_PID}"')
        
        if RESULT == '信息: 没有运行的任务匹配指定标准。':
            CHECKED = False 
            std_out("[ 检查 ] 没有运行的任务匹配指定标准。", 2)
        elif "pythonw.exe" in RESULT or "python.exe" in RESULT:
            CHECKED = True
            std_out("[ 检查 ] 检测到正在运行的任务！", 2)
        else:
            CHECKED = False
            std_out("[ 检查 ] 没有运行的任务匹配指定标准。", 2)
    return CHECKED


def write_pid():
    with open("./res/data/pid.txm",'w+',encoding="utf-8") as pidfile:
        SELF = os.getpid()
        pidfile.write(str(SELF))
    


if __name__ == '__main__':
    print(get_date())
