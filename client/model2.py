from utils import *
from env import Env
import threading
from saveload import *
from ui import *
import subprocess
import time

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
    return s[env.dir[flag]]
def findTool(env):
    tool_list = []
    for block in env.map.blocks:
        if len(block.objs) > 0:
            for obj in block.objs:
                if obj.type == ObjType.Item:
                    tool_list.append(block)
    return tool_list
def toolPick(env,tool_list):
    blood = []
    speed = []
    goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
    state = [0,0]
    for t in tool_list:
        if t.objs[0].type==2:#如果是buff
            if t.objs[0].status.buffType == BuffType.BuffHp:
                blood.append(t)
            else:
                speed.append(t)
    for c in env.us:
        tool = None
        if c.moveCD != 1:
            mds = 100
            for sp in speed:
                if mds > distance((c.x,c.y),(sp.x,sp.y)):
                    mds = distance((c.x,c.y),(sp.x,sp.y)) 
                    tool = sp        
        if c.hp != 100:#血量优先级大于speed
            mdb = 100
            for b in blood:
                if mdb > distance((c.x,c.y),(b.x,b.y)):
                    mdb = distance((c.x,c.y),(b.x,b.y)) 
                    tool = b  
        if tool:
            post = (tool.x,tool.y)
            goto[c.characterID] = [(c.x,c.y),post]
            state[c.characterID] = 1
    return state,goto

  
def getool(env,goto,flag):
    a = goTo(goto[flag][0],goto[flag][1])
    if a != None:
        return s[a]
    else:
        with open('debug.txt','a') as f:
            print(goto[flag],file=f)
def attackDenfence(env,goto,flag):
    a = goTo(goto[flag][0],goto[flag][1])
    return s[a]

class Model(object):
    def __init__(self):
        self.state = [0,0]#状态机初始化
        self.goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
        self.result = []
        self.env = Env()
        self.actionResp = None
        self.condition = threading.Condition()
        self.frame: int = -1
        with open('output.txt','w') as f:
            pass
        
    def input(self,env: Env):
        a = time.time()
        self.env = env
        tool_list = findTool(env)
        self.state,self.goto = toolPick(env,tool_list)
        if len(env.enemy):
            for enemy in env.enemy:
                if enemy.isAlive == True:
                    for us in env.us:
                        if 0<distance((enemy.x,enemy.y),(us.x,us.y))<=6:
                            self.state[us.characterID] = 2
                            self.goto[us.characterID] = [(us.x,us.y),(enemy.x,enemy.y)]       
        if env.frame > self.frame:
            self.frame = env.frame
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()

    def output(self,characterID):
        a = time.time()
        if characterID==0:
            output = ['','']
            for flag, state in enumerate(self.state):
                if state == 0:
                    output[flag] = cruise(self.env,flag)#巡航
                if state == 1:
                    output[flag] = getool(self.env,self.goto,flag)#得道具
                if state == 2:
                    output[flag] = attackDenfence(self.env,self.goto,flag)

                if self.env.us[flag].moveCDLeft == 0:
                    output[flag] += 's'
                else:
                    output[flag] = s[(s2i[output[flag]] + self.env.us[flag].moveCDLeft)%6]
                if state == 2 and self.env.us[flag].slaveWeapon.attackCDLeft == 0:#使用副武器
                    output[flag] += 'k'
                else:
                    if self.env.us[flag].masterWeapon.attackCDLeft == 0:#使用主武器
                        output[flag] += 'j'

                if self.env.us[flag].isAlive == False:#死亡不输入
                    output[flag] = ''
            self.result = output
            if self.actionResp:
                save(self.actionResp, self.result)
                with open('output.txt','a') as f:
                    print('frame:{}'.format(self.actionResp.frame),'action{}'.format(self.result),'state:{}'.format(self.state),file=f)
                    print('output_cost:{}'.format(time.time()-a),'state:{}'.format(self.state))
            return self.result[characterID]
        else:
            return self.result[characterID]
# def getenv():
#     findSequence = str(1670917645822) + "\n"
#     findFlag = False
#     with open(saveloadPath, 'r') as file:
#         #findSequence = file.readline()
#         for lineStr in file.readlines()[-600:]:
#             if findFlag:
#                 if len(lineStr) == len(findSequence):
#                     break
#                 jsonObj: dict = json.loads(lineStr)
#                 saveInfo: SaveInfo = SaveInfo(Env().from_json(json.dumps(jsonObj['env'])), jsonObj['actions'])
#                 yield saveInfo
#             if lineStr == findSequence:
#                 findFlag = True
if __name__ == '__main__':
    '''加载特定一次训练的信息'''
    packet =  PacketResp()
    model = Model()
    ui = UI()
    characterID = 0
    '1670917645822'
    for saveInfo in getresp():
        actionResp = saveInfo.actionResp
        packet.data = actionResp
        model.env = model.env.readEnv(actionResp)
        #refreshUI(ui,packet)
        model.input(model.env)
        st = model.output(characterID)
        print('frame = {}'.format(actionResp.frame))