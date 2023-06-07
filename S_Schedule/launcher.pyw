import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

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
    win.pend()
    # 启动应用进入事件循环
    app.exec_()
    win.thread.exit()
    flag = win.flag
    while flag and TASK_PROTECT:
        print("[ 警告 ] 主程序正在重新启动……")
        win.show()
        app.exec_()
        win.thread.exit()
    cur.close()
    sys.exit(table.close())
