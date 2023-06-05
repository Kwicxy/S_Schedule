import datetime

import init


cur = init.get_sql()[1]
SATURDAY_REFERENCE = init.get_json()[5]
WEDNESDAY_REFERENCE = init.get_json()[6]

# 判断时间表
def judgeTime(Obj):
    global cTimeObj
    # 判断当天时间表
    if Obj in ['5', '6', '周六']:
        cur.execute("SELECT * FROM '时间' WHERE _rowid_=2")
    elif Obj in ['0','1','2','3','4','通常']:
        cur.execute("SELECT * FROM '时间' WHERE _rowid_=1")
    else:
        cur.execute("SELECT * FROM 特殊时间 WHERE Name=:nm",{"nm":Obj})
    # 将时间表转化为dt对象
    cTimeTuple = cur.fetchall()[0]
    cTimeObj = []
    for i in range(len(cTimeTuple)-1):
        tempTime = cTimeTuple[i].split(':')
        cHr = int(tempTime[0])
        cMin = int(tempTime[1])
        cTimeObj.append(datetime.time(cHr, cMin))
    cTimeObj.append(datetime.time(23, 59, 59, 999))        # 时间的最大值qwq

    return cTimeObj

# 将目前时间与时间表逐一对照
def timeComp(Obj):
    '''temp, cnt-1'''
    temp = cTimeObj[0]
    cnt = 0
    while Obj.__ge__(temp):
        cnt += 1
        temp = cTimeObj[cnt]

    return (temp, cnt-1)

# 时间差值计算
def timeCalc(tma, tmb):
    dh = tmb.hour - tma.hour
    dm = tmb.minute - tma.minute
    dtime = dh *60 +dm
    return str(dtime)

def initSpDate():
    '''spDate, spDtStr'''
    cur.execute("SELECT Date FROM 特殊")
    cd = cur.fetchall()
    v = len(cd)
    spDate = []
    spDtStr = []
    for i in range(v):
        temp1 = cd[i][0]
        spDtStr.append(temp1)
        temp2 = temp1.split('-')
        yyyy = int(temp2[0])
        mm = int(temp2[1])
        dd = int(temp2[2])
        spDate.append(datetime.date(yyyy,mm,dd))
    return (spDate, spDtStr)
        
def initSpTime():
    '''spTimeList'''
    spTimeList=[]
    cur.execute("SELECT Name FROM 特殊时间")
    temp1 = cur.fetchall()
    for i in range(0,len(temp1)):
        spTimeList.append(temp1[i][0])
    return spTimeList
        
# 获取已有倒数日
def getCd():
    '''cdName, cdDate'''
    cur.execute("SELECT 名称 FROM 倒数日")
    temp = cur.fetchall()
    s = len(temp)
    cdName = []
    for i in range(s):
        cdName.append(temp[i][0])
    #print(cdName)

    cur.execute("SELECT 日期 FROM 倒数日")
    cd = cur.fetchall()
    s = len(cd)
    cdDate = []
    for i in range(s):
        temp = cd[i][0].split('-')
        yyyy = int(temp[0])
        mm = int(temp[1])
        dd = int(temp[2])
        cdDate.append(datetime.date(yyyy,mm,dd))
    #print(cdDate)
    print("[ 运行 ] 倒数日获取成功！")

    return (cdName, cdDate)

# 计算日期差值
def dateDelta(dta,dtb):
    ans=dta-dtb
    print("[ 运行 ] 完成了1次差值计算。")
    return ans.days
      
# 判断周六的AB课表
def judgeParity(Obj):
    delta = Obj.isocalendar()[1] % 2
    refer = datetime.date(2022, 4, 30).isocalendar()[1] % 2   # 参照日期【待确认】
    # 奇偶相同出参照的，不同出对象的
    if SATURDAY_REFERENCE==1:
        if delta == refer:
            return 2
        else:
            return 1
    else:
        if delta == refer:
            return 1
        else:
            return 2

def judgeThird(Obj):
    delta = Obj.isocalendar()[1] % 3
    refer = datetime.date(2022, 10, 15).isocalendar()[1] % 3   # 参照日期【待确认】
    ans = ((delta -refer)%3 +SATURDAY_REFERENCE) %3 +1
    return ans
    
if __name__=='__main__':
    ae=datetime.datetime.now().time()
    print(timeCalc_alter_school(ae))
