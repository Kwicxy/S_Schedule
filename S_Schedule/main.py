from functools import cache
import datetime
import time
import sys
import os
import json
from random import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction,  QMessageBox, QSystemTrayIcon, QGraphicsDropShadowEffect, QGraphicsBlurEffect
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import uic

import init
from methods import *
from subwin import *
import dlc

table, cur = init.get_sql()
filePath = init.get_path()
param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR, TOMORROW, CONSOLE, IGNORE_PID = init.get_json()
DATE_NOW, WKDAY_NOW, weekcn, weeken = init.get_date()

cdName, cdDate = getCd()


flag = True
deadline = False

# 刷新用后台线程
class BackendThread(QObject):
    # 通过类成员对象定义信号
    update = pyqtSignal()
    formula = pyqtSignal()
    cnt = 0
    def go(self):
        global deadline, REFRESH_RATE
        while not deadline:
            # 每隔(REFRESH_RATE)秒发送一次刷新信号
            self.update.emit()
            self.cnt += 1
            if self.cnt >= 10:
                self.formula.emit()
                self.cnt = 0
            time.sleep(REFRESH_RATE)
 
# 系统托盘菜单
class TrayIcon(QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.ui = MainWindow
        self.ICON_TRAY = QIcon(filePath+"/res/icons/schale.png")
        self.ICON_EXTRA = QIcon(filePath+"/res/icons/EXTRA_w.png")
        self.ICON_SPECIAL = QIcon(filePath+"/res/icons/mika_ureshii.png")
        self.ICON_NORMAL = [QIcon(filePath+"/res/icons/mika_talking.png"), QIcon(filePath+"/res/icons/mika_idle.png"), QIcon(filePath+"/res/icons/mika_serious.png")]
        
        self.createMenu()
        self.count = 0
    
    def createMenu(self):
        self.setToolTip("Schale Schedule v4")
        self.menu = QMenu()
        self.action_about = QAction("关于", self, triggered=self.ui.handleAbout)

        self.action_edit = QAction("编辑会话", self, triggered=self.ui.markUpSafe)
        self.action_hidden = QAction("参数设置",self,triggered=self.hiddenWindow)
        self.action_generate = QAction("下一页公式",self,triggered=self.ui.show_formula)
        self.action_time = QAction("全屏时钟",self,triggered=self.time)
        self.action_time.setCheckable(True)
        self.action_blur = QAction("隐藏公式",self,triggered=self.blur)
        self.action_blur.setCheckable(True)
        self.action_restart = QAction("重新启动", self, triggered=self.restart)
        self.action_quit = QAction("退出程序", self, triggered=self.quit)

        self.menu.addSection("界面操作")
        self.menu.addAction(self.action_time)
        self.menu.addAction(self.action_blur)
        self.menu.addAction(self.action_generate)
        self.menu.addSection("系统操作")
        self.menu.addAction(self.action_about)
        self.menu.addAction(self.action_edit)
        self.menu.addAction(self.action_hidden)
        self.menu.addAction(self.action_restart)
        self.menu.addAction(self.action_quit)
        self.setContextMenu(self.menu)

        # 设置图标
        self.setIcon(self.ICON_TRAY)
        self.icon = self.MessageIcon()

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

        self.getHintText()
        self.chance = 0.1
        init.std_out("[ 托盘 ] 初始化已完成。")
    
    def hiddenWindow(self):
        self.dev = DevWin()
        self.dev.ui.protectBox.setChecked(TASK_PROTECT)
        self.dev.ui.startupBox.setChecked(STARTUP)
        self.dev.ui.hongjie.setChecked(SHJ)
        self.dev.show()

    def time(self):
        if self.action_time.isChecked():
            self.ui.time_open()
        else:
            self.ui.time_hide()

    def blur(self):
        if self.action_blur.isChecked():
            self.ui.richtext_blur(True)
        else:
            self.ui.richtext_blur(False)
            
    def restart(self):
        self.setVisible(False)
        os.startfile(".\\restart.py")
        # self.quit()

    # 退出
    def quit(self):
        is_quit=self.ui.handleExit()        # 该变量保存主界面是否退出
        if is_quit!=0:
            self.setVisible(False)          # 删除托盘图标
        
    def start_hint(self):
        START_TIME = datetime.datetime.now()
        TARGET_TIME = START_TIME + datetime.timedelta(minutes=1)
        TARGET_TIME = TARGET_TIME.replace(second=0)
        DELTA = TARGET_TIME.__sub__(START_TIME).seconds
        self.showMessage("Schale - Message",f"线程将在{DELTA}s后启动.",self.ICON_EXTRA,3000)

    def getHintText(self):
        with open("./res/userfiles/special_lobby.txt",'r',encoding='utf-8') as f:
            self.SPECIAL_TEXT = f.readlines()
            for i in range(len(self.SPECIAL_TEXT)):
                if '\\n' in self.SPECIAL_TEXT[i]:
                    self.SPECIAL_TEXT[i] = self.SPECIAL_TEXT[i].replace('\\n','\n')
        with open("./res/userfiles/normal_lobby.txt",'r',encoding='utf-8') as f:
            self.NORMAL_TEXT = f.readlines()
            for i in range(len(self.NORMAL_TEXT)):
                if '\\n' in self.NORMAL_TEXT[i]:
                    self.NORMAL_TEXT[i] = self.NORMAL_TEXT[i].replace('\\n','\n')

    # 接受图标传入事件 1是单击右键，2是双击，3是单击左键，4是中键点击
    def onIconClicked(self, reason):
        if reason == 3:
            self.count+=1
            init.std_out(f"[ 托盘 ] 被谁戳了！第{self.count}次了！",2)
            if uniform(0,1) <= self.chance:
                text = choice(self.SPECIAL_TEXT)
                self.showMessage("Schale - Lobby Message",text,self.ICON_SPECIAL,3000)
            else:
                text = choice(self.NORMAL_TEXT)
                self.showMessage("Schale - Lobby Message",text,choice(self.ICON_NORMAL),3000)

# 主界面
class MainWin(QMainWindow):
    # 初始化
    def __init__(self):
        super().__init__()
        # 进程检查
        if init.check_pid() and not IGNORE_PID:
            QMessageBox.warning(self,"错误","有一个正在运行的进程！")
            sys.exit()
        else:
            init.write_pid()

        # 变量初始化
        self.flag = flag
        self.theme = "./ui/main_ba.ui"
        # 各实例初始化
        self.ui = uic.loadUi(self.theme, self)
        self.tmw = TimeWin()

        self.apply_style()
        
        judgeTime(str(WKDAY_NOW))

        # 获取日期并显示
        self.ui.dateNow.setText(DATE_NOW.strftime("%m - %d"))
        self.ui.wkdayNow.setText('星期'+str(weekcn[WKDAY_NOW]))
        self.SHOW_TOMORROW = False
        
        self.show_countdown()
        self.init_formula()
        self.show_classtable(DATE_NOW, WKDAY_NOW)
        self.show_duty(WKDAY_NOW+1)

        self.handle_refresh()
        self.hide()
        init.std_out("[ 运行 ] 主窗口初始化完成！")
         
    # 等待正分钟启动线程
    def pend(self):
        START_TIME = datetime.datetime.now()
        TARGET_TIME = START_TIME + datetime.timedelta(minutes=1)
        TARGET_TIME = TARGET_TIME.replace(second=0)
        DELTA = TARGET_TIME.__sub__(START_TIME).seconds
        print(f"[ 后台 ] 线程将在{DELTA}s后启动.")
        #sleep(DELTA)
        self.set_backend()
        self.show()

    # 管理后台线程
    def set_backend(self):
        # 创建线程
        self.backend = BackendThread()
        # 连接信号
        self.backend.update.connect(self.handle_refresh)
        self.backend.formula.connect(self.show_formula)
        self.thread = QThread()
        self.backend.moveToThread(self.thread)  
        # 开始线程
        self.thread.started.connect(self.backend.go)
        self.thread.start()
        init.std_out("[ 运行 ] 后台线程已启动！")

    # 应用样式
    def apply_style(self):
        # 默认阴影
        self.effect_shadow = QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(1,1) # 偏移
        self.effect_shadow.setBlurRadius(8) # 阴影半径
        self.effect_shadow.setColor(QColor("#666666")) # 阴影颜色
        self.ui.LeftPanelFrame.setGraphicsEffect(self.effect_shadow)

        # 红字阴影
        self.effect_shadow_red = QGraphicsDropShadowEffect(self)
        self.effect_shadow_red.setOffset(1,1) # 偏移
        self.effect_shadow_red.setBlurRadius(8) # 阴影半径
        self.effect_shadow_red.setColor(QColor("#7f0800")) # 阴影颜色
        self.ui.RedFrame.setGraphicsEffect(self.effect_shadow_red)

        self.effect_blur = QGraphicsBlurEffect()
        self.effect_blur.setBlurRadius(19.19+8.10)

        # 窗口置于底层|无框|透明背景
        self.setWindowFlags(Qt.WindowStaysOnBottomHint|Qt.Tool|Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        init.std_out("[ 运行 ] 主界面样式应用完成！")
        self.show()
    
    def richtext_blur(self,status):
        if status:
            self.ui.formula.setGraphicsEffect(self.effect_blur)
        else:
            self.ui.formula.setGraphicsEffect(None)




    # 初始化富文本框
    def init_formula(self):
        with open(filePath+"/res/userfiles/formula.html",'r+',encoding='utf-8') as f:
            [head, body, tail] = f.read().split("<!--split.structure-->")
            bodies = body.split("<!--split.content-->")
            self.html = [head+bodies[i]+tail for i in range(len(bodies))]
            self.html_len = len(self.html)
            self.cnt = 0
        init.std_out("[ 运行 ] 富文本初始化完成。")
        self.show_formula()

    # 全屏时钟
    def time_open(self):
        self.tmw.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.Tool|Qt.FramelessWindowHint)
        self.tmw.setAttribute(Qt.WA_TranslucentBackground)
        self.tmw.show()

    def time_hide(self):
        self.tmw.setWindowFlags(Qt.WindowStaysOnBottomHint|Qt.Tool|Qt.FramelessWindowHint)
        self.tmw.hide()
      
    # 显示倒数日
    def show_countdown(self):
        cdName, cdDate = getCd()
        self.ui.cdTitle.setText("距离"+cdName[CHOSEN_COUNTDOWN]+"开始")
        self.ui.cdDigit.setText(str(dateDelta(cdDate[CHOSEN_COUNTDOWN],DATE_NOW)))
        DelDate = str(dateDelta(cdDate[CHOSEN_COUNTDOWN],DATE_NOW))
        LenDate = len(DelDate)
        self.ui._remains.setText("还有"+' '*10*LenDate+"天")
        self.ui.cdConsumption.setText("IN "+DelDate+" DAY(S)")

    # 显示课表
    def show_classtable(self, day, wkday):
        # 获取当日课表
        spDate, spDtStr = initSpDate()
        if day in spDate:
            init.std_out(f"[ 运行 ] 存在指定日期的特殊课表.")
            cur.execute("SELECT * FROM '特殊' WHERE Date=:dt",{"dt":day.isoformat()})
            raw=cur.fetchall()[0]
            o=raw[0:10]
            special_time=raw[10]
            if special_time!='':
                judgeTime(special_time)
        else:
            if not wkday in [5, 6]:
                init.std_out(f"[ 运行 ] 正常课表[{wkday+1}].")
                cur.execute(f"SELECT * FROM '正常' WHERE _rowid_={wkday+1}")
            elif wkday == 5:
                third = judgeThird(day)
                init.std_out(f"[ 运行 ] 特殊课表：周六[{third}].") 
                cur.execute(f"SELECT * FROM '周六' WHERE _rowid_={third}")
            else:
                cur.execute("SELECT * FROM '周六' WHERE _rowid_=4")
            o = cur.fetchall()[0]
            print(o)
        # 显示当日课表   
        self.allClass=[] 
        for i in range(len(o)):
            if i != 0:
                if i == SEPARATOR:
                    self.allClass.append('----')
                    self.allClass.append('')
                self.allClass.append(o[i])
                if i != 9:
                    self.allClass.append('')
        self.ui.classTable.setText('\n'.join(self.allClass))

    # 获取值日表并显示
    def show_duty(self, Obj):
        cur.execute(f"SELECT * FROM '值日' WHERE _rowid_={Obj}")
        duty = cur.fetchall()
        
        dutyLeader = duty[0][0]
        dutySweepA = duty[0][1]
        dutySweepB = duty[0][2]
        dutySweepC = duty[0][3]
        dutyMop = duty[0][4]
        dutyBoard = duty[0][5]

        self.ui.dutyLeader.setText(dutyLeader)
        self.ui.dutySweepA.setText(dutySweepA)
        self.ui.dutySweepB.setText(dutySweepB)
        self.ui.dutySweepC.setText(dutySweepC)
        self.ui.dutyMop.setText(dutyMop)
        self.ui.dutyBoard.setText(dutyBoard)
        
        init.std_out("[ 运行 ] 值日表已更新。")

    # 更新富文本框
    def show_formula(self):
        self.ui.formula.setHtml(self.html[self.cnt])
        self.cnt = (self.cnt+1)%(self.html_len)
        init.std_out("[ 运行 ] 富文本已更新。")

    # 接管需要刷新的工作
    def handle_refresh(self):
        # 时间面板
        timen = datetime.datetime.now().time()
        #timen = datetime.time(18,3)
        self.tmw.timeNow.setText(timen.strftime("%H:%M"))
        self.ui.timeNow.setText(timen.strftime("%H:%M"))
        temp, posNow = timeComp(timen)

        # 倒数面板
        if posNow == 25:
            self.ui.timeTitle.setText("离今天结束")
            self.ui.timeDescription.setText("The day ends")
        elif posNow == 24:
            self.ui.timeTitle.setText("离今天放学")
            self.ui.timeDescription.setText("The school ends")
        elif posNow %2 == 0:
            self.ui.timeTitle.setText("离本节下课")
            self.ui.timeDescription.setText("The class ends")
        elif posNow %2 == 1:
            self.ui.timeTitle.setText("离下节上课")
            self.ui.timeDescription.setText("The next class starts")
        
        delta = timeCalc(timen,temp)
        self.ui.timeRemain.setText(delta)
        self.ui._remains_3.setText("还有"+' '*10*len(delta)+"分钟")
        self.ui.timeConsumption.setText("in "+delta+ " minute(s)")
        
        # 课表面板
        self.ui.classIndicator.clear()
        init.std_out("[ 后台 ] 当前位置: "+str(posNow), 0, CONSOLE)
        self.classIndList=[]
        if 0 <= posNow <= 18:
            self.classIndList=[" " for i in range(posNow)]
            self.classIndList.append("→")
            self.ui.classIndicator.setText('\n'.join(self.classIndList))
        elif posNow == -1:
            self.ui.classIndicator.setText("\n\n\n\n还\n没\n开\n始")
        elif posNow >= 19:
            if TOMORROW:
                self.ui.classIndicator.setText("\n\n\n\n明\n天\n课\n表")
                if not self.SHOW_TOMORROW:
                    DATE_TOMORROW = DATE_NOW+datetime.timedelta(days=1)
                    WKDAY_TOMORROW = (WKDAY_NOW +1)%7
                    self.show_classtable(DATE_TOMORROW, WKDAY_TOMORROW)
                    self.SHOW_TOMORROW = True
            else:
                self.ui.classIndicator.setText("\n\n\n\n已\n经\n结\n束")
        

        #####
        # dlc.showZR()  # 抛出一个或者一个一个zr
        ##### 

    # 退出程序
    def handleExit(self):
        choice = QMessageBox.question(
            self.ui,
            "退出",
            "你想结果这个进程吗（恼")
        if choice == QMessageBox.Yes:
            init.std_out("[ 注意 ] 主程序接收到退出信号。",2)
            self.flag = False
            self.thread.quit()
            QApplication.instance().quit()
        else:
            return 0

    # 显示“关于”信息
    def handleAbout(self):
        f = open(filePath+"./res/userfiles/readme.txt", 'r', encoding='utf-8')
        aboutText = f.read()
        f.close()
        QMessageBox.about(
            self.ui,
            "OvO",
            aboutText)

    # 防止意外退出
    def markUpSafe(self):
        try:
            self.handle_edit()
        except BaseException:
            pass

    # 编辑对话框
    def handle_edit(self):
        # 实例化一个对话框类
        init.std_out("[ 运行 ] 正在启动对话框…")
        self.dlg = EditWin(self)
        # 显示对话框，代码阻塞在这里，
        # 等待对话框关闭后，才能继续往后执行
        self.mdlg.show()

    # 应用编辑对话框的参数
    def updateEdit(self,changed_table, changed_time, changed_duty, changed_cd):
        if changed_table != '':
            spDate, spDtStr = initSpDate()
            self.ui.classTable.clear()
            if DATE_NOW in spDate:
                cur.execute("SELECT * FROM '特殊' WHERE Date=:dt",{"dt":DATE_NOW.isoformat()})
                raw = cur.fetchall()[0]
                o = raw[0:10]
                changed_time = raw[10]
            else:
                if changed_table in ['周六1', '周六2']:
                    cur.execute(
                        f"SELECT * FROM '周六' WHERE _rowid_={int(changed_table[-1])}")
                elif changed_table == '(新建课表)':
                    cur.execute("SELECT * FROM '正常' WHERE _rowid_=?",str(WKDAY_NOW+1))
                elif WKDAY_NOW == 2:
                    parity = judgeParity(DATE_NOW)
                    cur.execute(f"SELECT * FROM '周三' WHERE _rowid_={parity}")
                else:
                    cur.execute(
                        f"SELECT * FROM '正常' WHERE _rowid_={weeken[changed_table]}")
                o = cur.fetchall()[0]
            if len(o) != 10:
                QMessageBox.critical(
                    self.ui,
                    "注意",
                    "库中无数据或数据异常。"
                )
            self.allClass = [] 
            for i in range(len(o)):
                if i != 0:
                    if i == SEPARATOR:
                        #self.ui.classTable.append('----')
                        self.allClass.append('----')
                        # self.ui.classTable.append('')
                        self.allClass.append('')
                    #self.ui.classTable.append(o[0][i])
                    self.allClass.append(o[i])
                    if i != 9:
                        #self.ui.classTable.append('')
                        self.allClass.append('')
            self.ui.classTable.setText('\n'.join(self.allClass))
            print(self.allClass)
            self.xx=False
            self.shjPos=-2
            for k in range(len(self.allClass)):
                if self.allClass[k]=="信息":
                    self.shjPos=k
                    self.xx=True
            if self.xx:
                init.std_out(f"[ 运行 ] 沈红杰这个小逼崽子在{self.shjPos}！")
            else:
                init.std_out(f"[ 运行 ] 没找着沈红杰！")
        
        if changed_time != '':
            spTimeList = initSpTime()
            if changed_time == "(新建时间表)":
                
                QMessageBox.about(
                        self.ui,
                        "提示",
                        "请重新打开'编辑'窗口以使用新建时间表。")
            else:
                judgeTime(changed_time)

        if changed_duty != '':
            self.show_duty(weeken[changed_duty])

        if changed_cd != '':
            global CHOSEN_COUNTDOWN
            CHOSEN_COUNTDOWN = changed_cd
            param["CHOSEN_COUNTDOWN"] = changed_cd
            with open(filePath+"/res/data/param.json",'w+',encoding='utf-8') as jsFile:
                json.dump(param,jsFile)
            self.ui.cdName.setText(cdName[changed_cd])
            self.ui.cd.setText(str(dateDelta(cdDate[changed_cd],DATE_NOW)))
        init.std_out("[ 运行 ] 与编辑对话框的会话结束！",2)
        return None
     
