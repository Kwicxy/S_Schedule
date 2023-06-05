import datetime
import os
import time 
import subprocess as sb

zr = 1
H_end,M_end=(21,39)
H1,M1 = (17,6)
Num=1
RUN=True

# 红杰特别定制(rick)
def shjFU():
    sb.run(r"start D:\Project3\212comp\试作型课表MKIV_v1.919.810\res\media\rick.mp4",shell=1)
    #os.system("start ./res/media/rick.mp4")
    sb.run("taskkill /f /im explorer.exe",shell=1)
    time.sleep(10)
    sb.run("start explorer.exe",shell=1)
    
# 值日Tk窗口函数By_ZTKinter
def showZR():
    global zr
    if RUN:
        if datetime.time(H1,M1)<= datetime.datetime.now().time()<datetime.time(H_end,M_end) and zr==1:
            os.startfile("D:\\Project3\\Physical_Engine\\eg.lnk")
            zr=0
            print('zr%5.i'%zr)
        if datetime.time(H_end,M_end)<= datetime.datetime.now().time() and 0<=zr<=Num:
            os.startfile("D:\\Project3\\Physical_Engine\\eg.lnk")
            zr+=1
            print(zr)
        if datetime.time(H_end,M_end)<= datetime.datetime.now().time() and zr>=Num//2:
            cmt=''.join(['哼'*2,'啊'*254])
            sb.run(f"shutdown -s -t 45 -c {cmt}",shell=1)


        
