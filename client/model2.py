from utils import *
from env import Env
import threading
from saveload import *
from ui import *
import subprocess
import time
import copy
def fill_block(env,flag):
    not_my_land=[]
    pos = (env.us[flag].x,env.us[flag].y)
    minpos = (24,24)
    for block in env.map.blocks:
        if block.valid == True:
            if not (block.color == env.us[0].color and env.frame == block.frame):
                not_my_land.append((block.x,block.y))
    for i in not_my_land:
        if 0<distance(pos,i)<=distance(pos,minpos):
            minpos = i
    
    a = goTo(pos , minpos)
    if env.us[flag].masterWeapon.weaponType == 1:
        mudi = mweapon1(pos,a)
    else:
        mudi = mweapon2(pos,a)
    if (env.us[flag].masterWeapon.attackCDLeft == 0) and (minpos in mudi):
        return s[a]+'j'
    if (env.us[flag].moveCDLeft == 0) and distance(pos,minpos) != 1:
        return s[a]+'s'

    return s[a]

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
    output = s[env.dir[flag]]

    if env.us[flag].moveCDLeft == 0:
        output += 's'
    if env.us[flag].masterWeapon.attackCDLeft == 0:#使用主武器
        output += 'j'


    if env.us[flag].moveCD <= 2:
        output = fill_block(env,flag)

    return output
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
                    if mds > 8:
                        tool = None
                    else:
                        tool = sp      
        if c.hp != 100:#血量优先级大于speed
            mdb = 100
            for b in blood:
                if mdb > distance((c.x,c.y),(b.x,b.y)):
                    mdb = distance((c.x,c.y),(b.x,b.y)) 
                    if mdb > 8:
                        tool = None
                    else:
                        tool = b  
        if tool:
            post = (tool.x,tool.y)
            goto[c.characterID] = [(c.x,c.y),post]
            state[c.characterID] = 1
    return state,goto

  
def getool(env,goto,flag):
    a = goTo(goto[flag][0],goto[flag][1])
    if env.us[flag].masterWeapon.attackCDLeft == 0:
        return s[a] + 'j'
    if env.us[flag].moveCDLeft == 0:
        return s[a] + 's'
    return s[a]

def keep_distance(env,goto,flag,dis):
    a = goTo(goto[flag][0],goto[flag][1])    
    if distance(goto[flag][0],goto[flag][1]) == dis:
        for enemy in env.enemy:
            if (enemy.x,enemy.y) == goto[flag][1] and enemy.isGod == True:
                return s[a]
        if env.us[flag].moveCDLeft == 0 and env.us[flag].masterWeapon.attackCDLeft == 0 :
            return s[a]+'s'+'j'
        else:
            return s[a]
    elif distance(goto[flag][0],goto[flag][1]) < dis:
        if env.us[flag].moveCDLeft == 0:
            if env.us[flag].slaveWeapon.attackCDLeft == 0:#使用副武器
                return 'k' + s[(a-3)%6]+'s'
            return s[(a-3)%6]+'s'
        if env.us[flag].masterWeapon.attackCDLeft == 0:
            return s[a]+'j'
        return s[a]
    else:
        if env.us[flag].moveCDLeft == 0:
            return s[a]+'s'
        return s[a]
def run_away(env,goto,flag,dis):
    a = goTo(goto[flag][0],goto[flag][1]) 
    if distance(goto[flag][0],goto[flag][1]) <= dis:
        return s[(a-3)%6]+'s'
    return ''
    
class Model(object):
    def __init__(self):
        self.state = [0,0]#状态机初始化
        self.goto = [[(0,0),(0,0)],[(0,0),(0,0)]]
        self.result = []
        self.env = Env()
        self.actionResp = None
        self.condition = threading.Condition()
        self.frame: int = -1
        with open('log_output.txt','w') as f:
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
                        if 0<distance((enemy.x,enemy.y),(us.x,us.y))<=10:
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
                    output[flag] = keep_distance(self.env,self.goto,flag,4)
                        #output[flag] += run_away(self.env,self.goto,flag,8)

                if 's' not in output[flag] and 'j' not in output[flag] and 'k' not in output[flag]:#没有行动时进行张望
                    output[flag] = s[(s2i[output[flag]] - self.env.us[flag].moveCDLeft)%6]
                if self.env.us[flag].isAlive == False:#死亡不输入
                    output[flag] = ''
            self.result = output
            if self.actionResp:
                save(self.actionResp, self.result)
                with open('log_output.txt','a') as f:
                    print('frame:{}'.format(self.actionResp.frame),'action{}'.format(self.result),'state:{}'.format(self.state),file=f)
                    print('bengle :(')
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
        refreshUI(ui,packet)
        model.input(model.env)
        st = model.output(characterID)
        print('frame = {}'.format(actionResp.frame),'action:{}'.format(st))