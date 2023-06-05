import os
import subprocess as sb
path = os.path.abspath(__file__)
filePath = os.path.dirname(path)
with open(filePath+"\\res\\data\\pid.txm",'r',encoding='utf-8') as f:
    pid = f.readline()

sb.run("taskkill /f /pid "+pid, shell=1)
os.startfile(filePath+"\\launcher.pyw")
