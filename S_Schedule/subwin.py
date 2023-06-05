import json
from PyQt5.QtWidgets import  QApplication, QDialog, QMessageBox, QMainWindow, QLabel, QFrame, QWidget
from PyQt5.QtCore import  QDate, QRect, Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5 import uic

from time import sleep
import init
from methods import *

table, cur = init.get_sql()
filePath = init.get_path()
param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR, TOMORROW, CONSOLE, IGNORE_PID = init.get_json()
DATE_NOW, WKDAY_NOW, weekcn, weeken = init.get_date()


TITLE_BAR_HEIGHT = 45

def handle_hint(flag):

    app = QApplication([])
    hint = HintBar()
    hint.move(0,900)
    hint.show()
    app.exec_()
    while flag == 0:
        sleep(1)
    else:
        hint.hide()

class HintBar(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/hint2.ui",self)
        self.setWindowFlags(Qt.WindowStaysOnBottomHint|Qt.Tool|Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


# 开发者选项对话框
class DevWin(QDialog):

    _startPos = None
    _endPos = None
    _isTracking = False

    # 初始化
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/dev.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR, TOMORROW, CONSOLE, IGNORE_PID = init.get_json()
        self.ui.spinBox.setValue(REFRESH_RATE)
        self.ui.separatorPosition.setValue(SEPARATOR)
        self.ui.confirmButton.clicked.connect(self.handleConfirm)
        self.ui.cancelButton.clicked.connect(self.handleCancel)
        self.ui.protectBox.setChecked(TASK_PROTECT)
        self.ui.startupBox.setChecked(STARTUP)
        self.ui.homoS.setChecked(HOMO)
        self.ui.hongjie.setChecked(SHJ)
        self.ui.tomorrowBox.setChecked(TOMORROW)
        self.ui.ignoreBox.setChecked(IGNORE_PID)
        CONSOLE_TXT = ["INFO", "WARN", "ERROR"]
        self.ui.consoleBox.setCurrentText(CONSOLE_TXT[CONSOLE])
        init.std_out("[ 开发 ] 初始化已完成", 1)
    

    def handleConfirm(self):
        global param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR
        GET_PROTECT = self.ui.protectBox.isChecked()
        GET_SPIN = self.ui.spinBox.value()
        GET_SEPARATOR = self.ui.separatorPosition.value()
        GET_SATURDAY = self.ui.satRefer.value()
        GET_STARTUP = self.ui.startupBox.isChecked()
        GET_HONGJIE = self.ui.hongjie.isChecked()
        GET_HOMO = self.ui.homoS.isChecked()
        GET_TOMORROW = self.ui.tomorrowBox.isChecked()
        GET_CONSOLE = self.ui.consoleBox.currentIndex()
        GET_IGNORE = self.ui.ignoreBox.isChecked()
        param["TASK_PROTECT"] = GET_PROTECT
        param["REFRESH_RATE"] = GET_SPIN
        param["STARTUP"] = GET_STARTUP
        param["SHJ"] = GET_HONGJIE
        param["SATURDAY_REFERENCE"] = GET_SATURDAY
        param["HOMO"] = GET_HOMO
        param["SEPARATOR"] = GET_SEPARATOR
        param["TOMORROW"] = GET_TOMORROW
        param["CONSOLE"] = GET_CONSOLE
        param["IGNORE_PID"] = GET_IGNORE
        with open(filePath +"/res/data/param.json", 'w+', encoding='utf-8') as jsFile:
            json.dump(param,jsFile,indent=True)
        print(f"[ 开发 ] 已写入更改： {param}", 1)
        param, TASK_PROTECT, REFRESH_RATE, STARTUP, SHJ, SATURDAY_REFERENCE, WEDNESDAY_REFERENCE, HOMO, CHOSEN_COUNTDOWN, SEPARATOR, TOMORROW, CONSOLE, IGNORE_PID = init.get_json()
        self.hide()

    def handleCancel(self):
        init.std_out("[ 开发 ] 操作已取消。", 1)
        self.hide()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

# 新建项目统一对话框
class NewWin(QDialog):
    '''
        这是一个超级无敌至尊大缝合怪类
        函数基本上都是从以前迭代的版本直接复制下来的
        所以可能会出现一些奇奇怪怪的bug
        OvO
    '''

    _startPos = None
    _endPos = None
    _isTracking = False

    # 初始化
    def __init__(self, dev, parent=None):
        super().__init__()
        self.ui = uic.loadUi("./ui/new.ui", self)
        #self.ui = NewWin_Ui()
        #self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dev = dev
        self.qdaten = QDate(DATE_NOW.year,DATE_NOW.month,DATE_NOW.day)
        self.ui.dateEdit.setDate(self.qdaten)
        self.ui.confirmButton.clicked.connect(self.handleConfirm)
        self.ui.cancelButton.clicked.connect(self.handleCancel)
        for i in range(9):
                exec(f"self.ui.comboBox_{i+2}.setEditable(True)")
        # 时间表初始化
        self.ui.nextButton.clicked.connect(self.handleNext)
        self.ui.clearButton.clicked.connect(self.handleClear)
        # 倒数日初始化
        cdName = getCd()[0]
        self.tempName=cdName
        del(self.tempName[0])
        self.ui.cdBox.addItems(self.tempName)
        self.ui.delButton.clicked.connect(self.handleDelete)

    # ui重新加载（重新打开窗口时将按钮全部设置为不勾选）
    def resetUI(self):
        self.ui.dateEdit.setDate(self.qdaten)
        self.ui.checkBox_class.setCheckState(False)
        self.ui.checkBox_time.setCheckState(False)
        self.ui.checkBox_cd.setCheckState(False)
        self.ui.nextButton.setDisabled(False)
        self.startTimes = 1
        # 时间部分重置
        self.loadtime = False
        self.ui.timeStatus.setText("等待键入…")
        with open(filePath+"./res/userfiles/guide.txt",encoding="utf-8") as self.f: 
            self.listGuide = self.f.readlines()
        self.ui.guide.setText(self.listGuide[0].rstrip('\n'))
        self.cnt=1
        self.ui.progressBar.setValue(1)
        self.qname1=''
        self.qname=''
        self.timeBox=[]
        # 课表对应的时间表combobox
        spTimeList = initSpTime()
        self.timeList=['', "通常", "周六"]
        if len(spTimeList)!=0:
            for t in spTimeList:
                self.timeList.append(t)
        self.ui.usingTime.addItems(self.timeList)
        self.show()

    # take一个error code弹出错误信息
    def handleError(self, code:int, sender:str):
        ERROR_INFO = {1:"日期重复。",2:"数据项格式不正确或无数据项。",3:"数据项不匹配。",4:"实例正在被使用。"}
        QMessageBox.warning(self.ui,
                                  "错误",
                                  f"错误位于：{sender}。\n错误代码{code}：{ERROR_INFO[code]}")

    # 删除倒数日函数
    def handleDelete(self):
        global CHOSEN_COUNTDOWN, cdName
        delName=self.ui.cdBox.currentText()
        delNum=self.ui.cdBox.currentIndex()
        if delNum==CHOSEN_COUNTDOWN:
            self.handleError(4,"倒数日")
        else:
            choice=QMessageBox.question(self.ui,
                                        '注意',f'确定删除“{delName}”吗？')
            if choice==QMessageBox.Yes:
                cur.execute("DELETE FROM '倒数日' WHERE _rowid_=?",(delNum+2,))
                table.commit()
                cdName, cdDate = getCd()
                self.ui.cdBox.clear()
                self.tempName=cdName
                del(self.tempName[0])
                self.ui.cdBox.addItems(self.tempName)
    
    # 时间表函数
    def handleNext(self):
        self.qname=self.ui.lineEdit.text()
        if self.qname=='':
            self.handleError(2,"时间表")
            return
        if self.qname!=self.qname1:
            if self.cnt!=1:
                QMessageBox.warning(self.ui,
                                    "警告",
                                    f"不一致的名称.\n已编辑的名称: {self.qname1}\n当前名称: {self.qname}")
                return
            else:
                self.qname1=self.qname
        qtime=self.ui.timeEdit.time()
        self.tmStr=qtime.toString("hh:mm")
        print(self.tmStr)
        if self.cnt==20:
            self.timeBox.append(self.tmStr)
            print(self.timeBox)
            info='请确认键入信息:    \n'
            for i in range(20):
                info=info+str(i+1)+':  '+self.timeBox[i]+'\n'
            QMessageBox.about(self.ui,
                              "确认",
                              info)
            self.loadtime = True
            self.ui.timeStatus.setText("键入完成。")
            self.ui.nextButton.setDisabled(True)
        else:
            self.timeBox.append(self.tmStr)
            self.cnt+=1
            self.ui.progressBar.setValue(self.cnt)
            self.ui.guide.setText(self.listGuide[self.cnt-1].rstrip('\n'))

    def handleClear(self):
        t = QMessageBox.question(self.ui,
                             "注意",
                             "这将会删除已写入的全部特殊时间表！\n \
                             是否继续？")
        if t == QMessageBox.Yes:
            cur.execute("DELETE FROM 特殊时间")
            table.commit()
            QMessageBox.about(self.ui,
                              "提示",
                              "已完成删除操作.")

    # 确认按钮函数
    def handleConfirm(self):
        # 课表部分
        if self.ui.checkBox_class.isChecked():
            global spDate,spDtStr
            self.dev.ctable = "(新建课表)"
            spDate, spDtStr = initSpDate()
            qdate = self.ui.dateEdit.date()
            dtStr = qdate.toString("yyyy-MM-dd")
            if dtStr in spDtStr:
                t = QMessageBox.question(self.ui,
                                    "注意 - 课程表",
                                    "已有该日记录, 是否覆盖?")
                if t == QMessageBox.Yes:
                    cur.execute("DELETE FROM '特殊' WHERE Date=:dt",{"dt":dtStr}) 
                    table.commit()
                else:
                    self.handleError(1,"课表")
                    return

            template = self.ui.comboBox.currentText()       #课表模板
            edit_array = ['']*9                             #存储对于模版的更改
            for i in range(9):                              #循环赋值
                exec(f"edit_array[{i}]=self.ui.comboBox_{i+2}.currentText()")
            if template in ['周六1', '周六2']:               #判断模板课表
                cur.execute(
                    f"SELECT * FROM '周六' WHERE _rowid_={int(template[-1])}")
            else:
                cur.execute(f"SELECT * FROM '正常' WHERE _rowid_={weeken[template]}")
            c1 = cur.fetchall()
            c2 = ['']*10
            for i in range(9):
                c2[i] = c1[0][i+1]
                if edit_array[i] != '':
                    c2[i] = edit_array[i]
            print(c2)
            usingtable = self.ui.usingTime.currentText()
            cur.execute("INSERT INTO '特殊' VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (dtStr,c2[0], c2[1], c2[2], c2[3], c2[4], c2[5], c2[6], c2[7],
                         c2[8],usingtable))
            table.commit()
            init.std_out("[ 新建 ] 新建课表操作完成。",1)
        
        # 时间表部分
        if self.ui.checkBox_time.isChecked() and self.loadtime:
            cur.execute("INSERT INTO 特殊时间 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        [self.timeBox[0],self.timeBox[1],self.timeBox[2],self.timeBox[3],
                         self.timeBox[4],self.timeBox[5],self.timeBox[6],self.timeBox[7],
                         self.timeBox[8],self.timeBox[9],self.timeBox[10],self.timeBox[11],
                         self.timeBox[12],self.timeBox[13],self.timeBox[14],self.timeBox[15],
                         self.timeBox[16],self.timeBox[17],self.timeBox[18],self.timeBox[19],
                         self.qname1])
            table.commit()
            QMessageBox.about(self.ui,
                              "提示",
                              "已完成新建操作.\n重新打开'编辑'窗口后生效.")
        elif self.ui.checkBox_time.isChecked() and self.loadtime == False:
            self.handleError(2,"时间表")

        # 倒数日部分
        if self.ui.checkBox_cd.isChecked():
            qdate = self.ui.newdt.date()
            dtStr = qdate.toString("yyyy-MM-dd")
            newName = self.ui.newcd.text()
            t = QMessageBox.question(self.ui,
                                   "请确认",
                                    f"请确认将要添加的内容：\n \
                                    名称：{newName}\n \
                                    日期：{dtStr}")
            if t == QMessageBox.Yes and newName != '':
                cur.execute("INSERT INTO '倒数日' VALUES(?,?)", (newName,dtStr))
                table.commit()
                QMessageBox.about(self.ui,
                                  "完成",
                                  "已完成新建")
            elif t == QMessageBox.Yes and newName == '':
                self.handleError(2,"倒数日")
                return
            cdName,cdDate = getCd()
            self.ui.cdBox.clear()
            self.tempName = cdName
            del(self.tempName[0])
            self.ui.cdBox.addItems(self.tempName)
        
        if self.ui.checkBox_class.isChecked() or self.ui.checkBox_time.isChecked() and self.loadtime == True or self.ui.checkBox_cd.isChecked():
            user_choice = QMessageBox.question(self,
                                               "提示",f"操作成功完成\n本次启动累计完成了{self.startTimes}次操作\n是否继续？")
            if user_choice:
                self.startTimes += 1
                return
            else:
                self.hide()
        else:
            QMessageBox.about(self,"提示","您未作出任何操作。")
        self.hide()

    # 取消按钮函数
    def handleCancel(self):
        self.hide()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

