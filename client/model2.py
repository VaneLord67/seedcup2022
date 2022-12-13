from utils import *
from env import Env
import threading
from saveload import *

def cruise(env,flag):
    character = env.us[flag]
    x = character.x
    y = character.y
    pos = (x,y)
    if flag == 0:#角色0
        l1 = line((18,-2),(18,-18))
        l2 = line((18,-18),(2,-18))
        l3 = line((2,-18),(2,-2))
        l4 = line((2,-2),(18,-2))
    if flag == 1:#角色1
        l1 = line((13,-7),(13,-13))
        l2 = line((13,-13),(7,-13))
        l3 = line((7,-13),(7,-7))
        l4 = line((7,-7),(13,-7))
    if pos in l1[:-1]:
        env.dir[flag] = 2
    elif pos in l2[:-1]:
        env.dir[flag] = 1 
    elif pos in l3[:-1]:
        env.dir[flag] = 5
    elif pos in l4[:-1]:
        env.dir[flag] = 4
    else:
        l = list(set(l1+l2+l3+l4))
        mind = 24
        for i in l:
            if distance(pos,i)<= mind:
                mind = distance(pos,i)
                pos2 = i
        env.dir[flag] = goTo(pos,pos2)
    return s[env.dir[flag]]+'sj'
    
def getool(env):
    pass
def attackDenfence(env):
    pass
class Model(object):
    def __init__(self):
        self.state = [0,0]#状态机初始化
        self.env = Env()
        self.condition = threading.Condition()
    def input(self,env: Env):
        self.env = env
    def output(self):
        output = ''
        for flag, state in enumerate(self.state):
            if state == 0:
                output += cruise(self.env,flag)#巡航
            if state == 1:
                output += getool(self.env,flag)#得道具
            if state == 2:
                output += attackDenfence(self.env,flag)
        save(self.env, output)
        return output

if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    model = Model()
    for result in getresp(1670902625355):
        print(result)