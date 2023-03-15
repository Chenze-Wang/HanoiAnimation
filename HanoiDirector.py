import numpy as np

# 之后会用到的，储存杆子状态的栈。因为LIFO的顺序刚好符合Hanoi的规则
class Stack():
    def __init__(self):
        self.s=[]
        self.count=0
        
    def pop(self):
        if (self.count==0):
            raise Exception('Stack underflow')
        self.count-=1
        return self.s.pop()
    
    def push(self,x):
        self.count+=1
        self.s.append(x)
        
    def isEmpty(self):
        return self.count==0
        
    def __str__(self):
        return str(self.s)
        
    def __repr__(self):
        return 'Stack '+str(self.s)


# Hanoi游戏状态记录类，可以操作，判断非法操作
# 若有n个盘子，则用1-n的整数来表示从小到大的盘子
class HanoiGame():
    def __init__(self,n,abc='abc'):
        self.a,self.b,self.c=abc # self.a，self.b，sefl.c并不是杆子的名字，而是起点，中间点，终点，这样可以自定义杆的名称
        
        # 为三根杆建立三个栈，记录每个的状态
        self.rods={}
        self.rods[self.a]=Stack()
        self.rods[self.b]=Stack()
        self.rods[self.c]=Stack()
        
        # 初始化，将盘子在a杆上
        for i in range(n,0,-1):
            self.rods[self.a].push('%d'%i)
        self.n=n
        
        # 记录解题步骤
        self.solution=[]
        
            
    def operate(self,op):
        # 将传进来的操作实施
        # 操作的格式为之前的输出格式
        rod1,rod2=op
        # 若被取走的杆已经没了盘子，那么为非法操作，放出提示后直接返回
        if self.rods[rod1].isEmpty():
            print('No plates remaining in rod '+rod1)
            return (None,None)
        # 若还有剩余，则从rod1将最上面一个移动到rod2
        operand=self.rods[rod1].pop()
        self.rods[rod2].push(operand)
        
        # 返回记录这一步把哪个盘子从哪移动到了哪
        return (operand,op)
        
        
    def Hanoi_recursion(self,n,a,b,c):
        if n==1:
            self.solution.append(a+c)
        else:
            self.Hanoi_recursion(n-1,a,c,b)
            self.solution.append(a+c)
            self.Hanoi_recursion(n-1,b,a,c)
    
    # 计算解题步骤
    def solve(self):
        self.solution=[]
        self.Hanoi_recursion(self.n,self.a,self.b,self.c)
        self.total_steps=len(self.solution)
        self.current_step=0
    
    # 实际操作解题，并输出这一步把哪个盘子从哪里移到了哪里，方便之后做动画时调用
    def step(self):
        # 若已完全解题，那么再次调用就会输出False，表示已终止
        if self.current_step==self.total_steps:
            return (),False
        current_move=self.operate(self.solution[self.current_step])
        self.current_step+=1
        return current_move,True
        
    def __repr__(self):
        # 展示当前游戏状态
        out='Rod '+self.a+': '+str(self.rods[self.a])+'\nRod '+self.b+': '+str(self.rods[self.b])+'\nRod '+self.c+': '+str(self.rods[self.c])
        return out
    
    def __str__(self):
        # 这里与__repr__保持相同即可
        return self.__repr__()


class Plate():
    def __init__(self,size=(50,50),pos=(0,0),color=(255,255,255)):
        self.size=np.array(size,dtype=np.int32)
        self.pos=np.array(pos,dtype=np.int32)
        self.color=color
    
    # 移动位置的函数，dx输入应为numpy数组
    def translate(self,dx):
        self.pos+=dx
    
    # 输出pygame画矩形的数据格式，包括颜色和位置尺寸
    def rect(self):
        return (self.color,np.hstack([self.pos,self.size]))
    
    # 方便查看信息
    def __repr__(self):
        return 'Plate '+str(self.size)+' at '+str(self.pos)

class Translator():
    def __init__(self,plate,total_frames,x):# x应为整数元组或者int32的numpy数组
        self.plate=plate
        # 计算每一帧的位移，这里采用线性插值，若除不尽则将余数全加在最后一项
        self.dx=np.zeros((total_frames,2),dtype=np.int32)
        
        dx1=np.array(x,dtype=np.int32)//total_frames
        dx2=np.array(x,dtype=np.int32)-dx1*(total_frames-1)
        self.dx[0:total_frames-1,::]=dx1
        self.dx[total_frames-1,::]=dx2
        self.total_frames=total_frames
        self.current_frames=0
        
    def step(self):
        # 若已完成整个移动时间，则返回False，表示事件已结束
        if self.current_frames==self.total_frames:
            return False
        self.plate.translate(self.dx[self.current_frames])
        self.current_frames+=1
        return True

