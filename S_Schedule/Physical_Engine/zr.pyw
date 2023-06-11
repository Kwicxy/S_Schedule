###################################################
##############--Author:Octpus_tank--###############
##############------特-IIIv3.0------###############
###################################################
'''
-->适配物理引擎 Physical Engine
'''
import time as tm
import datetime as dt
import sys
import os
from tkinter import *
from tkinter.ttk import *
import ctypes
import random as rd
from win32api import GetSystemMetrics
import platform as pl
import engine as pe
import os
import datetime
import json as js
###################################################
file_name = os.path.join(os.getcwd(), "data.json")
sz=(500,480)

FPS=30
MOVE=True#是否移动

def write_in():
    today = dt.datetime.now().strftime("%m-%d")
    data = {}
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8", mode="r") as f:
            data = js.load(f)
    if today in data:
        data[today] += 1
    else:
        data[today] = 1
    with open(file_name, encoding="utf-8", mode="w") as f:
        js.dump(data, f, ensure_ascii=False, indent=True)

if datetime.time(21,29)<= datetime.datetime.now().time():
    ran = rd.random()
    print(ran)
    write_in()
    if ran <= 1.0/3.0:
        os.startfile("D:\\Project3\\Physical_Engine\\eg.lnk")


###################################################
w,h=GetSystemMetrics(0),GetSystemMetrics(1)
OS=pl.release()
###################################################
root=Tk()
root.title('值日')
if not OS in ['7','XP']:
    ctypes.windll.user32.SetProcessDPIAware()
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    root.tk.call('tk', 'scaling', ScaleFactor/75)
    sz=(sz[0]*2,sz[1]*2)

move=(rd.randint(0,w-sz[0]),rd.randint(0,h-sz[1]))
root.geometry('%dx%d'%sz+'+%d+%d'%move)
root.resizable(0,0)
###################################################
pos=list(move)
xhad=w-sz[0]
yhad=h-sz[1]

PE=pe.Physical_Engine([11110000000.4,rd.randint(-1000,1000)*114514], pos, [xhad*3.1,yhad*8.25,0,0], 0.8 , [0.714,0.7919],1)
#                    初速度      初位置      边界        重力    hitk    slidek
FLY_CONTROL=PE.move()

drag_tm = 0
drag_start = False

wait = 5*FPS
pos_nw = pos
PE.drag(pos,list(map(lambda x:x+rd.randint(-5,5),pos)),1)
def fly():
    global drag_tm, drag_start, pos
    if MOVE:
        pos_nw = [round(root.winfo_x(),0),round(root.winfo_y(),0)]
        
        if (abs(pos_nw[0]-pos[0])<=2 and abs(pos_nw[1]-pos[1])<=2):
            flag=False
            if not drag_start:
                handle_nw = next(FLY_CONTROL)
                pos1=handle_nw['ABSOLUTE']
                tk=handle_nw['TICK']
                if abs(pos1[0]-pos[0])>=2 or abs(pos1[1]-pos[1])>=2:
                    pos=pos1
##                    print(handle_nw['ABSOLUTE']) 
                    root.geometry('%dx%d'%sz+'+%d+%d'%pos)
                root.after(int(FPS*tk),fly)
            else:
                PE.drag(drag_start,pos_nw,drag_tm)
                drag_start = False
                drag_tm = 0
                root.after(0,fly)
        else:
            pos = pos_nw
            if not drag_start:
                drag_start = pos_nw
            drag_tm +=1
##            print(drag_start,pos,drag_tm)
            root.after(wait,fly)
def controlfly():
    global MOVE
    if not MOVE:
        MOVE=True
        fly()
    else:
        MOVE=False
###################################################
wek=tm.strftime('%a')
tm1=tm.strftime('%Y/%m/%d')
lbtime=Label(root,text=tm1+'  '+wek+'.',relief=FLAT,font=('黑体',30)).pack()
lbtitle=Label(root,text='值日'+' 组别:'+wek+'.',relief=FLAT,font=('黑体',30)).pack()
###################################################
path=os.getcwd()
f=open(os.path.join(path,'list.txt'))
line=f.readline()
while line[0:3]!=wek:
    line=f.readline()
f.close()
lst=list(line[4:].split('/'))
tolst=[]
tolst.append(lst[0])
saoa=lst[1].split(',')
sao=''
for j in saoa:
    sao=sao+j+'\n'
sao=sao[:-1]
tolst.append(sao)
tolst.append(lst[2])
tuo=lst[3][:-1]
if not tuo=='0':
    tolst.append(tuo)
string=''
for i in range(len(tolst)):
    work=['黑  板: ','扫  地: ','倒垃圾: ','拖  地: ']
    string+=work[i]+tolst[i]+'\n'
string=string[:-1]
lbstu=Label(root,text=string,relief=FLAT,font=('黑体',45),justify=RIGHT).pack()
###################################################
def tuichu():
    root.destroy()
    sys.exit()
mainmenu=Menu(root)
menuFile=Menu(mainmenu,tearoff=0)
mainmenu.add_cascade(label='菜单',menu=menuFile)
menuFile.add_cascade(label='移动',command=controlfly)
menuFile.add_separator()
menuFile.add_cascade(label='退出',command=tuichu)
root.config(menu=mainmenu)

def main():
    root.after(int(1*FPS),fly)
    root.mainloop()
###################################################
if __name__ == '__main__':
    main()

