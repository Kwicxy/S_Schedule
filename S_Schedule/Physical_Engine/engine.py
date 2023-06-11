###################################################
##############--Author:Octpus_tank--###############
##############------ Alpha2.0-------###############
###################################################
'''
--------------*#  Physical Engine  #*--------------
创建:Physical_Engine(v, location, edge, g, v_hitloss_rate = [1,1], v_slideloss_rate = 1)
参数分别为:
  i. ) 初速度  [<x方向速度>,<y方向速度>]
  ii.) 初始位置  [<x方向位置>,<y方向位置>]
 iii.) 边界  [<x方向上界>,<y方向上界>,<x方向下界>,<y方向下界>] 注意:x轴向下建立.
  iv.) 重力加速度  (单位长度/tick) 注意:x轴向下建立.
  v. ) 水平滑行速度损失比 (单位长度/(tick^2))
  vi.) 精度(小数位数) 注意:不要在运行过程中修改.如要修改请调用check_data()

包含:
  i. ) check_data():检查各项属性是否正常.若不正常,则退出或自动修复或提醒
  ii.) drag(<初始绝对坐标>,<末了绝对坐标>,<耗时(tick)>):拖动窗口时调用
 iii.) move():生成器.每次返回下一次的运动指令.
              返回值:{'ABSOLUTE':<绝对坐标>, 'RELATIVE':<相对坐标(移动方式)> , 'TICK':<动作耗时(tick)>}

'''
from time import sleep
##from zr import main
class Physical_Engine :
    
    def __init__(self, v, location, edge, g, v_hitloss_rate = [1,1], v_slideloss_rate = 1):
        global INT, FLOAT
        self.v = v #初速度  [<x方向速度>,<y方向速度>]
        self.location = location #初始位置  [<x方向位置>,<y方向位置>]
        self.edge = edge #边界  [<x方向上界>,<y方向上界>,<x方向下界>,<y方向下界>] 注意:x轴向下建立.
        self.g = g #重力加速度  (单位长度/tick) 注意:x轴向下建立.
        self.v_hitloss_rate = v_hitloss_rate #[<x方向速度撞击损失比>,<y方向速度撞击损失比>]
        self.v_slideloss_rate = v_slideloss_rate #水平滑行速度损失比 (单位长度/(tick^2))
        self.accuracy = 2 #精度(小数位数) 注意:不要在运行过程中修改.如要修改请调用check_data()
        INT = type(1)
        FLOAT = type(0.1)
        self.__ACCURACY = 0.1** self.accuracy #精度(小数) 精度过高会引起性能问题(特别是碰撞期间)
        self.__activity = [] #初始化<运动过程分解任务事件存储列表>

    def __selfexplode(self,error_type ,errors):#报错与退出
        print(f'*出现错误:{error_type}:')
        for error in errors:
            print(error)
        sleep(3);exit()

    def check_data(self):
        errors = []
        ##检测数据类型
        if not (type(self.v[0]) in [INT,FLOAT] and\
           type(self.v[1]) in [INT,FLOAT]):
            errors.append(f'初始速度 数据类型有误(设定速度:{self.v})')
        if not (type(self.location[0]) in [INT,FLOAT] and\
           type(self.location[1]) in [INT,FLOAT]):
            errors.append(f'初始位置 数据类型有误(设定速度:{self.location})')
        if not (type(self.location[0]) in [INT,FLOAT] and\
           type(self.edge[1]) in [INT,FLOAT] and\
           type(self.edge[2]) in [INT,FLOAT] and\
           type(self.edge[3]) in [INT,FLOAT]):
            errors.append(f'初始边界 数据类型有误(设定速度:{self.edge})')
        if not type(self.g) in [INT,FLOAT]:
            errors.append(f'重力加速度 数据类型有误(设定速度:{self.g})')
        if not (type(self.v_hitloss_rate[0]) in [INT,FLOAT] and\
           type(self.v_hitloss_rate[1]) in [INT,FLOAT]):
            errors.append(f'速度撞击损失比 数据类型有误(设定速度:{self.v_hitloss_rate})')
        if not type(self.v_slideloss_rate) in [INT,FLOAT]:
            errors.append(f'水平滑行速度损失比 数据类型有误(设定速度:{self.v_slideloss_rate})')
        if not type(self.accuracy) in [INT]:
            errors.append(f'精度 数据类型有误(设定速度:{self.accuracy})')
        if not errors == []:
            self.__selfexplode('数据类型错误' ,errors)
        ##检测数据合理性
        if not (self.edge[2] <= self.location[0] <= self.edge[0]) and\
                (self.edge[3] <= self.location[1] <= self.edge[1]):
            errors.append(f'初始位置 越界(设定初始位置:{self.location} ,设定边界:{self.edge})')
        if not (self.v_hitloss_rate[0] > 0 and\
                self.v_hitloss_rate[1] > 0):
            errors.append(f'速度撞击损失比 出现负数(设定速度撞击损失比:{self.v_hitloss_rate})')
        if not self.v_slideloss_rate > 0:
            errors.append(f'水平滑行速度损失比 出现负数(设定水平滑行速度损失比:{self.v_hitloss_rate})')
        if not self.accuracy >=1:
            errors.append(f'精度 小于了1(设定精度:{self.accuracy})')
        if not errors == []:
            self.__selfexplode('数据合理性问题' ,errors)
        ##建议
        notices = []
        if not (self.v_hitloss_rate[0] <= 1 and\
                self.v_hitloss_rate[1] <=1):
            notices.append(f'速度撞击损失比 大于1(设定速度撞击损失比:{self.v_hitloss_rate})')
        if not self.v_slideloss_rate <= 1:
            notices.append(f'水平滑行速度损失比 大于1(设定水平滑行速度损失比:{self.v_hitloss_rate})')
        if not self.accuracy <=3:
            notices.append(f'精度 大于了3(设定精度:{self.accuracy})(根据设备性能而定)')
        if not 0.1**self.accuracy == self.__ACCURACY: #如设定精度与实际精度不符
            notices.append(f'设定精度与实际精度不符.已自动调整')
            self.__ACCURACY = 0.1** self.accuracy
        if not notices == []:
            print('#注意:')
            for notice in notices:print(notice)
        #规整精度.规整到self.__ACCURACY的精度
        self.v [0] = round(self.v [0],self.accuracy)
        self.v [1] = round(self.v [1],self.accuracy)

    def __edge_handle(self):
        x_location_nw , y_location_nw = tuple(self.location) #初始化模拟位置
        x_v , y_v = tuple(self.v) #初始化模拟速度
        self.__result = [] #初始化模拟结果
        tick_last = 0 #记录上一次的时刻,便于计算下一个动作所需时间
        
        if not ((self.edge[2] <= x_location_nw + x_v <= self.edge[0]) and\
           (self.edge[3] <= y_location_nw + y_v <= self.edge[1])): #如越界
            for tick in range(1,int(1//self.__ACCURACY)+1):#开始模拟.模拟精度:self.__ACCURACY
                flag=False #记录该时刻是否碰撞
                x_location_nw += x_v * self.__ACCURACY #迈步
                y_location_nw += y_v * self.__ACCURACY
                if not self.edge[2] <= x_location_nw <= self.edge[0]:#x方向碰撞
                    self.v[0] *= -1 #x方向速度反向
                    x_location_nw -= x_v * self.__ACCURACY #将出界的步撤回
                    self.v[0] *= self.v_hitloss_rate[0] #x方向碰撞速度衰减
                    flag=True
                if not self.edge[3] <= y_location_nw <= self.edge[1]:#y方向碰撞
                    self.v[1] *= -1 #y方向速度反向
                    #self.v[0] *= -1
                    y_location_nw -= y_v * self.__ACCURACY #将出界的步撤回
                    self.v[1] *= self.v_hitloss_rate[1] #y方向碰撞速度衰减
                    flag=True
                if self.edge[1] >= self.location[1] >= self.edge[1]-self.__ACCURACY*100 and abs(self.v[1])<self.__ACCURACY*100: #滑行时
                    self.v[1] = 0 #y方向速度归0
                    if self.v[0]!=0:
                        tag = self.v[0]/abs(self.v[0])
                        vx_nw = self.v[0] - tag * self.v_slideloss_rate
                        if vx_nw/(abs(vx_nw)) == tag :#同向
                            self.v[0] = vx_nw#计算速度损失
                        else:
                            self.v[0] = 0
                else: #飞行时
                    self.v[1] += self.g * self.__ACCURACY #计算重力加速度

                if flag: #若该时刻发生了碰撞
                    self.__result.append([x_location_nw, y_location_nw,\
                                          (tick - tick_last) * self.__ACCURACY]) #将碰撞时的动作加入
                    tick_last = tick #记录碰撞时刻
                    x_v , y_v = tuple(self.v) #刷新速度
            self.__result.append([x_location_nw, y_location_nw,\
                                  (tick - tick_last) * self.__ACCURACY]) #加入收尾动作
        self.__result = self.__result[::-1] #列表倒转,便于pop从栈顶倒序取出

    def move(self):
        #self.check_data()
        while True:
            ## handle_nw :新的命令.即每次调用返回的命令的原始格式. 内容:[<目标点x绝对位置>,<目标点y绝对位置>,<耗时>]
##            print(self.v)
            if self.__activity == []:#如栈中的任务做完
                self.__edge_handle()
                if self.__result != []: #会发生碰撞,运动过程分解
                    self.__activity += self.__result[:-1] #存储要执行的步骤.第一步直接准备执行,不存入
                    handle_nw = self.__result[-1] #取出第一步(内容:绝对位置xy)
                else: #不会发生碰撞
                    handle_nw = [self.v[0]+self.location[0],self.v[1]+self.location[1],1] #直接加上速度
                if self.edge[1] >= self.location[1] >= self.edge[1]-self.__ACCURACY*100 and abs(self.v[1])<self.__ACCURACY*100: #滑行时
                    self.v[1] = 0 #y方向速度归0
                    if self.v[0]!=0:
                        tag = self.v[0]/abs(self.v[0])
                        vx_nw = self.v[0] - tag * self.v_slideloss_rate
                        if vx_nw/(abs(vx_nw)) == tag :#同向
                            self.v[0] = vx_nw#计算速度损失
                        else:
                            self.v[0] = 0
                else: #飞行时
                    self.v[1] += self.g #计算重力加速度
                self.v [0] = round(self.v [0],self.accuracy) #规整精度.规整到self.__ACCURACY的精度
                self.v [1] = round(self.v [1],self.accuracy)
            else: #如栈中的任务没做完
                handle_nw = self.__activity.pop()
            ##以下整理输出
            handle_absolute = tuple(handle_nw[:-1]) #绝对坐标
            handle_relative = tuple([handle_nw[0]-self.location[0],\
                                     handle_nw[1]-self.location[1]]) #相对坐标(移动方式)
            handle_result = {'ABSOLUTE':handle_absolute , 'RELATIVE':handle_relative ,\
                             'TICK':handle_nw[-1]}
            self.location = handle_nw[:-1] #刷新内部位置数据
            yield handle_result 
    def __list_cal(self, list1, list2, operation):
        return eval(f'list(map(lambda x:x[0]{operation}x[1],zip({list1},{list2})))')

    def drag(self, last_location, nw_location, delt_time): #拖动对象的处理
        delt_v = self.__list_cal(nw_location, last_location ,'-')
        self.v = self.__list_cal(delt_v, [delt_time]*2 , '/')
        self.location = nw_location
        for i in range(3):
            location_piece = self.location[i%2]
            edge_piece = self.edge[i]
            logic = ['<','>'][i//2]
            if not eval(f'{location_piece}{logic}{edge_piece}'):
                self.location[i%2] = edge_piece
##                print(f'{location_piece}{logic}{edge_piece}')
        #self.check_data()

##if __name__=='__main__':
##    main()