# 编辑对话框
class EditWin(QDialog):
    '''
        通过四个combobox实现快速更换课表
        也可以呼出newwin进行高级编辑
    '''

    _startPos = None
    _endPos = None
    _isTracking = False

    # 初始化
    def __init__(self,Main,parent=None):
        self.ctable = self.ctime = self.cduty = self.ccd = ''
        super().__init__()
        self.ui = uic.loadUi("./ui/dlg.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.master = Main
        #self.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint)
        self.show()
        self.ui.classBox.addItems(
            ['', '周一', '周二', '周三', '周四', '周五', '周六1', '周六2'])
        spTimeList = initSpTime()
        self.timeList = ['', "通常", "周六"]
        if len(spTimeList) != 0:
            for t in spTimeList:
                self.timeList.append(t)
        self.ui.timeBox.addItems(self.timeList)
        self.ui.dutyBox.addItems(
            ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'])
        cdName, cdDate = getCd()
        self.cdAns=cdName
        self.ui.cdBox.addItems(self.cdAns)
        self.ui.classBox.currentIndexChanged.connect(self.handleClass)
        self.ui.timeBox.currentIndexChanged.connect(self.handleTime)
        self.ui.dutyBox.currentIndexChanged.connect(self.handleDuty)
        self.ui.cdBox.currentIndexChanged.connect(self.handleCountdown)
        self.ui.confirmButton.clicked.connect(self.handleConfirm)
        self.ui.cancelButton.clicked.connect(self.handleCancel)
        self.ui.newButton.clicked.connect(self.handleNew)
        init.std_out("[ 编辑 ] 初始化已完成",1)


    def handleNew(self):
        self.newdlg = NewWin(self)
        self.newdlg.resetUI()

    def handleClass(self):
        self.ctable = self.ui.classBox.currentText()
        #if self.ctable == '(新建课表)':
        #    self.mod = ModWin()
        #    init.std_out("[ 编辑 ] 正在启动对话框……")
        #    self.mod.exec_()
        init.std_out("[ 编辑 ] 选择了课表：", self.ctable,1)

    def handleTime(self):
        self.ctime = self.ui.timeBox.currentText()
        #if self.ctime == '(新建时间表)':
        #    self.tm = TimeWin()
        #    init.std_out("[ 编辑 ] 正在启动对话框……")
        #    self.tm.exec_()
        init.std_out("[ 编辑 ] 选择了时间表：", self.ctime,1)

    def handleDuty(self):
        self.cduty = self.ui.dutyBox.currentText()
        init.std_out("[ 编辑 ] 选择了值日表：", self.cduty,1)

    def handleCountdown(self):
        self.ccd = self.ui.cdBox.currentIndex()
        #if self.ccd==len(self.cdAns)-1:
        #    self.cdw= CdWin()
        #    init.std_out("[ 编辑 ] 正在启动对话框……")
        #    self.cdw.exec_()
        #    getCd()
        #    self.cdAns=cdName
        #    self.cdAns.append("(编辑)")
        #    self.ui.cdBox.clear()
        #    self.ui.cdBox.addItems(self.cdAns)
        init.std_out("[ 编辑 ] 选择了倒数日：", self.ccd,1)

    def handleCancel(self):
        self.master.updateEdit(self.ctable, self.ctime, self.cduty, self.ccd)
        init.std_out("[ 编辑 ] 操作已取消。",1)
        self.hide()

    def handleConfirm(self):
        init.std_out("[ 编辑 ] 操作已提交！",1)
        self.master.updateEdit(self.ctable, self.ctime, self.cduty, self.ccd)
        self.hide()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and e.y() <= TITLE_BAR_HEIGHT:
            self._isTracking = False
            self._startPos = None
            self._endPos = None


class TimeWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/tm.ui",self)

class BannerWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/banner.ui",self)
        self.move(480,-160)

    def move_in(self):
        y = -160
        while y < 0:
            self.move(480,y)
            y+=2
            sleep(0.002)

    def move_out(self):
        y = 0
        while y > -160:
            self.move(480,y)
            y-=2
            sleep(0.002)

if __name__ == '__main__':
    bn=BannerWin()
    bn.show()
    while True:
        if datetime.time(14,36,55)<= datetime.datetime.now().time() and not self.bn.on and datetime.date.today().weekday() == 5:
            bn.move_in()
        if datetime.time(14,37,5)<= datetime.datetime.now().time() and self.bn.on and datetime.date.today().weekday() == 5:
            bn.move_out()
        sleep(0.1)
