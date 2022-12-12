from utils import *
from env import Env
def cruise(Env):
    pass
def getool(Env):
    pass
def attackDenfence(Env):
    pass
class Model(object):
    def __init__(self):
        self.state1 = 0#状态机初始化
        self.state2 = 0
        self.env:Env
    def input(self):
        pass
    def output(self):
        if self.state == 0:
            output1 = cruise(self.env)#巡航
        if self.state == 1:
            output = getool()#得道具
        if self.state == 2:
            output = attackDenfence()