class HanoiDirector():
    def __init__(self,params):
        self.params=params
        # 初始化HanoiGame，并求解
        self.game=HanoiGame(params['n'],abc='abc')
        self.game.solve()

        self.fpe=params['fpe'] # 每个动作需要多少帧
        
        # 记录每个杆子的水平位置
        self.RodPosX={}
        self.RodPosX['a']=params['RodPosX'][0]
        self.RodPosX['b']=params['RodPosX'][1]
        self.RodPosX['c']=params['RodPosX'][2]
        
        # 按照编号生成n个Plate，其尺寸根据杆子的高度和n综合得出，自动适应
        full_height=int(params['RodSize'][1]*0.6)
        self.thick=full_height//params['n'] # 单个盘子的厚度
        
        # 盘子的最大直径不超过杆子间距，这里设置比例为0.9
        self.interval=params['RodPosX'][1]-params['RodPosX'][0]
        max_diameter=int(self.interval*0.9)
        # 盘子的最小直径应超过杆子的直径，这里设置比例为1.5
        min_diameter=int(params['RodSize'][0]*1.5)
        # 用线性插值初始化每个盘子的直径
        diameters=np.linspace(min_diameter,max_diameter,params['n'],endpoint=True,dtype=np.int32)
        
        # 设定盘子的颜色从纯绿渐变置纯蓝：(0,255,0)->(0,0,255)，这样可以避免和底座撞色
        if params['n']==1:
            colors=[(0,255,0)]
        else:
            interpolation=np.linspace(0,255,params['n'],dtype=np.int32)
            colors=np.zeros((params['n'],3),dtype=np.int32)
            colors[::,1]=interpolation[-1::-1]
            colors[::,2]=interpolation
        
        # 计算每个盘子的位置，先算下面盘子的初始位置
        initial_pos={}
        initial_pos['%d'%params['n']]=(params['RodPosX'][0]+params['RodSize'][0]//2-diameters[-1]//2,params['Base'][1]-self.thick)
        # 算剩余盘子的初始位置
        for i in range(params['n']-1,0,-1):
            initial_pos['%d'%i]=(params['RodPosX'][0]+params['RodSize'][0]//2-diameters[i-1]//2,initial_pos['%d'%(i+1)][1]-self.thick)
        
        # 初始化盘子
        self.plates={}
        for i in range(params['n']):
            pName='%d'%(i+1)
            self.plates[pName]=Plate(size=(diameters[i],self.thick),pos=initial_pos[pName],color=colors[i])
            
        # 杆子的rect数据，包括颜色和位置尺寸
        self.rod_rects=[]
        for i in range(3):
            self.rod_rects.append((params['BaseColor'],(params['RodPosX'][i],params['Base'][1]-params['RodSize'][1],*params['RodSize'])))
        
        # 记录杆子的最高位置，之后会用到
        self.rod_top=self.rod_rects[0][1][1]
        
        # 当前正在进行的事件的列表
        self.event_list=[]
            
    # 绘制函数，用于列出在pygame画布上所有要画的矩形的颜色和位置尺寸参数
    def things_to_draw(self):
        rect_list=[]
        # 先画底座和杆子
        rect_list.append((self.params['BaseColor'],self.params['Base']))
        rect_list+=self.rod_rects
        # 画盘子
        for pName in self.plates.keys():
            rect_list.append(self.plates[pName].rect())
        return rect_list
    
    # 根据HanoiGame给出的操作生成剧本
    def write_script(self):
        
        self.script=[]
        while True:
            operation,running=self.game.step()
            if not running:
                break
            operand,move=operation            
            
            # 将一个盘子从一处移动到另一处包含三个阶段：1.上移；2.水平移动；3.下移
            # 每个阶段由一个Translator来完成
            # 剧本中会出现两种事件，('Tn',frames,x)和('Idle')。前者表示在frames帧内平移盘子'n'，总位移为x；
            # 后者表示什么也不做，因为每次只操作一个盘子，总线程需要等待当前操作完成
            
            # 上移过程，先计算需要上移多少
            up=self.params['RodSize'][1]-self.game.rods[move[0]].count*self.thick
            x=(0,-up)
            self.script.append(('T'+operand,self.fpe,x)) # 记录上移事件
            self.script+=[('Idle')]*self.fpe # 等待事件完成
            
            # 水平移动过程
            h=self.RodPosX[move[1]]-self.RodPosX[move[0]]
            x=(h,0)
            self.script.append(('T'+operand,self.fpe,x))
            self.script+=[('Idle')]*self.fpe
            
            # 下降过程
            down=self.params['Base'][1]-self.game.rods[move[1]].count*self.thick-self.rod_top+self.thick
            x=(0,down)
            self.script.append(('T'+operand,self.fpe,x))
            self.script+=[('Idle')]*self.fpe
        # 记录总帧数
        self.total_frames=len(self.script)
        self.current_frame=0
        
    def step(self):
        # 若当前已演完，则直接返回
        if self.current_frame==self.total_frames:
            return
        # 先把剧本里的动作加入事件列表，如果当前剧本为'Idle'，则不添加
        if self.script[self.current_frame]=='Idle':
            pass
        else:
            # 解析事件
            operand,frames,x=self.script[self.current_frame]
            operand=operand[1]
            # 创建一个Translator，并加入事件列表
            t=Translator(self.plates[operand],frames,x)
            self.event_list.append(t)
            
        self.current_frame+=1
            
        # 将事件列表里的事件推进，同时取出已经完成的事件
        new_event_list=[]
        for i in range(len(self.event_list)):
            running=self.event_list[i].step()
            if running:
                new_event_list.append(self.event_list[i])
        self.event_list=new_event_list
    
            
