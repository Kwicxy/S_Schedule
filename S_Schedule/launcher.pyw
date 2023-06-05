import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

import subwin

import init
from main import *


if __name__ == '__main__':
    param = init.get_json()
    table, cur = init.get_sql()
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   #Qt高分屏适配
    # 创建应用实例
    app = QApplication(sys.argv)
    # 创建主窗口和托盘实例
    win = MainWin()
    tray = TrayIcon(win)
    # 显示主窗口和托盘
    tray.show()
    tray.start_hint()
    #win.show()
    win.pend()
    # 启动应用进入事件循环
    app.exec_()
    win.thread.exit()
    flag = win.flag
    while flag and TASK_PROTECT:
        if flag and not SHJ:
            #QMessageBox.warning(
            #    win.ui,
            #    "哼哼",
            #    "请使用退出按钮\n这是退出课表的安全方式。"
            #)
            pass
        elif flag and SHJ:
            print("[ 警告 ] 沈红杰操你妈！")
        print("[ 警告 ] 主程序正在重新启动……")
        win.show()
        app.exec_()
        win.thread.exit()
    cur.close()
    sys.exit(table.close())
